# -*- coding:utf-8 -*-
import logging
import functools
import urlparse


def require_admin(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            url = self.get_login_url()
            if '?' not in url:
                if urlparse.urlsplit(url).scheme:
                    next_url = self.request.full_url()
                else:
                    next_url = self.request.uri
                url += '?next=' + next_url
                return self.redirect(url)
        return method(self, *args, **kwargs)
    return wrapper


class cache(object):
    """Cache decorator, an easy way to manage cache.
    The result key will be like: prefix:arg1-arg2k1#v1k2#v2
    """
    def __init__(self, prefix, time=0):
        self.prefix = prefix
        self.time = time

    def __call__(self, method):
        @functools.wraps(method)
        def wrapper(handler, *args, **kwargs):
            if not hasattr(handler, 'cache'):
                # fix for UIModule
                handler.cache = handler.handler.cache
            if not handler.cache:
                return method(handler, *args, **kwargs)

            if args:
                key = self.prefix + ':' + '-'.join(str(a) for a in args)
            else:
                key = self.prefix
            if kwargs:
                for k, v in kwargs.iteritems():
                    key += '%s#%s' % (k, v)

            value = handler.cache.get(key)
            if value is None:
                value = method(handler, *args, **kwargs)
                try:
                    handler.cache.set(key, value, self.time)
                except:
                    logging.warn('cache error: %s' % key)
                    pass
            return value
        return wrapper


def require_system(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip != '127.0.0.1':
            self.send_error(403)
            return
        return method(self, *args, **kwargs)
    return wrapper
