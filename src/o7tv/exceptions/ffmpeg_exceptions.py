class O7tvError(Exception):
    pass


class FfmpegError(O7tvError):
    pass


class FfmpegInvalidInputError(FfmpegError):
    pass


class FfmpegUnsupportedFormatError(FfmpegError):
    pass


class FfmpegConversionError(FfmpegError):
    pass


class FfmpegStreamError(FfmpegError):
    pass
