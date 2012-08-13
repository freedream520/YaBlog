# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici.
    I guess when you're young...you just believe there'll be many people with whom you'll connect with.
    Later in life you realize it only happens a few times. 
"""
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer,String,DateTime,Text, Boolean
from sqlalchemy.orm import relationship, backref
from tornado.options import options

from lib.database import db

class Tag(db.Model):

    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    post_count = Column(Integer, default=0, index=True)
    post_ids = Column(Text)

    @property
    def permalink(self):
        if not hasattr(self, '_permalink'):
            self._permalink = "%s/tag/%s" % (options.siteurl, self.slug)
        return self._permalink

class Post(db.Model):

    TYPE_POST = 'post'
    TYPE_PAGE = 'page'

    category_id = Column(Integer, ForeignKey('category.id'), index=True, nullable=False)
    type = Column(String(30), default='post', index=True)
    title = Column(String(200))
    content = Column(Text)
    html = Column(Text)
    slug = Column(String(200), unique=True, index=True)
    format = Column(String(30))
    excerpt = Column(Text)
    thumbnail = Column(String(500))
    keywords = Column(String(100))
    description = Column(String(200))
    created = Column(DateTime, index=True, default=datetime.utcnow)
    updated = Column(DateTime, index=True, default=datetime.utcnow)
    views = Column(Integer, index=True, default=0)
    tag_ids = Column(String(1000))
    comment_open = Column(Boolean, default=True)

    @property
    def tags(self):
        if not hasattr(self, '_tags'):
            ids = self.tag_ids.split('|')
            if ids:
                ids = set([int(id) for id in ids if id and id.isdigit()])
            if ids:
                self._tags = Tag.query.filter_by(id__in=ids).all()
            else:
                self._tags = []
        return self._tags

    @property
    def tags_str(self):
        tags = self.tags
        if not tags:
            return ''
        post_tags = [tag.title for tag in tags]
        return ','.join(post_tags)

    @property
    def permalink(self):
        if not hasattr(self, '_permalink'):
            self._permalink = "%s/%s.html" % (options.siteurl, self.slug)
        return self._permalink

    def has_format(self, format):
        return self.format == format

class Category(db.Model):

    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(String(500))
    post_count = Column(Integer, default=0, index=True)

    posts = relationship('Post', backref='category')

    @property
    def permalink(self):
        if not hasattr(self, '_permalink'):
            self._permalink = "%s/category/%s" % (options.siteurl, self.slug)
        return self._permalink

class Link(db.Model):

    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(String(200))