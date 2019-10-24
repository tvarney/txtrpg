
import traceback


def format_exception(e: Exception, with_stacktrace: bool=True) -> str:
    if with_stacktrace:
        return ''.join(traceback.format_exception(type(e), e, e.__traceback__))
    return "{}: {}".format(type(e).__name__, e)

