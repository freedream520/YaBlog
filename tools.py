#!/usr/bin/env python

import argparse
import config
from tornado.options import options
import app

from lib.util import parse_config_file

def create_db():
    from config import db
    import models
    db.create_db()
    return

def init_project():
    pass

def backup_mysql():
    parse_config_file("/home/messense/config/messense.conf")
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
        if cmd == 'init':
            return init_project()

    if isinstance(args.command, basestring):
        return run_command(args.command)
    if isinstance(args.command, (list, tuple)):
        for cmd in args.command:
            run_command(cmd)


if __name__ == "__main__":
    main()