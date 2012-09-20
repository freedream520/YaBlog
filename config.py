# -*- coding:utf-8 -*-
import os
PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]

# Timezone
os.environ['TZ'] = 'Asia/Shanghai'

from tornado.options import define,options

define('version',1.0)
# server config
define('port', type=int, default=8002)
define('debug', type=bool, default=True)
define('master', type=str, default='mysql://demo:demo@localhost:3306/demo_blog?charset=utf8')
define('slaves', type=list, default=[])
# cache config
define('cache', type=str, default='memcache')
define('memcache', type=str, default='127.0.0.1:11211')
define('redis_host', type=str, default='')
define('redis_port', type=int, default=6379)
define('redis_db', type=int, default=0)
define('redis_password', type=str, default='')
define('redis_socket_timeout', type=int, default=None)

# site config
define('sitename', type=str, default='Messense')
define('siteurl', type=str, default='http://messense.me')
define('description', type=str, default='')
define('login_url', type=str, default='/dashboard/login')
define('static_path', type=str, default=os.path.join(PROJDIR,'static'))
define('static_url_prefix', type=str, default='/static/')
define('template_path', type=str, default=os.path.join(PROJDIR,'templates'))
define('locale_path', type=str, default=os.path.join(PROJDIR,'locale'))
define('default_locale', type=str, default='zh_CN')
define('xsrf_cookies', type=bool, default=False)
define('cookie_secret', type=str, default='QkiIjc2rT+GlhhTBaBAQNLybcuOIj0j8lKN/LW8rrHA=')
define('password_secret', type=str, default='cici')

# theme setting
define('theme_name',  type=str, default='default')
define('post_per_page', type=int, default=10)

# admin setting
define('admin_username', type=str, default='demo')
define('admin_password', type=str, default='demo')
define('admin_nickname', type=str, default='demo')

# duoshuo
define('duoshuo_shortname', type=str, default='messense')

# mail setting
define('mail_notify', default=False, type=bool)
define('mail_host', default='smtp.gmail.com:587', type=str)
define('mail_username', default='', type=str)
define('mail_password', default='', type=str)
define('mail_from_addr', default='', type=str)

# init  cache
cache = None
if options.cache:
    if options.cache == 'memcache':
        try:
            import memcache
            cache = memcache.Client(options.memcache.split(), debug=options.debug)
        except:
            pass
    elif options.cache == 'redis':
        try:
            import redis
            cache = redis.Redis(host=options.redis_host, port=options.redis_port, db=options.redis_db, password=options.redis_password, socket_timeout=options.redis_socket_timeout)
        except:
            pass