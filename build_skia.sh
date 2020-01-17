#!/bin/bash
# Run this script as `source ./build_skia.sh`.
# This way the LD_LIBRARY_PATH environment variable is imported in the current shell.
# NOTE: This was only tested on macOS. It requires python2 to be on the $PATH and
# it must be run *outside* of a python3 venv otherwise gn tool will complain...

pushd src/cpp/skia

python2 tools/git-sync-deps

bin/gn gen out/Shared --args='is_official_build=true is_component_build=true is_debug=false skia_enable_pdf=false skia_enable_ccpr=false skia_enable_gpu=false skia_enable_discrete_gpu=false skia_enable_nvpr=false skia_enable_skottie=false skia_enable_skshaper=false skia_use_dng_sdk=false skia_use_expat=false skia_use_gl=false skia_use_harfbuzz=false skia_use_icu=false skia_use_libgifcodec=false skia_use_libjpeg_turbo=false skia_use_libwebp=false skia_use_piex=false skia_use_sfntly=false skia_use_xps=false skia_use_zlib=false skia_use_libpng=false'

ninja -C out/Shared

export LD_LIBRARY_PATH=$(pwd)/out/Shared

popd
