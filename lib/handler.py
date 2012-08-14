# -*- coding:utf-8 -*-
import re
import os
import datetime
import hashlib

from tornado import web
from tornado.web import RequestHandler
from tornado.options import options
from tornado import escape
from tornado import locale

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

from lib.util import ObjectDict, create_token
from lib.filters import xmldatetime, wrap_content

class AppHandler(RequestHandler):

    _first_run = True

    def initialize(self):
        if AppHandler._first_run:
            AppHandler._first_run = False

    def finish(self, chunk=None):
        super(AppHandler,self).finish(chunk)
        if self.get_status() == 500:
            try:
                self.db.commit()
            except:
                self.db.rollback()
            finally:
                self.db.commit()

    def on_finish(self):
        self.db.remove()

    @property
    def db(self):
        return self.application.db

    @property
    def cache(self):
        return self.application.cache

    # locale translate alias
    def _(self, content):
        return self.locale.translate(content)

    def get_error_html(self, status_code, **kwargs):
        if not options.debug:
            self.set_status(status_code)
            return self.render_string('%s.html' % status_code, **kwargs)
        else:
            def get_snippet(fp, target_line, num_lines):
                if fp.endswith('.html'):
                    fp = os.path.join(self.get_template_path(), fp)
                half_lines = (num_lines/2)
                try:
                    with open(fp) as f:
                        all_lines = [line for line in f]
                        code = ''.join(all_lines[target_line-half_lines-1:target_line+half_lines])
                        formatter = HtmlFormatter(linenos=True, linenostart=target_line-half_lines, hl_lines=[half_lines+1])
                        lexer = get_lexer_for_filename(fp) 
                        return highlight(code, lexer, formatter)
                except Exception, ex:
                    return ''

            css = HtmlFormatter().get_style_defs('.highlight')
            exception = kwargs.get('exception', None)
            exception_template = os.path.join(self.settings['template_path'], 'exception.html')
            return self.render_string(exception_template, 
                                      get_snippet=get_snippet,
                                      css=css,
                                      exception=exception,
                                      status_code=status_code, 
                                      kwargs=kwargs)

    @property
    def next_url(self):
        next_url = self.get_argument('next',None)
        if next_url:
            next_url = next_url.replace('%2F', '/')
        return next_url or '/'

    def is_mobile(self):
        _mobile = (r'ipod|iphone|android|blackberry|palm|nokia|symbian|'
                   r'samsung|psp|kindle|phone|mobile|ucweb|opera mini|fennec|'
                   r'webos')
        return True if re.search(_mobile, self.user_agent.lower()) else False

    def is_spider(self):
        _spider = r'bot|crawl|spider|slurp|search|lycos|robozilla|fetcher'
        return True if re.search(_spider, self.user_agent.lower()) else False

    def is_ajax(self):
        return "XMLHttpRequest" == self.request.headers.get("X-Requested-With")

    @property
    def user_agent(self):
        return self.request.headers.get("User-Agent", "bot")


class BaseHandler(AppHandler):

    def prepare(self):
        self._prepare_context()
        self._prepare_filters()

    def render_string(self, template_name, **kwargs):
        kwargs.update(self._filters)
        assert "context" not in kwargs, "context is a reserved keyword."
        kwargs["context"] = self._context
        return super(BaseHandler, self).render_string(template_name,**kwargs)

    def get_template_path(self):
        return os.path.join(options.template_path, options.theme_name)

    def print_form_error(self, field, css_class='form-error'):
        if field and hasattr(self._context.form, field):
            ret = self.locale.translate(getattr(self._context.form, field))
            if ret:
                return '<span class="' + css_class + '">' + ret + '</span>'
        return ''

    def print_form_class(self, field, css='error'):
        if self.print_form_error(field):
            return ' %s' % css
        return ''

    def add_context(self, name, value):
        setattr(self._context, name, value)

    def add_filter(self, name, func):
        setattr(self._filters, name, func)

    def _prepare_context(self):
        self._context = ObjectDict()
        self._context.now = datetime.datetime.utcnow()
        self._context.version = options.version
        self._context.sitename = options.sitename
        self._context.siteurl = options.siteurl
        self._context.description = options.description
        self._context.debug = options.debug
        self._context.duoshuo_shortname = options.duoshuo_shortname
        self._context.message = []
        self._context.form = ObjectDict()
        self._context.next_url = self.next_url or self.request.headers.get("HTTP-REFERER",'/')

    def _prepare_filters(self):
        self._filters = ObjectDict()
        self._filters.markdown = wrap_content
        self._filters.xmldatetime = xmldatetime
        self._filters.format_date = self.format_date
        self._filters.is_mobile = self.is_mobile
        self._filters.is_spider = self.is_spider
        self._filters.form_error = self.print_form_error
        self._filters.form_class = self.print_form_class

    def format_date(self, date):
        # GMT +8
        return self.locale.format_date(date, -480)

    def create_message(self, msg):
        self._context.message.append(msg)

    def form_error(self, field, msg=''):
        setattr(self._context.form, field, msg)

class DashboardHandler(BaseHandler):

    def get_current_user(self):
        cookie = self.get_secure_cookie('token')
        if not cookie:
            return None
        token = hashlib.md5(options.admin_username).hexdigest()
        if cookie != token:
            self.clear_cookie('token')
            return None
        return True

    def get_template_path(self):
        return self.settings.get('template_path')

class ApiHandler(AppHandler):

    xsrf_protect = False

    def check_xsrf_cookie(self):
        if not self.xsrf_protect:
            return
        return super(ApiHandler, self).check_xsrf_cookie()

    def get_current_user(self):
        cookie = self.get_secure_cookie('token')
        if not cookie:
            return None
        token = hashlib.md5(options.admin_username).hexdigest()
        if cookie != token:
            self.clear_cookie('token')
            return None
        return True
    
    def write(self, chunk):
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            callback = self.get_argument('callback', None)
            if callback:
                chunk = "%s{%s}" % (callback, escape.to_unicode(chunk))
            self.set_header("Content-Type","application/javascript; charset=UTF-8")
        super(ApiHandler, self).write(chunk)

class UIModule(web.UIModule):

    @property
    def db(self):
        return self.handler.db

    @property
    def cache(self):
        return self.handler.cache

    # locale translate
    def _(self, content):
        return self.handler._(content)