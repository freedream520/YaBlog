# -*- coding:utf-8 -*-
import re
import markdown

from tornado import escape
from tornado.options import options

from lib.ubb import ubb

def wrap_content(text):

    # get link back
    def make_link(m):
        link = m.group(1)
        title = link
        if link.startswith('http://') or link.startswith('https://'):
            return '<a href="%s" rel="nofollow">%s</a>' % (link, title)
        return '<a href="http://%s" rel="nofollow">%s</a>' % (link, title)

    # http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    pattern = re.compile(
        r'(?m)^((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}'
        r'/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+'
        r'|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')
    text = pattern.sub(make_link, text)

    pattern = re.compile(
        r'(?i)(?:&lt;)((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}'
        r'/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+'
        r'|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))(?:&gt;)')

    text = pattern.sub(make_link, text)

    return ubb(markdown.markdown(text))

def xmldatetime(value):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')