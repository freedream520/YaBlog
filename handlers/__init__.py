# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11

    I love cici.But I know I can not reach you.
    I can not find you.
    I miss you so much.
"""
from lib.handler import BaseHandler

class ErrorHandler(BaseHandler):

    def prepare(self):
        super(ErrorHandler, self).prepare()
        self.send_error(404)