# -*- coding:utf-8 -*-
import re
import types

def regex(pattern, data, flags=0):
    if isinstance(pattern, basestring):
        pattern = re.compile(pattern, flags)

    return pattern.match(data)


def email(data):
    pattern = r'^.+@[^.].*\.[a-z]{2,10}$'
    return regex(pattern, data, re.IGNORECASE)


def url(data):
    pattern = (
        r'(?i)^((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}'
        r'/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+'
        r'|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))$')
    return regex(pattern, data, re.IGNORECASE)


def username(data):
    pattern = r'^[a-zA-Z0-9]+$'
    return regex(pattern, data)

def password(data):
    for x in data:
        if x > chr(127):
            return False
    return True

def number(data):
    if False == type(data) is types.IntType:
        return str(data).isdigtal()
    return True

def string(data):
    return type(data) is types.StringType

def empty(data):
    if len(data) == 0:
        return True
    return False

def date(data):
    if len(data) == 10:
        rule = '(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)$/'
        match = re.match(rule , data)
        if match:
            return True
        return False
    return False

def telphone(data):
    if data:
        if re.match('^((0\d{2,3})-)(\d{7,8})(-(\d{3,}))?$', data):
            return True
    return False

def mobilephone(data):
    if data:
        if re.match('^(\+\d{2})?1[358]\d{9}$', data):
            return True
    return False

def phone(data):
    if data:
        if  telphone(data) or mobilephone(data):
            return True
    return False
