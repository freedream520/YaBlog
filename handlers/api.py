# -*- coding:utf-8 -*-
"""
    @author messense
    @date 2012-05-11
    I love cici.
    Miss you so much now.
"""
from datetime import datetime

from tornado.options import options

from lib.handler import ApiHandler
from lib.filters import wrap_content
from lib import validators

from models import Post, Category, Tag, Link
from models.mixin import PostMixin, CategoryMixin, TagMixin, LinkMixin

class PostListApiHandler(ApiHandler, CategoryMixin):

    """
    List posts.
    Pass a param category in query string to get posts by category
    """
    def get(self):
        json = {}
        p = self.get_argument('p', 1) # current page
        count = self.get_argument('count', 10) # show post count
        try:
            p = int(p)
            count = int(count)
        except:
            p = 1
            count = 10
        category_id = self.get_argument('category', 0) # show post by category
        try:
            category_id = int(category_id)
        except:
            category_id = 0
        if category_id > 0:
            category = self.get_category_by_id(category_id)
            if not category:
                json = {
                    'error' : 1,
                    'msg' : self._('No such category')
                }
                self.write(json)
                return
            offset = (p -1)*count
            posts = Post.query.filter_by(type=Post.TYPE_POST, category_id=category_id).offset(offset).limit(count).all()
            posts_json = [{
                'id' : post.id,
                'title' : post.title,
                'slug' : post.slug,
                'format' : post.format,
                'excerpt' : post.excerpt,
                'thumbnail' : post.thumbnail,
                'created' : post.created.strftime('%Y-%m-%d %H:%M'),
                'updated' : post.updated.strftime('%Y-%n-%d %H:%M'),
                'views' : post.views,
                'permalink' : post.permalink,
                'comment_open' : post.comment_open
            } for post in posts]
            json = {
                'error' : 0,
                'posts' : posts_json,
                'category' : {
                    'id' : category_id,
                    'title' : category.title,
                    'slug' : category.slug,
                    'description' : category.description,
                    'permalink' : category.permalink,
                    'post_count' : category.post_count
                }
            }
        else:
            offset = (p -1)*count
            posts = Post.query.filter_by(type=Post.TYPE_POST).offset(offset).limit(count).all()
            posts_json = [{
                'id' : post.id,
                'title' : post.title,
                'slug' : post.slug,
                'format' : post.format,
                'excerpt' : post.excerpt,
                'thumbnail' : post.thumbnail,
                'created' : post.created.strftime('%Y-%m-%d %H:%M:%S'),
                'updated' : post.updated.strftime('%Y-%n-%d %H:%M:%S'),
                'views' : post.views,
                'permalink' : post.permalink,
                'comment_open' : post.comment_open,
                'category' : {
                    'id' : post.category.id,
                    'title' : post.category.title,
                    'slug' : post.category.slug,
                    'description' : post.category.description,
                    'permalink' : post.category.permalink,
                    'post_count' : post.category.post_count
                }
            } for post in posts]
            json = {
                'error' : 0,
                'posts' : posts_json
            }
        self.write(json)

class PostApiHandler(ApiHandler, PostMixin, CategoryMixin, TagMixin):

    """
    Get a post by id
    """
    def get(self, id):
        json = {}
        post = self.get_post_by_id(id)
        if not post:
            json = {
                'error' : 1,
                'msg' : self._('Post not found')
            }
            self.write(json)
            return
        json = {
            'error' : 0,
            'post' : {
                'id' : post.id,
                'title' : post.title,
                'slug' : post.slug,
                'format' : post.format,
                'excerpt' : post.excerpt,
                'thumbnail' : post.thumbnail,
                'created' : post.created.strftime('%Y-%m-%d %H:%M:%S'),
                'updated' : post.updated.strftime('%Y-%n-%d %H:%M:%S'),
                'views' : post.views,
                'permalink' : post.permalink,
                'category' : {
                    'id' : post.category.id,
                    'title' : post.category.title,
                    'slug' : post.category.slug,
                    'description' : post.category.description,
                    'permalink' : post.category.permalink,
                    'post_count' : post.category.post_count
                }
            }
        }
        self.write(json)

    """
    Create new post
    """
    def post(self):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return
        type = self.get_argument('type', Post.TYPE_POST)
        title = self.get_argument('title', None)
        content = self.get_argument('content', '')
        slug = self.get_argument('slug', None)
        format = self.get_argument('format', 'standard')
        excerpt = self.get_argument('excerpt', '')
        thumbnail = self.get_argument('thumbnail', '')
        category_id = self.get_argument('category', None)
        tags = self.get_argument('tags', '')
        date = self.get_argument('date', None)
        comment_open = bool(int(self.get_argument('comment_open', '1')))
        if type not in [Post.TYPE_POST, Post.TYPE_PAGE]:
            type = Post.TYPE_POST
        if format not in ['standard', 'aside', 'gallery', 'link', 'image', 'quote', 'status', 'video', 'audio', 'chat']:
            format = 'standard'
        # valid arguments
        if not slug:
            json = {
                'error' : 1,
                'msg' : self._('Slug field can not be empty')
            }
            self.write(json)
            return
        elif self.get_post_by_slug(slug):
            json = {
                'error' : 1,
                'msg' : self._('Slug already exists')
            }
            self.write(json)
            return
        if type == Post.TYPE_POST and not category_id:
            json = {
                'error' : 1,
                'msg' : self._('Category field can not be empty')
            }
            self.write(json)
            return
        if type == Post.TYPE_POST:
            category = self.get_category_by_id(category_id)
            if not category:
                json = {
                    'error' : 1,
                    'msg' : self._('No such category')
                }
                self.write(json)
                return
        if date:
            if validators.date(date):
                date = datetime.strptime(date, '%Y-%m-%d')
            elif validators.datetime(date):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            else:
                date = datetime.utcnow()
        else:
            date = datetime.utcnow()
        # now create post
        post = Post()
        post.type = type
        post.created = date
        post.title = title
        post.slug = slug
        post.content = content
        post.html = wrap_content(content)
        post.format = format
        post.excerpt = excerpt
        post.thumbnail = thumbnail
        post.comment_open = comment_open
        if type == Post.TYPE_POST:
            post.category_id = category.id
        else:
            post.category_id = 1 # default category
        # update category post count
        if type == Post.TYPE_POST:
            category.post_count += 1
            self.db.add(category)
        # commit
        self.db.add(post)
        self.db.commit()
        # create tags
        if type == Post.TYPE_POST and tags:
            post.tag_ids = self.create_tags(tags.split(','), post.id)
            self.db.add(post)
            self.db.commit()
        # delete cache
        keys = ['PostList:1', 'CategoryPostList:%s:1' % category.id, 'SystemStatus', 'ArchiveHTML', 'TagCloud']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully created'),
            'post' : {
                'post' : {
                'id' : post.id,
                'title' : post.title,
                'slug' : post.slug,
                'format' : post.format,
                'excerpt' : post.excerpt,
                'thumbnail' : post.thumbnail,
                'created' : post.created.strftime('%Y-%m-%d %H:%M'),
                'updated' : post.updated.strftime('%Y-%n-%d %H:%M'),
                'views' : post.views,
                'permalink' : post.permalink
            }
            }
        }
        if type == Post.TYPE_POST:
            json['category'] = {
                'id' : category.id,
                'title' : category.title,
                'slug' : category.slug,
                'description' : category.description,
                'permalink' : category.permalink,
                'post_count' : category.post_count
            }
        self.write(json)

    """
    Modify a post
    """
    def put(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        post = self.get_post_by_id(id)
        if not post:
            json = {
                'error' : 1,
                'msg' : self._('Post not found')
            }
            self.write(json)
            return
        quick = bool(self.get_argument('quick', ''))
        type = self.get_argument('type', Post.TYPE_POST)
        title = self.get_argument('title', None)
        content = self.get_argument('content', '')
        slug = self.get_argument('slug', None)
        format = self.get_argument('format', 'standard')
        excerpt = self.get_argument('excerpt', '')
        thumbnail = self.get_argument('thumbnail', '')
        category_id = self.get_argument('category', None)
        tags = self.get_argument('tags', '')
        date = self.get_argument('date', None)
        comment_open = bool(int(self.get_argument('comment_open', '1')))
        if type not in [Post.TYPE_POST, Post.TYPE_PAGE]:
            type = post.type
        if format not in ['standard', 'aside', 'gallery', 'link', 'image', 'quote', 'status', 'video', 'audio', 'chat']:
            format = 'standard'
        # valid arguments
        if not slug:
            json = {
                'error' : 1,
                'msg' : self._('Slug field can not be empty')
            }
            self.write(json)
            return
        elif slug != post.slug and self.get_post_by_slug(slug):
            json = {
                'error' : 1,
                'msg' : self._('Slug already exists')
            }
            self.write(json)
            return
        if type == Post.TYPE_POST and not category_id:
            json = {
                'error' : 1,
                'msg' : self._('Category field can not be empty')
            }
            self.write(json)
            return
        if type == Post.TYPE_POST:
            category = self.get_category_by_id(category_id)
            if not category:
                json = {
                    'error' : 1,
                    'msg' : self._('No such category')
                }
                self.write(json)
                return
        if date:
            if validators.date(date):
                date = datetime.strptime(date, '%Y-%m-%d')
            elif validators.datetime(date):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            else:
                date = post.created

        # update post
        post.title = title
        post.slug = slug
        if not quick:
            post.content = content
            post.html = wrap_content(content)
            post.format = format
            post.excerpt = excerpt
            post.thumbnail = thumbnail
        post.comment_open = comment_open
        post.updated = datetime.utcnow()
        if date:
            post.created = date
        if type == Post.TYPE_POST:
            post.category_id = category.id
        # create tags
        if not quick and type == Post.TYPE_POST and tags:
            post.tag_ids = self.create_tags(tags.split(','), post.id)
        # commit
        self.db.add(post)
        self.db.commit()
        # delete cache
        keys = ['PostList:1', 'CategoryPostList:%s:1' % post.category_id, 'TagCloud', 'ArchiveHTML']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully modified'),
            'post' : {
                'post' : {
                'id' : post.id,
                'title' : post.title,
                'slug' : post.slug,
                'format' : post.format,
                'excerpt' : post.excerpt,
                'thumbnail' : post.thumbnail,
                'created' : post.created.strftime('%Y-%m-%d %H:%M'),
                'updated' : post.updated.strftime('%Y-%n-%d %H:%M'),
                'views' : post.views,
                'permalink' : post.permalink
            }
            }
        }
        if type == Post.TYPE_POST:
            json['category'] = {
                'id' : category.id,
                'title' : category.title,
                'slug' : category.slug,
                'description' : category.description,
                'permalink' : category.permalink,
                'post_count' : category.post_count
            }
        self.write(json)

    """
    Delete a post
    """
    def delete(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        post = self.get_post_by_id(id)
        if not post:
            json = {
                'error' : 1,
                'msg' : self._('Post not found')
            }
            self.write(json)
            return
        category = post.category
        category.post_count -= 1
        self.db.delete(post)
        self.db.add(category)
        self.db.commit()
        # delete cache
        keys = ['PostList:1', 'CategoryPostList:%s:1' % category_id, 'SystemStatus']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully deleted')
        }
        self.write(json)

class CategoryListApiHandler(ApiHandler):

    """
    List categories
    """
    def get(self):
        json = {}
        p = self.get_argument('p', 1) # current page
        count = self.get_argument('count', 10) # show post count
        try:
            p = int(p)
            count = int(count)
        except:
            p = 1
            count = 10
        offset = (p -1)*count
        categories = Category.query.offset(offset).limit(count).all()
        categories_json = [{
            'id' : category.id,
            'title' : category.title,
            'slug' : category.slug,
            'description' : category.description,
            'permalink' : category.permalink,
            'post_count' : category.post_count
        } for category in categories]
        json = {
            'error' : 0,
            'categories' : categories_json
        }
        self.write(json)

class CategoryApiHandler(ApiHandler, CategoryMixin):

    """
    Get a category info
    """
    def get(self, id):
        json = {}
        category = self.get_category_by_id(id)
        if not category:
            json = {
                'error' : 1,
                'msg' : self._('Category not found')
            }
            self.write(json)
            return
        json = {
            'error' : 0,
            'category' : {
                'id' : category.id,
                'title' : category.title,
                'slug' : category.slug,
                'description' : category.description,
                'permalink' : category.permalink,
                'post_count' : category.post_count
            }
        }
        self.write(json)

    """
    Create a new category
    """
    def post(self):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        title = self.get_argument('title', None)
        slug = self.get_argument('slug', None)
        description = self.get_argument('description', '')
        # valid arguments
        if not title:
            json = {
                'error' : 1,
                'msg' : self._('Title field can not be empty')
            }
            self.write(json)
            return
        if not slug:
            json = {
                'error' : 1,
                'msg' : self._('Slug field can not be empty')
            }
            self.write(json)
            return
        elif self.get_category_by_slug(slug):
            json = {
                'error' : 1,
                'msg' : self._('Slug already exists')
            }
            self.write(json)
            return
        # create category
        category = Category()
        category.title = title
        category.slug = slug
        category.description = description
        self.db.add(category)
        self.db.commit()
        # delete cache
        keys = ['CategoryList', 'SystemStatus']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully created'),
            'category' : {
                'id' : category.id,
                'title' : category.title,
                'slug' : category.slug,
                'description' : category.description,
                'permalink' : category.permalink,
                'post_count' : category.post_count
            }
        }
        self.write(json)

    """
    Modify a category
    """
    def put(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        category = self.get_category_by_id(id)
        if not category:
            json = {
                'error' : 1,
                'msg' : self._('Category not found')
            }
            self.write(json)
            return

        title = self.get_argument('title', None)
        slug = self.get_argument('slug', None)
        description = self.get_argument('description', '')
        # valid arguments
        if not title:
            json = {
                'error' : 1,
                'msg' : self._('Title field can not be empty')
            }
            self.write(json)
            return
        if not slug:
            json = {
                'error' : 1,
                'msg' : self._('Slug field can not be empty')
            }
            self.write(json)
            return
        elif slug != category.slug and self.get_category_by_slug(slug):
            json = {
                'error' : 1,
                'msg' : self._('Slug already exists')
            }
            self.write(json)
            return
        # update category
        category.title = title
        category.slug = slug
        category.description = description
        self.db.add(category)
        self.db.commit()
        # delete cache
        self.cache.delete('CategoryList')

        json = {
            'error' : 0,
            'msg' : self._('Successfully modified'),
            'category' : {
                'id' : category.id,
                'title' : category.title,
                'slug' : category.slug,
                'description' : category.description,
                'permalink' : category.permalink,
                'post_count' : category.post_count
            }
        }
        self.write(json)

    """
    Delete a category
    """
    def delete(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        category = self.get_category_by_id(id)
        if not category:
            json = {
                'error' : 1,
                'msg' : self._('Category not found')
            }
            self.write(json)
            return
        self.db.delete(category)
        self.db.commit()
        # delete cache
        keys = ['CategoryList', 'SystemStatus']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully deleted')
        }
        self.write(json)

class TagListApiHandler(ApiHandler):

    """
    List tags
    """
    def get(self):
        json = {}
        p = self.get_argument('p', 1) # current page
        count = self.get_argument('count', 10) # show post count
        try:
            p = int(p)
            count = int(count)
        except:
            p = 1
            count = 10
        offset = (p -1)*count
        tags = Tag.query.offset(offset).limit(count).all()
        tags_json = [{
            'id' : tag.id,
            'title' : tag.title,
            'slug' : tag.slug,
            'permalink' : tag.permalink,
            'post_count' : tag.post_count
        } for tag in tags]
        json = {
            'error' : 0,
            'tags' : tags_json
        }
        self.write(json)

class TagApiHandler(ApiHandler, TagMixin):

    """
    Get tag info
    """
    def get(self, id):
        json = {}
        tag = self.get_tag_by_id(id)
        if not tag:
            json = {
                'error' : 1,
                'msg' : self._('Tag not found')
            }
            self.write(json)
            return
        json = {
            'error' : 0,
            'tag' : {
                'id' : tag.id,
                'title' : tag.title,
                'slug' : tag.slug,
                'permalink' : tag.permalink,
                'post_count' : tag.post_count
            }
        }
        self.write(json)

    """
    Create a new tag
    """
    def post(self):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        title = self.get_argument('title', None)
        slug = self.get_argument('slug', None)
        # valid arguments
        if not title:
            json = {
                'error' : 1,
                'msg' : self._('Title field can not be empty')
            }
            self.write(json)
            return
        elif self.get_tag_by_title(title):
            json = {
                'error' : 1,
                'msg' : self._('Tag already exists')
            }
            self.write(json)
            return
        if not slug:
            json = {
                'error' : 1,
                'msg' : self._('Slug field can not be empty')
            }
            self.write(json)
            return
        elif self.get_tag_by_slug(slug):
            json = {
                'error' : 1,
                'msg' : self._('Slug already exists')
            }
            self.write(json)
            return
        # create tag
        tag = Tag()
        tag.title = title
        tag.slug = slug
        self.db.add(tag)
        self.db.commit()
        # delete cache
        keys = ['TagCloud', 'SystemStatus']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully created'),
            'tag' : {
                'id' : tag.id,
                'title' : tag.title,
                'slug' : tag.slug,
                'permalink' : tag.permalink,
                'post_count' : tag.post_count
            }
        }
        self.write(json)

    """
    Modify a tag
    """
    def put(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        tag = self.get_tag_by_id(id)
        if not tag:
            json = {
                'error' : 1,
                'msg' : self._('Tag not found')
            }
            self.write(json)
            return

        title = self.get_argument('title', None)
        slug = self.get_argument('slug', None)
        # valid arguments
        if not title:
            json = {
                'error' : 1,
                'msg' : self._('Title field can not be empty')
            }
            self.write(json)
            return
        elif title != tag.title and self.get_tag_by_title(title):
            json = {
                'error' : 1,
                'msg' : self._('Tag already exists')
            }
            self.write(json)
            return
        if not slug:
            json = {
                'error' : 1,
                'msg' : self._('Slug field can not be empty')
            }
            self.write(json)
            return
        elif slug !=tag.slug and self.get_tag_by_slug(slug):
            json = {
                'error' : 1,
                'msg' : self._('Slug already exists')
            }
            self.write(json)
            return
        # update tag
        tag.title = title
        tag.slug = slug
        self.db.add(tag)
        self.db.commit()
        # delete cache
        self.cache.delete('TagCloud')

        json = {
            'error' : 0,
            'msg' : self._('Successfully modified'),
            'tag' : {
                'id' : tag.id,
                'title' : tag.title,
                'slug' : tag.slug,
                'permalink' : tag.permalink,
                'post_count' : tag.post_count
            }
        }
        self.write(json)

    """
    Delete a tag
    """
    def delete(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        tag = self.get_tag_by_id(id)
        if not tag:
            json = {
                'error' : 1,
                'msg' : self._('Tag not found')
            }
            self.write(json)
            return

        self.db.delete(tag)
        self.db.commit()
        # delete cache
        keys = ['TagCloud', 'SystemStatus']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully deleted')
        }
        self.write(json)

class LinkListApiHandler(ApiHandler):

    """
    List links
    """
    def get(self):
        json = {}
        p = self.get_argument('p', 1) # current page
        count = self.get_argument('count', 10) # show post count
        try:
            p = int(p)
            count = int(count)
        except:
            p = 1
            count = 10
        offset = (p -1)*count
        links = Link.query.offset(offset).limit(count).all()
        links_json = [{
            'id' : link.id,
            'title' : link.title,
            'url' : link.url,
            'description' : link.description
        } for link in links]
        json = {
            'error' : 0,
            'links' : links_json
        }
        self.write(json)

class LinkApiHandler(ApiHandler):

    """
    Get link info
    """
    def get(self, id):
        json = {}
        link = self.get_link_by_id(id)
        if not link:
            json = {
                'error' : 1,
                'msg' : self._('Link not found')
            }
            self.write(json)
            return
        json = {
            'error' : 0,
            'link' : {
                'id' : link.id,
                'title' : link.title,
                'url' : link.url,
                'description' : link.description
            }
        }
        self.write(json)

    """
    Create a new link
    """
    def post(self):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        title = self.get_argument('title', None)
        url = self.get_argument('url', None)
        description = self.get_argument('description', '')
        # valid arguments
        if not title:
            json = {
                'error' : 1,
                'msg' : self._('Title field can not be empty')
            }
            self.write(json)
            return
        if not url:
            json = {
                'error' : 1,
                'msg' : self._('URL field can not be empty')
            }
            self.write(json)
            return
        # create link
        link = Link()
        link.title = title
        link.url = url
        link.description = description
        self.db.add(link)
        self.db.commit()
        # delete cache
        keys = ['LinkList', 'SystemStatus']
        self.cache.delete_multi(keys)

        json = {
            'error' : 0,
            'msg' : self._('Successfully created'),
            'link' : {
                'id' : link.id,
                'title' : link.title,
                'url' : link.url,
                'description' : link.description
            }
        }
        self.write(json)

    """
    Modify a link
    """
    def put(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        link = self.get_link_by_id(id)
        if not link:
            json = {
                'error' : 1,
                'msg' : self._('Link not found')
            }
            self.write(json)
            return

        title = self.get_argument('title', None)
        url = self.get_argument('url', None)
        description = self.get_argument('description', '')
        # valid arguments
        if not title:
            json = {
                'error' : 1,
                'msg' : self._('Title field can not be empty')
            }
            self.write(json)
            return
        if not url:
            json = {
                'error' : 1,
                'msg' : self._('URL field can not be empty')
            }
            self.write(json)
            return
        # update link
        link.title = title
        link.url = url
        link.description = description
        self.db.add(link)
        self.db.commit()
        # delete cache
        self.cache.delete('LinkList')

        json = {
            'error' : 0,
            'msg' : self._('Successfully modified'),
            'link' : {
                'id' : link.id,
                'title' : link.title,
                'url' : link.url,
                'description' : link.description
            }
        }
        self.write(json)

    """
    Delete a link
    """
    def delete(self, id):
        json = {}
        if not self.current_user:
            json = {
                'error' : 1,
                'msg' : self._('Access denied')
            }
            self.write(json)
            return

        link = self.get_link_by_id(id)
        if not link:
            json = {
                'error' : 1,
                'msg' : self._('Link not found')
            }
            self.write(json)
            return

        self.db.delete(link)
        self.db.commit()
        # delete cache
        keys = ['LinkList', 'SystemStatus']
        self.cache.delete_multi(keys)
        
        json = {
            'error' : 0,
            'msg' : self._('Successfully deleted')
        }
        self.write(json)

handlers = [
    ('/api/posts', PostListApiHandler),
    ('/api/post', PostApiHandler),
    ('/api/post/(\d+)', PostApiHandler),
    ('/api/categories', CategoryListApiHandler),
    ('/api/category', CategoryApiHandler),
    ('/api/category/(\d+)', CategoryApiHandler),
    ('/api/tags', TagListApiHandler),
    ('/api/tag', TagApiHandler),
    ('/api/tag/(\d+)', TagApiHandler),
    ('/api/links', LinkListApiHandler),
    ('/api/link', LinkApiHandler),
    ('/api/link/(\d+)', LinkApiHandler),
]