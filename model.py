#!/usr/bin/env python
# -*-coding:utf-8-*-
import os

import sys
from flask import Flask
from settings import db_settings
from flask_sqlalchemy import SQLAlchemy

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % ( \
    db_settings['user'], db_settings['password'], db_settings['host'], \
    db_settings['port'], db_settings['db_name'])
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

"""

    宠物属性：
        PetCode	宠物唯一键值	201732131
        PetName	宠物名	哈士奇
        PetType	宠物类别	狗
        PetSex	宠物性别(0男1女)	0
        PetOld	宠物年龄	12
        PetSter	是否绝育(0否，1是)	1
        PetImmune	是否免疫（0否，1是）	1
        PetFeature	属性(数组)	["可爱","短毛"]
        PetDescription	宠物描述	极品很可爱
        ImgUrl	宠物缩略图	http://XXXX
        ImgList	宠物详情页轮播图（数组）	["http://XX","http://XX","http://XX"]
"""


class Pet(db.Model):
    __tablename__ = 'pet'
    pet_code = db.Column(db.Integer, primary_key=True, autoincrement=False)
    pet_name = db.Column(db.String(80), default="")
    pet_type = db.Column(db.String(80), default="")
    pet_sex = db.Column(db.Boolean)
    pet_old = db.Column(db.Integer)
    pet_ster = db.Column(db.Boolean)
    pet_immune = db.Column(db.Boolean)
    pet_feature = db.Column(db.Text, default="")
    pet_description = db.Column(db.String(256), default="")
    img_url = db.Column(db.String(256), default="")
    img_list = db.Column(db.Text, default="")
    pet_master_phone = db.Column(db.String(80), default="")
    pet_area = db.Column(db.String(80), default="")

    def __init__(self, **kwargs):
        super(Pet, self).__init__(**kwargs)

    def __repr__(self):
        return '<Pet %r>' % self.pet_name


"""
    用户属性：
        phone	手机号（注册手机号）	15705213522
        password	密码	123456
        userIcon	用户头像	http://XXXXX
        username	用户昵称	Daze
        area	用户所在地	南京
        description	用户自我描述	我们的上天啊
        auth	用户是否为合法用户(true:合法，false:非法)	true
"""


class User(db.Model):
    __tablename__ = 'user'
    phone = db.Column(db.String(80), unique=True, primary_key=True, autoincrement=False)
    username = db.Column(db.String(80), default="")
    password = db.Column(db.String(80), default="")
    user_icon = db.Column(db.String(256), default="")
    area = db.Column(db.String(80), default="南京".encode('utf-8'))
    description = db.Column(db.String(256), default="")
    auth = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %r>' % self.phone


"""
    收藏属性：
        phone	手机号（注册手机号）	15705213522
        PetCode	宠物唯一键值	201732131
"""


class Collection(db.Model):
    __tablename__ = 'collection'
    phone = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=False)
    pet_code = db.Column(db.String(80))

    def __init__(self, **kwargs):
        super(Collection, self).__init__(**kwargs)

    def __repr__(self):
        return '<Collection %r %r>' % self.phone


if __name__ == '__main__':

    db.drop_all()
    db.create_all()
    # u = User(phone='15705313513',password='123123')
    # db.session.add(u)

    # u = User.whoosh_search(u'15705').all()
    # print u
    # db.session.delete(u)
    # db.session.commit()
    # try:
    #     u = User.query.paginate(2, 2)
    #     for i in u.items:
    #         print i.phone
    # except:
    #     print 111

        # u = User.query.all()
