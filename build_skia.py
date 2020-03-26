#!/usr/bin/env python2
import sys

py_ver = sys.version_info[:2]
if py_ver > (2, 7):
    sys.exit("python 2.7 is required; this is {}.{}".format(*py_ver))

import argparse
import glob
import os
import shutil
import subprocess


# script to bootstrap virtualenv without requiring pip
GET_VIRTUALENV_URL = "https://asottile.github.io/get-virtualenv.py"

EXE_EXT = ".exe" if sys.platform == "win32" else ""

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

SKIA_SRC_DIR = os.path.join(ROOT_DIR, "src", "cpp", "skia")
SKIA_BUILD_ARGS = [
    "is_official_build=true",
    "is_debug=false",
    "skia_enable_pdf=false",
    "skia_enable_discrete_gpu=false",
    "skia_enable_nvpr=false",
    "skia_enable_skottie=false",
    "skia_enable_skshaper=false",
    "skia_use_dng_sdk=false",
    "skia_use_expat=false",
    "skia_use_freetype=false",
    "skia_use_fontconfig=false",
    "skia_use_fonthost_mac=false",
    "skia_use_harfbuzz=false",
    "skia_use_icu=false",
    "skia_use_libgifcodec=false",
    "skia_use_libjpeg_turbo=false",
    "skia_use_libpng=false",
    "skia_use_libwebp=false",
    "skia_use_piex=false",
    "skia_use_sfntly=false",
    "skia_use_xps=false",
    "skia_use_zlib=false",
]
if sys.platform != "win32":
    # On Linux, I need this flag otherwise I get undefined symbol upon importing;
    # on Windows, defining this flag creates other linker issues (SkFontMgr being
    # redefined by SkFontMgr_win_dw_factory.obj)...
    SKIA_BUILD_ARGS.append("skia_enable_fontmgr_empty=true")
    # We don't need GPU or GL support, but disabling this on Windows creates lots
    # of undefined symbols upon linking the skia.dll, so I keep them for Windows...
    SKIA_BUILD_ARGS.append("skia_enable_gpu=false")
    SKIA_BUILD_ARGS.append("skia_use_gl=false")
    SKIA_BUILD_ARGS.append("skia_enable_ccpr=false")


def make_virtualenv(venv_dir):
    from contextlib import closing
    import io
    from urllib2 import urlopen

    bin_dir = "Scripts" if sys.platform == "win32" else "bin"
    venv_bin_dir = os.path.join(venv_dir, bin_dir)
    python_exe = os.path.join(venv_bin_dir, "python" + EXE_EXT)

    # bootstrap virtualenv if not already present
    if not os.path.exists(python_exe):
        tmp = io.BytesIO()
        with closing(urlopen(GET_VIRTUALENV_URL)) as response:
            tmp.write(response.read())

        p = subprocess.Popen(
            [sys.executable, "-", "--no-download", venv_dir], stdin=subprocess.PIPE
        )
        p.communicate(tmp.getvalue())
        if p.returncode != 0:
            sys.exit("failed to create virtualenv")
    assert os.path.exists(python_exe)

    # pip install ninja
    ninja_exe = os.path.join(venv_bin_dir, "ninja" + EXE_EXT)
    if not os.path.exists(ninja_exe):
        subprocess.check_call(
            [
                os.path.join(venv_bin_dir, "pip" + EXE_EXT),
                "install",
                "--only-binary=ninja",
                "ninja",
            ]
        )

    # place virtualenv bin in front of $PATH, like 'source venv/bin/activate'
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join([venv_bin_dir, env.get("PATH", "")])

    return env


# as supported by shutil.make_archive
ARCHIVE_FORMATS = {
    ".zip": "zip",
    ".tar": "tar",
    ".tar.gz": "gztar",
    ".tar.bz2": "bztar",
}


def _split_archive_base_and_format(parser, fname):
    for ext in ARCHIVE_FORMATS:
        if fname.endswith(ext):
            fmt = ARCHIVE_FORMATS[ext]
            break
    else:
        parser.error(
            "Invalid archive file extension {fname!r}. "
            "Choose from {formats}".format(fname=fname, formats=list(ARCHIVE_FORMATS))
        )
    return fname.split(ext)[0], fmt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "build_dir",
        default=os.path.join("build", "skia"),
        nargs="?",
        help="directory where to build libskia (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--shared-lib",
        action="store_true",
        help="build a shared library (default: static)"
    )
    parser.add_argument(
        "--target-cpu",
        default=None,
        help="The desired CPU architecture for the build (default: host)",
        choices=["x86", "x64", "arm", "arm64", "mipsel"]
    )
    parser.add_argument("-a", "--archive-file", default=None)
    args = parser.parse_args()

    if args.archive_file is not None:
        archive_base, archive_fmt = _split_archive_base_and_format(
            parser, args.archive_file
        )

    build_dir = os.path.abspath(args.build_dir)
    venv_dir = os.path.join(build_dir, "venv2")

    env = make_virtualenv(venv_dir)

    subprocess.check_call(
        ["python", os.path.join("tools", "git-sync-deps")], env=env, cwd=SKIA_SRC_DIR
    )

    build_args = list(SKIA_BUILD_ARGS)
    if args.shared_lib:
        build_args.append("is_component_build=true")
    if args.target_cpu:
        build_args.append('target_cpu="{}"'.format(args.target_cpu))

    subprocess.check_call(
        [
            os.path.join(SKIA_SRC_DIR, "bin", "gn" + EXE_EXT),
            "gen",
            build_dir,
            "--args={}".format(" ".join(build_args)),
        ],
        env=env,
        cwd=SKIA_SRC_DIR,
    )

    subprocess.check_call(["ninja", "-C", build_dir], env=env)

    # when building skia.dll on windows with gn and ninja, the DLL import file
    # is written as 'skia.dll.lib'; however, when linking it with the extension
    # module, setuptools expects it to be named 'skia.lib'.
    if sys.platform == "win32" and args.shared_lib:
        for f in glob.glob(os.path.join(build_dir, "skia.dll.*")):
            os.rename(f, f.replace(".dll", ""))

    if args.archive_file is not None:
        # we pack the whole build_dir except for the venv2/ subdir
        shutil.rmtree(venv_dir)
        shutil.make_archive(archive_base, archive_fmt, build_dir)
