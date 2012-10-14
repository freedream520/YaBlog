#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import config
from tornado.options import options
# import app
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from lib.util import parse_config_file

parse_config_file("/Users/messense/config/messense.conf")


def create_db():
    from lib.database import db
    import models
    db.create_db()
    return


def export():
    from models import Post
    import os
    from os import path
    posts = Post.query.all()
    print("%s posts to be exported." % len(posts))
    if not path.exists('%s/md' % config.PROJDIR):
        os.mkdir("%s/md" % config.PROJDIR)
    for post in posts:
        fname = "%s/md/%s-%s.md" % (config.PROJDIR, post.created.strftime('%Y-%m-%d'), post.slug)
        if post.type == Post.TYPE_POST:
            if not path.exists('%s/md/%s' % (config.PROJDIR, post.category.title)):
                os.mkdir('%s/md/%s' % (config.PROJDIR, post.category.title))
            fname = "%s/md/%s/%s-%s.md" % (config.PROJDIR, post.category.title, post.created.strftime('%Y-%m-%d'), post.slug)
        else:
            fname = "%s/md/%s.md" % (config.PROJDIR, post.slug)
        if not path.exists(fname):
            text = "---\nlayout: %s\n" % post.type
            text += "title: %s\npermalink: %s.html\n" % (post.title, post.slug)
            #text += "date: %s\n" % post.created.strftime("%Y-%m-%d %H:%M:%S")
            if post.type == Post.TYPE_POST:
                text += "category: %s\n" % post.category.title
                text += "tags: [%s]\n" % (post.tags_str)
            text += "---\n\n%s" % post.content
            with open(fname, 'a') as f:
                f.write(text)
            print("%s.md created." % post.slug)
    print("Export finished.")


def backup_mysql():
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.Header import Header
    from datetime import datetime

    receiver = "69504439@qq.com"
    bakdir = "/home/messense/backup"

    mail = smtplib.SMTP(options.mail_host)
    mail.ehlo()
    mail.starttls()
    mail.login(options.mail_username, options.mail_password)

    msg = MIMEMultipart('alternative')
    sqlgz = "%s/messense-%s.sql.gz" % (bakdir, datetime.now().strftime('%Y%m%d'))
    attach = MIMEText(open(sqlgz, 'rb').read(), 'base64', 'utf-8')
    attach['Content-Type'] = 'application/octet-stream'
    attach['Content-Disposition'] = 'attachment;filename=messense-%s.sql.gz' % datetime.now().strftime('%Y%m%d')
    msg.attach(attach)

    msg['Subject'] = Header('MySQL backup - messense.me', 'utf-8')
    msg['From'] = options.mail_from_addr
    msg['To'] = receiver

    mail.sendmail(options.mail_from_addr, receiver, msg.as_string())
    mail.close()


def main():
    parser = argparse.ArgumentParser(
        prog='YaBlog',
        description='YaBlog: Yet another Blog',
    )
    parser.add_argument('command', nargs="*")
    parser.add_argument('-f', '--settings', dest='config')
    args = parser.parse_args()

    """if args.config:
        parse_config_file(args.config)  # config
    else:
        return init_project()"""

    def run_command(cmd):
        if cmd == 'createdb':
            return create_db()
        if cmd == 'export':
            return export()

    if isinstance(args.command, basestring):
        return run_command(args.command)
    if isinstance(args.command, (list, tuple)):
        for cmd in args.command:
            run_command(cmd)


if __name__ == "__main__":
    main()
