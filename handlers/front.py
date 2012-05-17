# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici and I miss you now.
"""
from lib.handler import BaseHandler, UIModule

from models import Post
from models.mixin import PostMixin

class IndexHandler(BaseHandler):

    def get(self):
        self.render('index.html')

class ArchiveHandler(BaseHandler):

    def archive_list(self, posts):
        years = list(set(post.created.year for post in posts))
        years.sort(reverse=True)
        for year in years:
            year_posts = [post for post in posts if post.created.year == year]
            yield (year, year_posts)

    def get(self):
        self.add_filter('archive_list', self.archive_list)
        self.render('archive.html')

class FeedHandler(BaseHandler):

    def format_feed_date(self, dt):
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
            dt.day,
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month - 1],
            dt.year, dt.hour, dt.minute, dt.second)

    def get(self):
        self.add_filter('format_feed_date', self.format_feed_date)
        posts = Post.query.filter_by(type=Post.TYPE_POST).order_by('-id').all()
        self.set_header("Content-Type","application/rss+xml; charset=UTF-8")
        self.render('feed.xml', posts=posts)

handlers = [
    ('/', IndexHandler),
    ('/archive', ArchiveHandler),
    ('/feed', FeedHandler),
]

class ArchiveModule(UIModule, PostMixin):
    def render(self, tpl="modules/archive.html"):
        key = "ArchiveHTML"
        html = self.cache.get(key)
        if not html:
            posts = Post.query.filter_by(type=Post.TYPE_POST).order_by('-id').all()
            html = self.render_string(tpl, posts=posts)
            self.cache.set(key, html, 3600)
        return html

ui_modules = {
    'ArchiveModule' : ArchiveModule,
}