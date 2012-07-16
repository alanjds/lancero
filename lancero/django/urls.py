#coding: utf-8
from django.conf import settings
from django.http import HttpResponseRedirect

import base64
from django.http import HttpResponse


#From: http://www.redrobotstudios.com/blog/2009/02/18/securing-django-with-ssl/
def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


#From: http://noah.heroku.com/past/2010/2/19/django_http_basic_auth/
class http_auth_required(object):
  """
  A decorator to handle basic HTTP authentication. Takes a dictionary of
  username: password pairs to authenticate against.
  """
  def __init__(self, credentials):
    self.credentials = credentials

  def __call__(self, view):
    def inner(request, *args, **kwargs):
      # header indicates login attempt
      if request.META.has_key('HTTP_AUTHORIZATION'):
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2 and auth[0].lower() == 'basic':
            username, password = base64.b64decode(auth[1]).split(':')
            if self.credentials.has_key(username) and self.credentials[username] == password:
              request.META['REMOTE_USER'] = username
              return view(request, *args, **kwargs)

      # The credentials are incorrect, or not provided; challenge for username/password
      response = HttpResponse()
      response.status_code = 401
      response['WWW-Authenticate'] = 'Basic realm="restricted"'
      return response

    return inner