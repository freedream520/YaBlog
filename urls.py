# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici.
    Is there any route to your heart?
"""
from handlers import front
from handlers import post
from handlers import category
from handlers import tag
from handlers import link
from handlers import api
from handlers import dashboard

from handlers import ErrorHandler

# Routes
handlers = []
handlers.extend(front.handlers)
handlers.extend(category.handlers)
handlers.extend(tag.handlers)
handlers.extend(link.handlers)
handlers.extend(api.handlers)
handlers.extend(dashboard.handlers)
handlers.extend(post.handlers)
# Error handler
handlers.append((r'.*', ErrorHandler))

# UIModules
ui_modules = {}
ui_modules.update(front.ui_modules)
ui_modules.update(post.ui_modules)
ui_modules.update(category.ui_modules)
ui_modules.update(tag.ui_modules)
ui_modules.update(link.ui_modules)
ui_modules.update(dashboard.ui_modules)