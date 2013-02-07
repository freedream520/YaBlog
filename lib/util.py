# -*- coding:utf-8 -*-
import functools
import hashlib
from random import choice

from HTMLParser import HTMLParser

from tornado import ioloop, stack_context
from tornado.options import define, options


def create_salt(length=16):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt = ''.join([choice(chars) for i in range(length)])
    return salt


def create_token(raw):
    salt = create_salt(8)
    hsh = hashlib.sha1(salt + raw + options.password_secret).hexdigest()
    return "%s$%s" % (salt, hsh)


def parse_config_file(path):
    if not path:
        return
    config = {}
    exec(compile(open(path).read(), path, 'exec'), config, config)
    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, config[name])


def delay_call(func, *arg, **kwargs):
    with stack_context.NullContext():
        io = ioloop.IOLoop.instance()
        io.add_callback(functools.partial(func, *arg, **kwargs))


class PageMixin(object):
    def _get_order(self, default='-id', orders={}):
        if not hasattr(self, 'get_argument'):
            self.get_argument = self.handler.get_argument
        order = self.get_argument('o', '0')
        if orders.get(order, None):
            return orders.get(order)
        return default

    def _get_page(self):
        if not hasattr(self, 'get_argument'):
            self.get_argument = self.handler.get_argument
        page = self.get_argument('p', '1')
        try:
            page = int(page)
            if page < 1:
                page = 1
            return page
        except:
            return 1

    def _get_pagination(self, q, count=None, perpage=10):
        if not hasattr(self, 'get_argument'):
            self.get_argument = self.handler.get_argument
        order = self.get_argument('o', '0')
        try:
            order = int(order)
        except:
            order = 0
        if not count:
            count = q.count()
        if perpage == 0:
            perpage = 10
        page_number = (count - 1) / perpage + 1  # this algorithm is fabulous
        page = self._get_page()
        if page > page_number:
            page = page_number
        if page < 1:
            page = 1

        offset = (page - 1) * perpage

        dct = {}
        dct['page_number'] = page_number
        dct['datalist'] = q.offset(offset).limit(perpage).all()
        if page < 5:
            dct['pagelist'] = range(1, min(page_number, 9) + 1)
        elif page + 4 > page_number:
            dct['pagelist'] = range(max(page_number - 8, 1), page_number + 1)
        else:
            dct['pagelist'] = range(page - 4, min(page_number, page + 4) + 1)
        dct['current_page'] = page
        dct['item_number'] = count
        dct['order'] = order
        return dct


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
