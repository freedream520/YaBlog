# -*- coding:utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

import config
import tornado.options
import tornado.locale
from tornado.options import define, options
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado import web
from lib.util import parse_config_file

class Application(web.Application):
    
        def __init__(self):
            from urls import handlers,ui_modules
            settings = dict(
                debug = options.debug,
                autoescape = None,
                cookie_secret = options.cookie_secret,
                xsrf_cookies = options.xsrf_cookies,
                static_path = options.static_path,
                template_path = options.template_path,
                static_url_prefix = options.static_url_prefix,
                ui_modules = ui_modules,
                login_url = options.login_url
            )
            super(Application,self).__init__(handlers,**settings)
            Application.db = config.db.session
            Application.cache = config.cache
            tornado.locale.load_translations(options.locale_path)
            tornado.locale.set_default_locale(options.default_locale)

def main():
    define('setting','')
    tornado.options.parse_command_line()
    parse_config_file(options.setting)
    server = HTTPServer(Application(),xheaders = True)
    server.listen(int(options.port))
    IOLoop.instance().start()

if __name__ == '__main__':
    main()