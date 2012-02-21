# coding: utf-8

from django.forms.widgets import Widget
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from lancero.misc import fckeditor

# From: http://www.djangosnippets.org/snippets/576/
class FCKeditor(Widget):
    def __init__(self, attrs=None):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}

        self.__widget = fckeditor.FCKeditor("FCKeditor1")
        super(FCKeditor, self).__init__(attrs)

        self.setAttrs(self.attrs)

    def setAttrs(self, attrs):
        if attrs is None:
            return

        if 'basepath' in attrs:
            self.__widget.BasePath = attrs['basepath']

        if 'width' in attrs:
            self.__widget.Width = attrs['width']

        if 'height' in attrs:
            self.__widget.Height = attrs['height']

        if 'toolbar' in attrs:
            self.__widget.ToolbarSet = attrs['toolbar']

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        value = force_unicode(value)

        self.__widget.InstanceName = name
        self.__widget.Value = value
        self.setAttrs(attrs)

        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(self.__widget.CreateHtml())
