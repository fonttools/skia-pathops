#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.errors import DistutilsSetupError
from distutils import log
from distutils.dep_util import newer_group
from distutils.dir_util import mkpath
from distutils.file_util import copy_file
import pkg_resources
import subprocess
import sys
import os
import platform
from io import open
import re


# Building libskia with its 'gn' build tool requires python2; if 'python2'
# executable is not in your $PATH, you can export PYTHON2_EXE=... before
# running setup.py script.
PYTHON2_EXE = os.environ.get("PYTHON2_EXE", "python2")

# check if minimum required Cython is available
cython_version_re = re.compile('\s*"cython\s*>=\s*([0-9][0-9\w\.]*)\s*"')
with open("pyproject.toml", "r", encoding="utf-8") as fp:
    for line in fp:
        m = cython_version_re.match(line)
        if m:
            cython_min_version = m.group(1)
            break
    else:
        sys.exit("error: could not parse cython version from pyproject.toml")
try:
    pkg_resources.require("cython >= %s" % cython_min_version)
except pkg_resources.ResolutionError:
    with_cython = False
else:
    with_cython = True

argv = sys.argv[1:]

# bail out early if we are compiling the cython extension module
if ({"build",
     "build_ext",
     "bdist_wheel",
     "install",
     "develop",
     "test"}.intersection(argv) and not with_cython):
    sys.exit(
        "error: the required Cython >= %s was not found" % cython_min_version
    )

needs_wheel = {'bdist_wheel'}.intersection(argv)
wheel = ['wheel'] if needs_wheel else []


class custom_build_ext(build_ext):
    """ Custom 'build_ext' command which allows to pass compiler-specific
    'extra_compile_args', 'extra_link_args', 'define_macros' and
    'undef_macros' options.

    The value of the Extension class keywords can be provided as a dict,
    with the the compiler type as the keys (e.g. "unix", "mingw32", "msvc"),
    and the values containing the compiler-specific list of options.
    A special empty string '' key may be used for default options that
    apply to all the other compiler types except for those explicitly
    listed.
    """

    def finalize_options(self):
        if with_cython:
            # compile *.pyx source files to *.cpp using cythonize
            from Cython.Build import cythonize

            # optionally enable line tracing for test coverage support
            linetrace = os.environ.get("CYTHON_TRACE") == "1"
            force = linetrace or self.force
            self.distribution.ext_modules[:] = cythonize(
                self.distribution.ext_modules,
                force=force,
                annotate=os.environ.get("CYTHON_ANNOTATE", False),
                quiet=not self.verbose,
                compiler_directives={
                    "linetrace": linetrace,
                    "language_level": 3,
                    "embedsignature": True,
                })

        build_ext.finalize_options(self)

    def build_extension(self, ext):
        sources = ext.sources
        if sources is None or not isinstance(sources, (list, tuple)):
            raise DistutilsSetupError(
                "in 'ext_modules' option (extension '%s'), "
                "'sources' must be present and must be "
                "a list of source filenames" % ext.name)
        sources = list(sources)

        ext_path = self.get_ext_fullpath(ext.name)
        depends = sources + ext.depends
        if not (self.force or newer_group(depends, ext_path, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            return
        else:
            log.info("building '%s' extension", ext.name)

        # Detect target language, if not provided
        language = ext.language or self.compiler.detect_language(sources)

        # do compiler specific customizations
        compiler_type = self.compiler.compiler_type

        # strip compile flags that are not valid for C++ to avoid warnings
        if compiler_type == "unix" and language == "c++":
            if "-Wstrict-prototypes" in self.compiler.compiler_so:
                self.compiler.compiler_so.remove("-Wstrict-prototypes")

        if isinstance(ext.extra_compile_args, dict):
            if compiler_type in ext.extra_compile_args:
                extra_compile_args = ext.extra_compile_args[compiler_type]
            else:
                extra_compile_args = ext.extra_compile_args.get("", [])
        else:
            extra_compile_args = ext.extra_compile_args or []

        if isinstance(ext.extra_link_args, dict):
            if compiler_type in ext.extra_link_args:
                extra_link_args = ext.extra_link_args[compiler_type]
            else:
                extra_link_args = ext.extra_link_args.get("", [])
        else:
            extra_link_args = ext.extra_link_args or []

        if isinstance(ext.define_macros, dict):
            if compiler_type in ext.define_macros:
                macros = ext.define_macros[compiler_type]
            else:
                macros = ext.define_macros.get("", [])
        else:
            macros = ext.define_macros or []

        if isinstance(ext.undef_macros, dict):
            for tp, undef in ext.undef_macros.items():
                if tp == compiler_type:
                    macros.append((undef,))
        else:
            for undef in ext.undef_macros:
                macros.append((undef,))

        if os.environ.get("CYTHON_TRACE") == "1":
            log.debug("adding -DCYTHON_TRACE to preprocessor macros")
            macros.append(("CYTHON_TRACE", 1))

        # compile the source code to object files.
        objects = self.compiler.compile(sources,
                                        output_dir=self.build_temp,
                                        macros=macros,
                                        include_dirs=ext.include_dirs,
                                        debug=self.debug,
                                        extra_postargs=extra_compile_args,
                                        depends=ext.depends)

        # Now link the object files together into a "shared object"
        if ext.extra_objects:
            objects.extend(ext.extra_objects)

        self.compiler.link_shared_object(
            objects, ext_path,
            libraries=self.get_libraries(ext),
            library_dirs=ext.library_dirs,
            runtime_library_dirs=ext.runtime_library_dirs,
            extra_postargs=extra_link_args,
            export_symbols=self.get_export_symbols(ext),
            debug=self.debug,
            build_temp=self.build_temp,
            target_lang=language)

    def run(self):
        # make sure skia library is built before the extension module, inside the
        # correct build_base dir (usually './build')
        build_dir = os.path.join(self.get_finalized_command("build").build_base, "skia")
        build_cmd = [PYTHON2_EXE, "build_skia.py", build_dir]
        # for Windows, we want to build a shared skia.dll. If we build a static lib
        # then gn/ninja pass the /MT flag (static runtime library) instead of /MD,
        # and produce linker errors when building the python extension module
        if sys.platform == "win32":
            build_cmd.append("--shared-lib")
        subprocess.run(build_cmd, check=True)

        # prepend the build dir to library_dirs so the linker can find our libskia
        for ext in self.extensions:
            ext.library_dirs.insert(0, build_dir)

        build_ext.run(self)

        # copy skia.dll next to the extension module
        if sys.platform == "win32":
            for ext in self.extensions:
                for lib_name in ext.libraries:
                    for lib_dir in ext.library_dirs:
                        dll_filename = lib_name + ".dll"
                        dll_fullpath = os.path.join(lib_dir, dll_filename)
                        if os.path.exists(dll_fullpath):
                            break
                    else:
                        log.debug(
                            "cannot find '{}' in: {}".format(
                                dll_filename, ", ".join(ext.library_dirs)
                            )
                        )
                        continue

                    ext_path = self.get_ext_fullpath(ext.name)
                    dest_dir = os.path.dirname(ext_path)
                    mkpath(dest_dir, verbose=self.verbose, dry_run=self.dry_run)
                    copy_file(
                        dll_fullpath,
                        os.path.join(dest_dir, dll_filename),
                        verbose=self.verbose,
                        dry_run=self.dry_run,
                    )


pkg_dir = os.path.join("src", "python")
cpp_dir = os.path.join("src", "cpp")
skia_dir = os.path.join(cpp_dir, "skia")

include_dirs = [os.path.join(skia_dir)]

extra_compile_args = {
    '': [
        '-std=c++14',
    ] + ([
        # extra flags needed on macOS for C++11
        "-stdlib=libc++",
        "-mmacosx-version-min=10.9",
    ] if platform.system() == "Darwin" else []),
    "msvc": [
        "/EHsc",
        "/Zi",
    ],
}

extensions = [
    Extension(
        "pathops._pathops",
        sources=[
            os.path.join(pkg_dir, 'pathops', '_pathops.pyx'),
        ],
        depends=[
            os.path.join(skia_dir, 'include', 'pathops', 'SkPathOps.h'),
        ],
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        libraries=["skia"],
        language="c++",
    ),
]

with open('README.md', 'r') as f:
    long_description = f.read()

version_file = os.path.join(pkg_dir, "pathops", "_version.py")

setup_params = dict(
    name="skia-pathops",
    use_scm_version={"write_to": version_file},
    description="Python access to operations on paths using the Skia library",
    url="https://github.com/fonttools/skia-pathops",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Khaled Hosny, Cosimo Lupo",
    author_email="fonttools@googlegroups.com",
    license="BSD-3-Clause",
    package_dir={"": pkg_dir},
    packages=find_packages(pkg_dir),
    ext_modules=extensions,
    cmdclass={
        'build_ext': custom_build_ext,
    },
    setup_requires=["setuptools_scm"] + wheel,
    install_requires=[
    ],
    extras_require={
        "testing": [
            "pytest",
            "coverage",
            "pytest-xdist",
            "pytest-randomly",
            "pytest-cython",
        ],
    },
    python_requires=">3.6",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
)

if __name__ == "__main__":
    setup(**setup_params)
