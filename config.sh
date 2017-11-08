# Define custom utilities
# Test for OSX with [ -n "$IS_OSX" ]

function pre_build {
    # Any stuff that you need to do before you start building the wheels
    # Runs in the root directory of this repository.
    :
}

function run_tests {
    # The function is called from an empty temporary directory.
    # Get absolute path to the pre-compiled wheel
    wheelhouse=$(abspath ../wheelhouse)
    wheel=`ls ${wheelhouse}/skia*.whl | head -n 1`

    # select tox environment
    if [ -n "$IS_OSX" ]; then
        PYTHON_VERSION=$MB_PYTHON_VERSION
    fi
    case "${PYTHON_VERSION}" in
        2.7)
           TOXENV=py27
           ;;
        3.5)
           TOXENV=py35
           ;;
        3.6)
           TOXENV=py36
           ;;
    esac

    # Runs tests on installed wheel
    tox --installpkg $wheel -e $TOXENV
}
