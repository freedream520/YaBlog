# -*- coding:utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Header import Header
from tornado.options import options

class MailClient(object):

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.quit()

    def send(self, to_addr, subject, content, html=False, **kwargs):
        # lazy load mail client
        if not hasattr(self, 'client'):
            self.client = smtplib.SMTP(options.mail_host)
            self.client.ehlo()
            self.client.starttls()
            self.client.login(options.mail_username, options.mail_password)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'UTF-8')
        msg['From'] = options.mail_from_addr
        if isinstance(to_addr, (list, tuple)):
            to_addr = ';'.join(to_addr)
        msg['To'] = to_addr
        for k, v in kwargs:
            msg[k] = v
        msg.attach(MIMEText(content, 'plain', _charset='UTF-8'))
        if html:
            msg.attach(MIMEText(content, 'html', _charset='UTF-8'))
        return self.client.sendmail(options.mail_from_addr, to_addr, msg.as_string())
