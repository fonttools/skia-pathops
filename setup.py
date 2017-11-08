#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.command.build_clib import build_clib
from distutils.errors import DistutilsSetupError
from distutils import log
from distutils.dep_util import newer_group, newer_pairwise
import pkg_resources
import sys
import os
import platform


needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []
needs_wheel = {'bdist_wheel'}.intersection(sys.argv)
wheel = ['wheel'] if needs_wheel else []


# use Cython if available, else try use pre-generated .cpp sources
cython_min_version = '0.27.3'
try:
    pkg_resources.require("cython >= %s" % cython_min_version)
except pkg_resources.ResolutionError:
    with_cython = False
    print('Distribution mode: Compiling from Cython-generated .cpp sources.')
else:
    with_cython = True
    print('Development mode: Compiling Cython modules from .pyx sources.')


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
            self.distribution.ext_modules[:] = cythonize(
                self.distribution.ext_modules,
                force=self.force,
                quiet=not self.verbose,
                compiler_directives={
                    "linetrace": linetrace,
                    "language_level": 3,
                })

        build_ext.finalize_options(self)

        if self.compiler is None:
            # we use this variable with tox to build using GCC on Windows.
            # https://bitbucket.org/hpk42/tox/issues/274/specify-compiler
            self.compiler = os.environ.get("DISTUTILS_COMPILER", None)
        if self.compiler == "mingw32":
            # workaround for virtualenv changing order of libary_dirs on
            # Windows, which makes gcc fail to link with the correct libpython
            # https://github.com/mingwpy/mingwpy.github.io/issues/31
            self.library_dirs.insert(0, os.path.join(sys.exec_prefix, 'libs'))

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


class custom_build_clib(build_clib):
    """ Custom build_clib command which allows to pass compiler-specific
    'macros' and 'cflags' when compiling C libraries.

    In the setup 'libraries' option, the 'macros' and 'cflags' can be
    provided as dict with the compiler type as the key (e.g. "unix",
    "mingw32", "msvc") and the value containing the list of macros/cflags.
    A special empty string '' key may be used for default options that
    apply to all the other compiler types except for those explicitly
    listed.
    """

    def finalize_options(self):
        build_clib.finalize_options(self)
        if self.compiler is None:
            # we use this variable with tox to build using GCC on Windows.
            # https://bitbucket.org/hpk42/tox/issues/274/specify-compiler
            self.compiler = os.environ.get("DISTUTILS_COMPILER", None)

    def build_libraries(self, libraries):
        for (lib_name, build_info) in libraries:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'sources' must be present and must be "
                    "a list of source filenames" % lib_name)
            sources = list(sources)

            # detect target language
            language = self.compiler.detect_language(sources)

            # do compiler specific customizations
            compiler_type = self.compiler.compiler_type

            # strip compile flags that are not valid for C++ to avoid warnings
            if compiler_type == "unix" and language == "c++":
                if "-Wstrict-prototypes" in self.compiler.compiler_so:
                    self.compiler.compiler_so.remove("-Wstrict-prototypes")

            # get compiler-specific preprocessor definitions
            macros = build_info.get("macros", [])
            if isinstance(macros, dict):
                if compiler_type in macros:
                    macros = macros[compiler_type]
                else:
                    macros = macros.get("", [])

            include_dirs = build_info.get('include_dirs')

            # get compiler-specific compile flags
            cflags = build_info.get("cflags", [])
            if isinstance(cflags, dict):
                if compiler_type in cflags:
                    cflags = cflags[compiler_type]
                else:
                    cflags = cflags.get("", [])

            expected_objects = self.compiler.object_filenames(
                sources,
                output_dir=self.build_temp)

            # TODO: also support objects' dependencies
            if (self.force or
                    newer_pairwise(sources, expected_objects) != ([], [])):
                log.info("building '%s' library", lib_name)
                # compile the source code to object files
                objects = self.compiler.compile(sources,
                                                output_dir=self.build_temp,
                                                macros=macros,
                                                include_dirs=include_dirs,
                                                extra_postargs=cflags,
                                                debug=self.debug)
            else:
                log.debug(
                    "skipping build '%s' objects (up-to-date)" % lib_name)
                objects = expected_objects

            # Now "link" the object files together into a static library.
            # (On Unix at least, this isn't really linking -- it just
            # builds an archive.  Whatever.)
            self.compiler.create_static_lib(objects, lib_name,
                                            output_dir=self.build_clib,
                                            debug=self.debug)


ext = '.pyx' if with_cython else '.cpp'
pkg_dir = os.path.join("src", "python")
skia_dir = os.path.join("src", "cpp", "skia")

skia_src = [
    os.path.join(skia_dir, "src", "core", "SkArenaAlloc.cpp"),
    os.path.join(skia_dir, "src", "core", "SkBuffer.cpp"),
    os.path.join(skia_dir, "src", "core", "SkCubicClipper.cpp"),
    os.path.join(skia_dir, "src", "core", "SkData.cpp"),
    os.path.join(skia_dir, "src", "core", "SkGeometry.cpp"),
    os.path.join(skia_dir, "src", "core", "SkMath.cpp"),
    os.path.join(skia_dir, "src", "core", "SkMatrix.cpp"),
    os.path.join(skia_dir, "src", "core", "SkPath.cpp"),
    os.path.join(skia_dir, "src", "core", "SkPathRef.cpp"),
    os.path.join(skia_dir, "src", "core", "SkPoint.cpp"),
    os.path.join(skia_dir, "src", "core", "SkRect.cpp"),
    os.path.join(skia_dir, "src", "core", "SkRRect.cpp"),
    os.path.join(skia_dir, "src", "core", "SkSemaphore.cpp"),
    os.path.join(skia_dir, "src", "core", "SkString.cpp"),
    os.path.join(skia_dir, "src", "core", "SkStringUtils.cpp"),
    os.path.join(skia_dir, "src", "core", "SkUtils.cpp"),
    os.path.join(skia_dir, "src", "core", "SkThreadID.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkAddIntersections.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkDConicLineIntersection.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkDCubicLineIntersection.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkDCubicToQuads.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkDLineIntersection.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkDQuadLineIntersection.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkIntersections.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpAngle.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpBuilder.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpCoincidence.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpContour.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpCubicHull.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpEdgeBuilder.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpSegment.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkOpSpan.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsCommon.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsConic.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsCubic.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsCurve.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsDebug.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsLine.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsOp.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsPoint.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsQuad.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsRect.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsSimplify.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsTightBounds.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsTSect.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsTypes.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathOpsWinding.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkPathWriter.cpp"),
    os.path.join(skia_dir, "src", "pathops", "SkReduceOrder.cpp"),
    os.path.join(skia_dir, "src", "ports", "SkDebug_stdio.cpp"),
    os.path.join(skia_dir, "src", "ports", "SkMemory_malloc.cpp"),
    os.path.join(skia_dir, "src", "ports", "SkOSFile_stdio.cpp"),
]

if os.name == "nt":
    skia_src += [
        os.path.join(skia_dir, "src", "ports", "SkDebug_win.cpp"),
        os.path.join(skia_dir, "src", "ports", "SkOSFile_win.cpp"),
    ]
elif os.name == "posix":
    skia_src += [
        os.path.join(skia_dir, "src", "ports", "SkOSFile_posix.cpp"),
    ]
else:
    raise RuntimeError("unsupported OS: %r" % os.name)

include_dirs = [
    os.path.join(skia_dir, 'include', 'config'),
    os.path.join(skia_dir, 'include', 'core'),
    os.path.join(skia_dir, 'include', 'pathops'),
    os.path.join(skia_dir, 'include', 'private'),
    os.path.join(skia_dir, 'src', 'core'),
    os.path.join(skia_dir, 'src', 'opts'),
    os.path.join(skia_dir, 'src', 'shaders'),
]

extra_compile_args = {
    '': [
        '-std=c++0x',
    ] + ([
        # extra flags needed on macOS for C++11
        "-stdlib=libc++",
        "-mmacosx-version-min=10.7",
    ] if platform.system() == "Darwin" else []),
    "msvc": [
        "/EHsc",
        "/Zi",
    ],
}

define_macros = {
    # On Windows Python 2.7, pyconfig.h defines "hypot" as "_hypot",
    # This clashes with GCC's cmath, and causes compilation errors when
    # building under MinGW: http://bugs.python.org/issue11566
    "mingw32": [("_hypot", "hypot")],
}

libraries = [
    (
        'skia', {
            'sources': skia_src,
            'include_dirs': include_dirs,
            'cflags': extra_compile_args,
            'macros': define_macros,
        },
    ),
]

extensions = [
    Extension(
        "skia.core",
        sources=[
            os.path.join(pkg_dir, 'skia', 'core' + ext),
        ],
        depends=[
            os.path.join(skia_dir, 'include', 'core', 'SkPath.h'),
        ],
        define_macros=define_macros,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        language="c++",
    ),
    Extension(
        "skia.pathops",
        sources=[
            os.path.join(pkg_dir, 'skia', 'pathops' + ext),
        ],
        depends=[
            os.path.join(skia_dir, 'include', 'pathops', 'SkPathOps.h'),
        ],
        define_macros=define_macros,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        language="c++",
    ),
]

# with open('README.rst', 'r') as f:
#     long_description = f.read()

setup_params = dict(
    name="skia-pathops",
    version="0.1.0.dev0",
    description="Boolean operations on paths using the Skia library",
    # long_description=long_description,
    author="Khaled Hosny, Cosimo Lupo",
    license="BSD-3-Clause",
    package_dir={"": pkg_dir},
    packages=find_packages(pkg_dir),
    libraries=libraries,
    ext_modules=extensions,
    cmdclass={
        'build_ext': custom_build_ext,
        'build_clib': custom_build_clib,
    },
    setup_requires=pytest_runner + wheel,
    tests_require=[
        'pytest>=2.8',
    ],
    install_requires=[
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
)

if __name__ == "__main__":
    setup(**setup_params)
