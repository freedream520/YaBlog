# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici.
    Hey.我真的好想你，不知道你现在到底在哪里.
"""
from lib.handler import BaseHandler, UIModule

from models.mixin import CategoryMixin


class CategoryListHandler(BaseHandler):
    def get(self):
        self.render('categories.html')


class CategoryHandler(BaseHandler, CategoryMixin):
    def get(self, slug):
        category = self.get_category_by_slug(slug)
        if not category:
            self.send_error(404)
            return
        self.render('category.html', category=category)

handlers = [
    ('/categories', CategoryListHandler),
    ('/category/([\w\-_]+)', CategoryHandler),
]


class CategoryListModule(UIModule, CategoryMixin):
    def render(self, tpl="modules/category_list.html"):
        key = "CategoryList"
        html = self.cache.get(key)
        if not html:
            categories = self.get_all_categories()
            html = self.render_string(tpl, categories=categories)
            self.cache.set(key, html, 3600)
        return html


class CategoryListWidget(UIModule, CategoryMixin):
    def render(self, tpl="modules/category_list_widget.html"):
        key = "CategoryListWidget"
        html = self.cache.get(key)
        if not html:
            categories = self.get_all_categories()
            html = self.render_string(tpl, categories=categories)
            self.cache.set(key, html, 3600)
        return html

ui_modules = {
    'CategoryListModule': CategoryListModule,
    'CategoryListWidget': CategoryListWidget,
}
