#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages, Extension
import os
import pkg_resources
import sys
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
    from setuptools.command.build_ext import build_ext
else:
    with_cython = True
    print('Development mode: Compiling Cython modules from .pyx sources.')
    from Cython.Distutils.build_ext import new_build_ext as build_ext


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

extra_compile_args = [
    '-std=c++0x',
    # extra flags needed on macOS for C++11
] + (["-stdlib=libc++", "-mmacosx-version-min=10.7"]
     if platform.system() == "Darwin" else [])

libraries = [
    (
        'skia', {
            'sources': skia_src,
            'include_dirs': include_dirs,
            'cflags': extra_compile_args,
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
    ext_modules=extensions,
    cmdclass={
        'build_ext': build_ext,
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
    libraries=libraries,
)

if __name__ == "__main__":
    setup(**setup_params)
