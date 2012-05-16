# -*- coding:utf-8 -*-
import os
PROJDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.split(PROJDIR)[0]

# Timezone
os.environ['TZ'] = 'Asia/Shanghai'

from tornado.options import define,options

define('version',1.0)
# server config
define('port',8002)
define('debug',True)
define('master','mysql://messense:ilovecc@localhost:3306/messense_blog?charset=utf8')
define('slaves',[])
# cache config
define('cache', 'memcache')
define('memcache', '127.0.0.1:11211')
define('redis_host', '')
define('redis_port', 6379)
define('redis_db', 0)
define('redis_password', '')
define('redis_socket_timeout', None)

# site config
define('sitename','Messense')
define('siteurl','http://messense.me')
define('login_url','/dashboard/login')
define('static_path',os.path.join(PROJDIR,'static'))
define('static_url_prefix','/static/')
define('template_path',os.path.join(PROJDIR,'templates'))
define('locale_path',os.path.join(PROJDIR,'locale'))
define('default_locale','zh_CN')
define('xsrf_cookies',False)
define('cookie_secret','QkiIjc2rT+GlhhTBaBAQNLybcuOIj0j8lKN/LW8rrHA=')
define('password_secret', 'cici')

# admin setting
define('admin_username', 'messense')
define('admin_password', 'ilovecc.in')
define('admin_nickname', 'messense')

# mail setting
define('mail_notify', False)
define('mail_host', 'smtp.gmail.com:587')
define('mail_username', 'wapdevelop@gmail.com')
define('mail_password', 'anwigfcmktrsknel')
define('mail_from_addr', 'wapdevelop@gmail.com')

# Gravatar config
define('gravatar_base_url','http://ruby-china.org/avatar/')
define('gravatar_extra','')

# emoji
define('emoji_url', '')

# duoshuo
define('duoshuo_shortname', 'messense')

# init db
from lib.database import SQLAlchemy
db = SQLAlchemy(options.master, options.slaves, echo=options.debug, convert_unicode=True)

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