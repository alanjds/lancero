#!/usr/bin/env python
#coding: utf-8

# Orignal version taken from http://www.djangosnippets.org/snippets/186/
# Original author: udfalkso
# Modified by: Shwagroo Team
# And then merged with http://www.djangosnippets.org/snippets/727/
# by: alanjds

import sys
import os
import tempfile
import cProfile
import django.db.models as models
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
try:
    import cStringIO as StringIO
except:
    import StringIO

try:
    import hotshot, hotshot.stats
except ImportError:
    pass

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    pass

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.name = 'lancero.middleware'

import re
words_re = re.compile( r'\s+' )

group_prefix_re = [
    re.compile( "^.*/django/[^/]+" ),
    re.compile( "^(.*)/[^/]+$" ), # extract module path
    re.compile( ".*" ),           # catch strange entries
]

SHOW_PROFILE_MAGIC_KEY='__profiler'

class HotshotProfilerMiddleware(object):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.

    WARNING: It uses hotshot profiler which is not thread safe.
    """
    def process_request(self, request):
        if (settings.DEBUG or (hasattr(request, 'user') and request.user.is_superuser)) and SHOW_PROFILE_MAGIC_KEY in request.GET:
            self.tmpfile = tempfile.mktemp()
            self.prof = hotshot.Profile(self.tmpfile)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (settings.DEBUG or (hasattr(request, 'user') and request.user.is_superuser)) and SHOW_PROFILE_MAGIC_KEY in request.GET:
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def get_group(self, file):
        for g in group_prefix_re:
            name = g.findall( file )
            if name:
                return name[0]

    def get_summary(self, results_dict, sum):
        list = [ (item[1], item[0]) for item in results_dict.items() ]
        list.sort( reverse = True )
        list = list[:40]

        res = "      tottime\n"
        for item in list:
            res += "%4.1f%% %7.3f %s\n" % ( 100*item[0]/sum if sum else 0, item[0], item[1] )

        return res

    def summary_for_files(self, stats_str):
        stats_str = stats_str.split("\n")[5:]

        mystats = {}
        mygroups = {}

        sum = 0

        for s in stats_str:
            fields = words_re.split(s);
            if len(fields) == 7:
                time = float(fields[2])
                sum += time
                file = fields[6].split(":")[0]

                if not file in mystats:
                    mystats[file] = 0
                mystats[file] += time

                group = self.get_group(file)
                if not group in mygroups:
                    mygroups[ group ] = 0
                mygroups[ group ] += time

        return "<pre>" + \
               " ---- By file ----\n\n" + self.get_summary(mystats,sum) + "\n" + \
               " ---- By group ---\n\n" + self.get_summary(mygroups,sum) + \
               "</pre>"

    def process_response(self, request, response):
        if (settings.DEBUG or (hasattr(request, 'user') and request.user.is_superuser)) and SHOW_PROFILE_MAGIC_KEY in request.GET:
            self.prof.close()

            out = StringIO.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile)
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()

            if response and response.content and stats_str:
                response.content = "<html><pre>" + stats_str + "</pre></html>"

            response.content = "\n".join(response.content.split("\n")[:40])

            response.content += self.summary_for_files(stats_str)

            os.unlink(self.tmpfile)

            response['Content-Type'] = 'text/html'

        return response


class CProfileProfilerMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and SHOW_PROFILE_MAGIC_KEY in request.GET:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and SHOW_PROFILE_MAGIC_KEY in request.GET:
            self.profiler.create_stats()
            out = StringIO.StringIO()
            old_stdout, sys.stdout = sys.stdout, out
            self.profiler.print_stats(1)
            sys.stdout = old_stdout
            response.content = '<html><pre>%s</pre></html>' % out.getvalue()
            response['Content-Type'] = 'text/html'
        return response


# From: django-middleware-extras
# adapted by: alanjds
class PrettifyHTMLMiddleware(object):
    """Middleware that prettifies HTML.

    Add it last to the list of MIDDLEWARE_CLASSES:

    MIDDLEWARE_CLASSES = (
        ...
        'lancero.middleware.PrettifyHTMLMiddleware'
    )
    """
    def __init__(self):
        try:
            from BeautifulSoup import BeautifulSoup
        except ImportError, e:
            raise MiddlewareNotUsed('Not prettifying HTML: BeautifulSoup cannot be imported')

    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            soup = BeautifulSoup(response.content)
            try:
                response.content = soup.prettify(spacesPerLevel=4)
            except TypeError, e:    # not alanjds' flavor of Soup
                # so, use official Soup flavor...
                response.content = soup.prettify()

        return response


# From: http://djangosnippets.org/snippets/420/
class ConsoleTracebackMiddleware:
    def process_exception(self, request, exception):
        import traceback
        import sys
        exc_info = sys.exc_info()
        print "######################## Exception #############################"
        print '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
        print "################################################################"
        #print repr(request)
        #print "################################################################"
