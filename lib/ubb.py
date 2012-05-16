# -*- coding:utf-8 -*-
import re
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
from tornado import escape

def ubb(text):
    # ubb support for [br] and [br/]
    def ubb_br(m):
        return '<br/>'

    pattern = re.compile(r'(\[br/?\])', re.I)
    text = pattern.sub(ubb_br, text)

    # ubb support for [url][/url]
    def ubb_link(m):
        link = m.group(1)
        if link.startswith('http://') or link.startswith('https://'):
            return '<a href="%s" rel="nofollow">%s</a>' % (link, link)
        return '<a href="http://%s" rel="nofollow">%s</a>' % (link, link)

    pattern = re.compile(r'\[url\]([^\[\]]+)\[/url\]', re.I)
    text = pattern.sub(ubb_link, text)

    # ubb support for [url=link]title[/url]
    def ubb_link_title(m):
        link = m.group(1)
        title = m.group(2)
        if not title:
            title = link
        if link.startswith('http://') or link.startswith('https://'):
            return '<a href="%s" rel="nofollow" title="%s">%s</a>' % (link, title, title)
        return '<a href="http://%s" rel="nofollow" title="%s">%s</a>' % (link, title, title)

    pattern = re.compile(r'\[url=([^\[\]]+)\]([^\[\]]*)\[/url\]', re.I)
    text = pattern.sub(ubb_link_title, text)

    # ubb support for [img][/img]
    def ubb_img(m):
        src = m.group(1)
        return '<img src="%s" />' % src

    pattern = re.compile(r'\[img\]([^\[\]]+)\[/img\]', re.I)
    text = pattern.sub(ubb_img, text)

    # ubb support for [h1][/h1] to [h6][/h6]
    def ubb_html_title(m):
        n = m.group(1)
        title = m.group(2)
        return '<h%s>%s</h%s>' % (n, title, n)

    pattern = re.compile(r'\[h([1-6]){1}\](.+)\[/h\1\]', re.I)
    text = pattern.sub(ubb_html_title, text)

    # ubb support for [b] [u] [i] [del] [q] [p]
    def ubb_buidsqp(m):
        tp = m.group(1)
        if tp == 'd':
            tp = 'del'
        elif tp == 's':
            tp = 'sub'
        content = m.group(2)
        return '<%s>%s</%s>' % (tp, content, tp)

    pattern = re.compile(r'\[(b|u|i|d|s|q|p)\](.+)\[/\1\]', re.I)
    text = pattern.sub(ubb_buidsqp, text)

    # ubb support for font awesome icons
    def ubb_icon(m):
        icon = m.group(1)
        return '<i class="icon-%s"></i>' % icon

    pattern = re.compile(r'\[icon\]([\w-]+)\[/icon\]', re.I)
    text = pattern.sub(ubb_icon, text)

    # ubb support for [quote]
    def ubb_quote(m):
        content = m.group(1)
        return '<blockquote>%s</blockquote>' % content

    pattern = re.compile(r'\[quote\](.+)\[/quote\]', re.I | re.M)
    text = pattern.sub(ubb_quote, text)

    # ubb support for [pre]
    def ubb_pre(m):
        content = m.group(1)
        return '<pre>%s</pre>' % content

    pattern = re.compile(r'\[pre\](.+)\[/pre\]', re.I | re.M)
    text = pattern.sub(ubb_pre, text)

    # ubb support for [code]
    def ubb_code(m):
        formatter = HtmlFormatter(noclasses=False)
        try:
            name = m.group(1)
            lexer = get_lexer_by_name(name)
        except ValueError:
            name = 'text'
            lexer = TextLexer()
        content = m.group(2).replace('&quot;', '"').replace('&amp;', '&').replace('&nbsp;', ' ').replace('<p>','').replace('</p>','')
        content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&#39;','"')
        code = highlight(content, lexer, formatter)
        code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '<br />')
        return '\n\n<div class="code">%s</div>\n\n' % code

    pattern = re.compile(r'\[code=([\w\-\+#]+)\](.+)\[/code\]', re.I | re.S | re.M)
    text = pattern.sub(ubb_code, text)

    # ubb support for audio player
    def ubb_music(m):
        url = m.group(2)
        return '<div class="player"><embed class="mp3_player" src="/static/audio_player.swf?audio_file=%s&color=FFFFFF" width="207" height="60" type="application/x-shockwave-flash"></embed></div>' % url

    pattern = re.compile(r'\[music\](\S+)\[/music\]', re.I)
    text = pattern.sub(ubb_music, text)

    # ubb for xiami music
    def ubb_xiami_music(m):
        id = m.group(2)
        return '<div class="player"><embed src="http://www.xiami.com/widget/0_%s/singlePlayer.swf" type="application/x-shockwave-flash" width="257" height="33" wmode="transparent"></embed></div>' % id

    pattern = re.compile(r'\[xiami\](http://www\.xiami\.com/song/)?(\d+)(\?[\w=]*)?\[/xiami\]', re.I)
    text = pattern.sub(ubb_xiami_music, text)

    return text