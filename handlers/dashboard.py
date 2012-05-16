# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-13
    I love cici.
    What are you doing now?
"""
import hashlib

from tornado.options import options

from lib.handler import BaseHandler, UIModule
from lib.filters import wrap_content
from lib.decorators import require_admin
from lib.util import create_token, PageMixin, ObjectDict

from models import Post, Category, Tag, Link
from models.mixin import PostMixin, CategoryMixin, TagMixin, LinkMixin

class DashboardLoginHandler(BaseHandler):

    def prepare(self):
        super(DashboardLoginHandler, self).prepare()
        if self.current_user:
            self.redirect('/dashboard')

    def get(self):
        self.render('dashboard/login.html', username='')

    def post(self):
        err = False
        username = self.get_argument('usename', None)
        password = self.get_argument('password', None)
        if not username:
            err = True
            self.form_error('username', 'Username field can not be empty')
        if not password:
            err = True
            self.form_error('password', 'Password field can not be empty')
        if username != options.admin_username or password != options.admin_password:
            err = True
            self.form_error('form', 'Username or password is not correct')

        if err:
            self.render('dashboard_login.html', username=username)
            return
        # login succeed,go to dashboard index page
        token = hashlib.md5(options.admin_username).hexdigest()
        self.set_secure_cookie('token', token)
        self.redirect('/dashboard')

class DashboardIndexHandler(BaseHandler):
    
    @require_admin
    def get(self):
        self.render('dashboard/index.html')

class DashboardCategoryListHandler(BaseHandler, CategoryMixin):

    @require_admin
    def get(self):
        self.render('dashboard/categories.html', categories=self.get_all_categories())

class DashboardPostListHandler(BaseHandler, PageMixin):

    @require_admin
    def get(self):
        p = self._get_page()
        query = Post.query.filter_by(type=Post.TYPE_POST).order_by('-id')
        page = ObjectDict(self._get_pagination(query, query.count(), 10))
        self.render('dashboard/posts.html', page=page)

class DashboardPageListHandler(BaseHandler, PostMixin):

    @require_admin
    def get(self):
        self.render('dashboard/pages.html', pages=self.get_all_pages())

class DashboardTagListHandler(BaseHandler, PageMixin):

    @require_admin
    def get(self):
        p = self._get_page()
        query = Tag.query.order_by('+id')
        page = ObjectDict(self._get_pagination(query, query.count(), 10))
        self.render('dashboard/tags.html', page=page)

class DashboardLinkListHandler(BaseHandler, LinkMixin):

    @require_admin
    def get(self):
        self.render('dashboard/links.html', links=self.get_all_links())

class DashboardCreatePostHandler(BaseHandler, CategoryMixin):

    @require_admin
    def get(self):
        self.render('dashboard/create_post.html', categories=self.get_all_categories())

class DashboardEditPostHandler(BaseHandler, PostMixin, CategoryMixin):

    @require_admin
    def get(self, id):
        post = self.get_post_by_id(id)
        if not post:
            self.send_error(404)
            return
        self.render('dashboard/edit_post.html', post=post, categories=self.get_all_categories())

class DashboardCreatePageHandler(BaseHandler):

    @require_admin
    def get(self):
        self.render('dashboard/create_page.html')

class DashboardEditPageHandler(BaseHandler, PostMixin):

    @require_admin
    def get(self, id):
        page = self.get_post_by_id(id)
        if not page:
            self.send_error(404)
            return
        self.render('dashboard/edit_page.html', page=page)

handlers = [
    ('/dashboard/login', DashboardLoginHandler),
    ('/dashboard', DashboardIndexHandler),
    ('/dashboard/category/list', DashboardCategoryListHandler),
    ('/dashboard/post/list', DashboardPostListHandler),
    ('/dashboard/page/list', DashboardPageListHandler),
    ('/dashboard/tag/list', DashboardTagListHandler),
    ('/dashboard/link/list', DashboardLinkListHandler),
    ('/dashboard/post/create', DashboardCreatePostHandler),
    ('/dashboard/post/(\d+)', DashboardEditPostHandler),
    ('/dashboard/page/create', DashboardCreatePageHandler),
    ('/dashboard/page/(\d+)', DashboardEditPageHandler),
]

class SystemStatusModule(UIModule):
    def render(self, tpl="modules/system_status.html"):
        key = 'SystemStatus'
        html = self.cache.get(key)
        if not html:
            category_count = Category.query.count()
            post_count = Post.query.filter_by(type=Post.TYPE_POST).count()
            page_count = Post.query.filter_by(type=Post.TYPE_PAGE).count()
            tag_count = Tag.query.count()
            link_count = Link.query.count()
            html = self.render_string(tpl, category_count=category_count, post_count=post_count, page_count=page_count, tag_count=tag_count, link_count=link_count)
            self.cache.set(key, html, 3600)
        return html

ui_modules = {
    'SystemStatusModule' : SystemStatusModule,
}