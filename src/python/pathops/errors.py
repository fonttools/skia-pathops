class PathOpsError(Exception):
    pass


class UnsupportedVerbError(PathOpsError):
    pass


class OpenPathError(PathOpsError):
    pass
