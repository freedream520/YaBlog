# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici.
    遇见了你，爱上了你，最后重归于平静
"""
from lib.handler import BaseHandler, UIModule

from models.mixin import TagMixin


class TagHandler(BaseHandler, TagMixin):
    def get(self, slug):
        tag = self.get_tag_by_slug(slug)
        if not tag:
            self.send_error(404)
            return
        self.render('tag.html', tag=tag)


class TagCloudHandler(BaseHandler):
    def get(self):
        self.render('tags.html')

handlers = [
    ('/tag/(.+)', TagHandler),
    ('/tags', TagCloudHandler),
]


class TagCloudModule(UIModule, TagMixin):
    def render(self, tpl="modules/tag_cloud.html"):
        key = "TagCloud"
        html = self.cache.get(key)
        if not html:
            tags = self.get_all_tags()
            html = self.render_string(tpl, tags=tags)
            self.cache.set(key, html, 3600)
        return html

ui_modules = {
    'TagCloudModule': TagCloudModule,
}
