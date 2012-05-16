# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici.
    我爱的人不是我的爱人
    她心里每一寸都属于另一个人
    她真幸福幸福得真残忍
"""
from lib.handler import BaseHandler, UIModule

from models import Link
from models.mixin import LinkMixin

class LinksHandler(BaseHandler):

    def get(self):
        self.render('links.html')

handlers = [
    ('/links', LinksHandler),
]

class LinkListModule(UIModule, LinkMixin):
    def render(self, tpl="modules/link_list.html"):
        key = "LinkList"
        html = self.cache.get(key)
        if not html:
            links = self.get_all_links()
            html = self.render_string(tpl, links=links)
            self.cache.set(key, html, 3600)
        return html

ui_modules = {
    'LinkListModule' : LinkListModule,
}