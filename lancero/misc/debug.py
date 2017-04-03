from __future__ import print_function

import sys
import traceback

# From: http://notimetolouse.blogspot.com.br/2009/10/simple-debugging-of-ajax-in-django.html
def console_debug(f):
    def x(*args, **kw):
        try:
            ret = f(*args, **kw)
        except Exception as e:
            print("ERROR:", str(e), file=sys.stderr)
            exc_type, exc_value, tb = sys.exc_info()
            message = "Type: %s\nValue: %s\nTraceback:\n\n%s" % (exc_type, exc_value, "\n".join(traceback.format_tb(tb)))
            print(message, file=sys.stderr)
            raise
        else:
            return ret
    return x
