# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici and I miss you now.
"""
from lib.handler import BaseHandler, UIModule

from models.mixin import PostMixin

class IndexHandler(BaseHandler):

    def get(self):
        self.render('index.html')

class ArchiveHandler(BaseHandler):

    def get(self):
        self.render('archive.html')

handlers = [
    ('/', IndexHandler),
    ('/archive', ArchiveHandler),
]

class ArchiveModule(UIModule, PostMixin):
    def render(self, tpl="modules/archive.html"):
        key = "ArchiveHTML"
        html = self.cache.get(key)
        if not html:
            posts = self.get_all_posts()
            sorted_posts = {}
            year = None
            month = None
            month_posts = []
            for post in posts:
                post_year = post.created.strftime('%Y')
                post_month = post.created.strftime('%B')
                if not year or year != post_year:
                    year = post_year
                    sorted_posts[year] = {}
                if not month or month != post_month:
                    if month != post_month:
                        sorted_posts[year][month]=month_posts
                        month_posts = []
                    month = post_month
                month_posts.append(post)
            if month_posts:
                if sorted_posts[year] is not dict:
                    sorted_posts[year] = {}
                if month not in sorted_posts[year]:
                    sorted_posts[year][month] = month_posts
            html = self.render_string(tpl, posts=sorted_posts)
            self.cache.set(key, html, 3600)
        return html

ui_modules = {
    'ArchiveModule' : ArchiveModule,
}