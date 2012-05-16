# -*- coding:utf-8 -*_
"""
    @author messense
    @date 2012-05-12
    I love cici.
    时间万岁，我总会无力伤悲
"""
from lib.handler import BaseHandler, UIModule
from lib.util import ObjectDict, PageMixin

from models import Post
from models.mixin import PostMixin

class PostHandler(BaseHandler, PostMixin):

    def get(self, slug):
        post = self.get_post_by_slug(slug)
        if not post:
            self.send_error(404)
            return
        if post.type == Post.TYPE_POST:
            self.render('post.html', post=post)
        elif post.type == Post.TYPE_PAGE:
            self.render('page.html', page=post)

handlers = [
    ('/(.+)\.html', PostHandler),
    ('/([\w\-_]+)', PostHandler),
]

class PostListModule(UIModule, PageMixin):
    def render(self, tpl="modules/post_list.html"):
        p = self._get_page()
        key = "PostList:%s" % p
        html = self.cache.get(key)
        if not html:
            query = Post.query.filter_by(type=Post.TYPE_POST).order_by('-id')
            count = query.count()
            page = ObjectDict(self._get_pagination(query, count, 10))
            html = self.render_string(tpl, page=page)
            self.cache.set(key, html, 3600)
        return html

class CategoryPostListModule(UIModule, PageMixin):
    def render(self, category, tpl="modules/category_post_list.html"):
        p = self._get_page()
        key = "CategoryPostList:%s:%s" % (category.id, p)
        html = self.cache.get(key)
        if not html:
            query = Post.query.filter_by(type=Post.TYPE_POST, category_id=category.id).order_by('-id')
            count = query.count()
            page = ObjectDict(self._get_pagination(query, count, count))
            html = self.render_string(tpl, page=page)
            self.cache.set(key, html, 3600)
        return html

class TagPostListModule(UIModule, PageMixin):
    def render(self, tag, tpl="modules/tag_post_list.html"):
        p = self._get_page()
        key = "TagPostList:%s:%s" % (tag.id, p)
        html = self.cache.get(key)
        if not html:
            ids = tag.post_ids.split('|')
            query = Post.query.filter_by(id__in=ids).order_by('-id')
            count = query.count()
            page = ObjectDict(self._get_pagination(query, count, count))
            html = self.render_string(tpl, page=page)
            self.cache.set(key, html, 3600)
        return html

ui_modules = {
    'PostListModule' : PostListModule,
    'CategoryPostListModule' : CategoryPostListModule,
    'TagPostListModule' : TagPostListModule
}