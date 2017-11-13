|Travis CI Status| |Appveyor CI Status|

Python bindings for the `Google Skia <https://skia.org>`__ library's
`Path Ops <https://skia.org/dev/present/pathops>`__ module, performing
boolean operations on paths (intersection, union, difference, xor).

Build
=====

A recent version of `Cython <https://github.com/cython/cython>`__ is
required to build the package (see the `build-requirements.txt` file for
the minimum required version).

For developers we recommend installing in editable mode using
`pip install -e .`, and compiling the extension module in the
same source directory.

```sh
$ pip install -r build-requirements.txt
$ python setup.py build_ext --inplace
$ pip install -e .
```

.. |Travis CI Status| image:: https://travis-ci.org/fonttools/skia-pathops.svg?branch=master
   :target: https://travis-ci.org/fonttools/skia-pathops
.. |Appveyor CI Status| image:: https://ci.appveyor.com/api/projects/status/jv7g1e0m0vyopbej?svg=true
   :target: https://ci.appveyor.com/project/fonttools/skia-pathops/branch/master
