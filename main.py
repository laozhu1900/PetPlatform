#!/usr/bin/env python
# -*-coding:utf-8-*-

from flask import Flask, request, jsonify
import json
from model import User, db, Pet

app = Flask(__name__)

info = {

    'result': 0,
    'msg': "成功",
    'data': 'null'

}


@app.route('/')
def hello_world():
    return jsonify(info)


"""
    用户注册接口
    {
        "phone":"15705213522",
        "password":"123456"
    }  //请求对象
    {
      "result": 0,
      "msg": "成功",
      "data": {
        "username":"",
        "userIcon":"",
        "phone":"15705213522",
        "area":"南京",
        "description":"",
        "auth":true
      }
    }//返回对象(首次注册地区默认为南京，没有的字段传"",不要为null)

    添加: 对用户的注册信息进行判断，如果

"""


@app.route("/register", methods=['POST'])
def login():
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    password = json_data['password']
    u = User.query.filter_by(phone=phone).first()
    if u is not None:
        info['result'] = 1
        info['msg'] = '该手机号已经被注册'
        return jsonify(info)
    else:
        user = User(phone=phone, password=password)
        db.session.add(user)
        db.session.commit()
        info['data'] = {
            "username": "",
            "userIcon": "",
            "phone": phone,
            "area": "南京",
            "description": "",
            "auth": "true"
        }
        return jsonify(info)


"""
    用户登录接口

    {
        "phone":"15705213522",
        "password":"123456"
    }  //请求对象
    {
      "result": 0,
      "msg": "成功",
      "data": {
        "username":"发发呆哟",
        "userIcon":"http://www.95599.cn/jiangsu/intro/jsweixintest/ABCWeJS/dist/static/img/mall/product.png",
        "phone":"15705213522",
        "area":"南京",
        "description":"高甜",
        "auth":true
      }
    }//返回对象（和注册接口的区别在auth可能为false）
"""


@app.route("/login", methods=['POST'])
def login():
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    password = json_data['password']
    u = User.query.filter_by(phone=phone).first()

    if u is None:
        info['result'] = 1
        info['msg'] = '该用户不存在'
        return jsonify(info)
    elif u.password != password:
        info['result'] = 1
        info['msg'] = '用户名或者密码错误'
        return jsonify(info)
    else:
        info["data"] = {
            "username": u.username,
            "userIcon": u.user_icon,
            "phone": u.phone,
            "area": u.area,
            "description": u.description,
            "auth": u.auth
        }
        return jsonify(info)


"""
    用户编辑接口
    {
        "phone":"15705213522",
        "username":"发发呆哟",
        "userIcon":"http://www.95599.cn/jiangsu/intro/jsweixintest/ABCWeJS/dist/static/img/mall/product.png",
        "area":"武汉",
        "description":"我爱哈士奇",
    }  //请求对象
    {
      "result": 0,
      "msg": "成功",
      "data": null
    }//返回对象（和注册接口的区别在auth可能为false）

"""


@app.route("/edit_user", methods=['POST'])
def edit_user():
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    u = User.query.filter_by(phone=phone).first()
    u.username = json_data['username']
    u.user_icon = json_data['userIcon']
    u.area = json_data['area']
    u.description = json_data['description']

    db.session.add(u)
    db.session.commit()
    return jsonify(info)


"""
    "拉黑用户接口"
    {
        "phone":"15705213522",
        "auth":false
    }  //请求对象
    {
      "result": 0,
      "msg": "成功",
      "data": null
    }//返回对象
"""


@app.route("/black_user", methods=['POST'])
def black_user():
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    u = User.query.filter_by(phone=phone).first()
    u.auth = json_data['auth']
    db.session.add(u)
    db.session.commit()
    return jsonify(info)


"""
    修改密码接口
    {
        "phone":"15705213522",
        "oldpwd":"123456",
        "newpwd":"111111"
    }  //请求对象
    {
      "result": 0,
      "msg": "成功",
      "data": null
    }//返回对象

"""


@app.route("/change_password", methods=['POST'])
def change_password():
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    u = User.query.filter_by(phone=phone).first()
    if u.password != json_data['oldpwd']:
        info['result'] = 1
        info['msg'] = '原始密码输入错误'
        return jsonify(info)
    else:
        u.password = json_data['newpwd']
        db.session.add(u)
        db.session.commit()


"""
    查询用户接口
    {
        "phone":"15705213522"
    }  //请求对象
    {
      "result": 0,
      "msg": "成功",
      "data": {
        "username":"发发呆哟",
        "userIcon":"http://www.95599.cn/jiangsu/intro/jsweixintest/ABCWeJS/dist/static/img/mall/product.png",
        "phone":"15705213522",
        "area":"南京",
        "description":"高甜"
    }
}//返回对象
"""


@app.route("/search_user", methods=['POST'])
def search_user():
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    u = User.query.filter_by(phone=phone).first()

    info["data"] = {
        "username": u.username,
        "userIcon": u.user_icon,
        "phone": u.phone,
        "area": u.area,
        "description": u.description,
    }
    return jsonify(info)


"""
    新增宠物接口
    {
        "ImgUrl":"http://www.95599.cn/jiangsu/intro/jsweixintest/ABCWeJS/dist/static/img/mall/product.png",
        "ImgList":["http://XXX","http://XXX","http://XXX"],
        "PetName":"哈士奇",
        "PetType":"狗",
        "PetSex":"0",
        "PetOld":"4",
        "PetSter":"0",
        "PetImmune":"0",
        "PetFeature":["可爱","短毛"],
        "PetDescription":"极品超小体",
        "area":"南京",
        "phone":"15705213522"
    }//请求对象
    {
        "result":0,
        "msg":"成功",
        "data"
    }

"""


@app.route("/add_pet", methods=['POST'])
def add_pet():
    json_data = json.loads(request.get_data())

    # p = Pet


if __name__ == '__main__':
    app.run()
