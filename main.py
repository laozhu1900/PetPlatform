#!/usr/bin/env python
# -*-coding:utf-8-*-
import math
import os

from flask import Flask, request, jsonify
import json

from werkzeug.utils import secure_filename

from model import User, db, Pet, Collection
from flask_cors import CORS
import uuid
from settings import *
from qiniu import Auth, put_file, etag, urlsafe_base64_encode

q = Auth(access_key=QINIU_ACCESS_KEY, secret_key=QINIU_SECRET_KEY)
app = Flask(__name__)

CORS(app)


@app.route('/')
def hello_world():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
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
def register():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
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
    上传图片借口
    {
      "result": 0,
      "msg": "成功",
      "data": {
        "imgUrl":"http://www.95599.cn/jiangsu/intro/jsweixintest/ABCWeJS/dist/static/img/mall/product.png"
      }
    }//返回对象（图片绝对地址）
"""


@app.route("/upload_pic", methods=['post'])
def upload_pic():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
    f = request.files['file']

    file_name = secure_filename(f.filename)

    # f = "2.jpg"
    #
    # file_name = "2.jpg"

    token = q.upload_token(bucket_name, file_name, 3600)
    put_file(token, file_name, f)

    info['data'] = "http://"+QINIU_BUCKET_DOMAIN+"/" + file_name

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
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    password = json_data['password']
    u = User.query.filter_by(phone=phone).first()

    if u is None:
        info['result'] = 1
        info['msg'] = '该用户不存在'
        return jsonify(info)
    elif u.password != password.strip():
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
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
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
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
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
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
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
        return jsonify(info)


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
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
    json_data = json.loads(request.get_data())

    phone = json_data['phone']
    u = User.query.filter_by(phone=phone).first()
    if u is not None:

        info["data"] = {
            "username": u.username,
            "userIcon": u.user_icon,
            "phone": u.phone,
            "area": u.area,
            "description": u.description,
        }
        return jsonify(info)
    else:
        info['result'] = 1
        info['msg'] = '用户不存在'
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
        "data":null
    }

"""


@app.route("/add_pet", methods=['POST'])
def add_pet():
    info = {

        'result': 0,
        'msg': "成功",
        'data': 'null'

    }
    json_data = json.loads(request.get_data())
    pet_id = uuid.uuid1()
    img_url = json_data['ImgUrl']
    img_list = ",".join(json_data['ImgList'])
    pet_name = json_data['PetName']
    pet_type = json_data['PetType']
    pet_sex = json_data['PetSex']
    pet_old = json_data['PetOld']
    pet_ster = json_data['PetSter']
    pet_immune = json_data['PetImmune']
    pet_feature = ".".join(json_data['PetFeature'])
    pet_description = json_data['PetDescription']
    area = json_data['area']
    phone = json_data['phone']
    p = Pet(pet_code=pet_id, img_url=img_url, img_list=img_list, pet_name=pet_name, pet_type=pet_type, pet_sex=pet_sex,
            pet_old=pet_old, pet_ster=pet_ster, pet_immune=pet_immune, pet_feature=pet_feature,
            pet_description=pet_description,
            pet_area=area, p_master_phone=phone)
    db.session.add(p)
    db.session.commit()
    return jsonify(info)


"""

    分页展示宠物界面
    {
        "page":"1",
        "num":"8"
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": [
        {
            "PetCode":"2017022801",
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
        },{
            ...
        }
      ]
    }//返回对象
"""


@app.route('/list-pets', methods=['POST'])
def list_pets():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None

    }
    json_data = json.loads(request.get_data())

    page = json_data['page']
    num = json_data['num']

    length = math.ceil(len(Pet.query.all()) * 1.0 / int(num))
    try:
        p = Pet.query.paginate(int(page), int(num), False)
        all_pets = p.items
        info['data'] = []

        for p in all_pets:
            tmp = {
                "PetCode": p.pet_code,
                "ImgUrl": p.img_url,
                "ImgList": p.img_list.split(","),
                "PetName": p.pet_name,
                "PetType": p.pet_type,
                "PetSex": p.pet_sex,
                "PetOld": p.pet_old,
                "PetSter": p.pet_ster,
                "PetImmune": p.pet_immune,
                "PetFeature": p.pet_feature.split(","),
                "PetDescription": p.pet_description,
                "area": p.pet_area,
                "phone": p.pet_master_phone
            }

            info['data'].append(tmp)
        return jsonify(info)

    except:
        info['result'] = 1
        info['msg'] = "超过当前页数，共" + str(length) + "页"
        return jsonify(info)


"""

    根据PetCode获取宠物详情
    {
        "PetCode":"2017022801"
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": {
            "PetCode":"2017022801",
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
        }
    }//返回对象

"""


@app.route("/search-pet", methods=['POST'])
def search_pet():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None
    }

    json_data = json.loads(request.get_data())
    pet_code = json_data['PetCode']

    p = Pet.query.filter_by(pet_code=pet_code).first()
    if p is not None:
        info['data'] = {
            "PetCode": p.pet_code,
            "ImgUrl": p.img_url,
            "ImgList": p.img_list.split(","),
            "PetName": p.pet_name,
            "PetType": p.pet_type,
            "PetSex": p.pet_sex,
            "PetOld": p.pet_old,
            "PetSter": p.pet_ster,
            "PetImmune": p.pet_immune,
            "PetFeature": p.pet_feature.split(","),
            "PetDescription": p.pet_description,
            "area": p.pet_area,
            "phone": p.pet_master_phone,
        }
        return jsonify(info)
    else:
        info['result'] = 1
        info['msg'] = "宠物不存在"
        return jsonify(info)


"""
    删除宠物
    {
        "PetCode":"2017022801"
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": null
    }//返回对象
"""


@app.route("/delete-pet", methods=['post'])
def delete_pet():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None
    }
    json_data = json.loads(request.get_data())

    pet_code = json_data['PetCode']

    p = Pet.query.filter_by(pet_code=pet_code)

    db.session.delete(p)
    db.session.commit()
    return jsonify(info)


"""
    根据phone查询宠物列表
    {
        "phone":"15705213722",
        "page":"1",
        "num":"8"
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": [
        {
            "PetCode":"2017022801",
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
        },{
            ...
        }
      ]
    }//返回对象

"""


@app.route("/search_pet_by_phone", methods=['post'])
def search_pet_by_phone():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None
    }

    json_data = json.loads(request.get_data())
    phone = json_data['phone']
    page = json_data['page']
    num = json_data['num']

    p_all = Pet.query.filter_by(phone=phone).all()

    if len(p_all) is not 0:
        length = math.ceil(len(p_all) * 1.0 / int(num))
        try:
            p = Pet.query.paginate(int(page), int(num), False)
            all_pets = p.items
            info['data'] = []

            for p in all_pets:
                tmp = {
                    "PetCode": p.pet_code,
                    "ImgUrl": p.img_url,
                    "ImgList": p.img_list.split(","),
                    "PetName": p.pet_name,
                    "PetType": p.pet_type,
                    "PetSex": p.pet_sex,
                    "PetOld": p.pet_old,
                    "PetSter": p.pet_ster,
                    "PetImmune": p.pet_immune,
                    "PetFeature": p.pet_feature.split(","),
                    "PetDescription": p.pet_description,
                    "area": p.pet_area,
                    "phone": p.pet_master_phone
                }

                info['data'].append(tmp)
            return jsonify(info)

        except:
            info['result'] = 1
            info['msg'] = "超过当前页数，共" + str(length) + "页"
            return jsonify(info)
    else:
        info['result'] = 1
        info['msg'] = "该用户没有宠物"
        return jsonify(info)


"""
    根据宠物名或者宠物类型模糊搜索
    {
        "word":"哈士奇"
        "page":"1",
        "num":"8"
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": [
        {
            "PetCode":"2017022801",
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
        },{
            ...
        }
      ]
    }//返回对象
"""


@app.route("/search_pet_vague", methods=['post'])
def search_pet_vague():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None
    }

    json_data = json.loads(request.get_data())
    word = json_data['word']
    page = json_data['page']
    num = json_data['num']

    all_by_name = Pet.query.filter(Pet.pet_name.like('%' + word + '%'))
    all_by_type = Pet.query.filter(Pet.pet_name.like('%' + word + '%'))
    p_all = all_by_name + all_by_type

    if len(p_all) is not 0:
        length = math.ceil(len(p_all) * 1.0 / int(num))
        try:
            p = Pet.query.paginate(int(page), int(num), False)
            all_pets = p.items
            info['data'] = []

            for p in all_pets:
                tmp = {
                    "PetCode": p.pet_code,
                    "ImgUrl": p.img_url,
                    "ImgList": p.img_list.split(","),
                    "PetName": p.pet_name,
                    "PetType": p.pet_type,
                    "PetSex": p.pet_sex,
                    "PetOld": p.pet_old,
                    "PetSter": p.pet_ster,
                    "PetImmune": p.pet_immune,
                    "PetFeature": p.pet_feature.split(","),
                    "PetDescription": p.pet_description,
                    "area": p.pet_area,
                    "phone": p.pet_master_phone
                }

                info['data'].append(tmp)
            return jsonify(info)

        except:
            info['result'] = 1
            info['msg'] = "超过当前页数，共" + str(length) + "页"
            return jsonify(info)
    else:
        info['result'] = 1
        info['msg'] = "没有符合条件的宠物"
        return jsonify(info)


"""
    查询我收藏的宠物列表（不做分页，需要连表查询）
    {
        "phone":"15705213522"
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": [
        {
            "PetCode":"2017022801",
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
            "phone":"13567787654"
        },{
            ...
        }
      ]
    }//返回对象

"""


@app.route("/search_star_pets", methods=['post'])
def search_star_pets():
    info = {

        'result': 0,
        'msg': "成功",
        'data': None
    }

    json_data = json.loads(request.get_data())
    phone = json_data['phone']

    all_pets_code = Collection.query.filter_by(phone=phone).all()

    if len(all_pets_code) is not 0:
        all_pets = []

        for i in all_pets:
            all_pets.append(Pet.query.filter_by(pet_code=i.pet_code).first())

        info['data'] = []

        for p in all_pets:
            tmp = {
                "PetCode": p.pet_code,
                "ImgUrl": p.img_url,
                "ImgList": p.img_list.split(","),
                "PetName": p.pet_name,
                "PetType": p.pet_type,
                "PetSex": p.pet_sex,
                "PetOld": p.pet_old,
                "PetSter": p.pet_ster,
                "PetImmune": p.pet_immune,
                "PetFeature": p.pet_feature.split(","),
                "PetDescription": p.pet_description,
                "area": p.pet_area,
                "phone": p.pet_master_phone
            }

            info['data'].append(tmp)
        return jsonify(info)

    else:
        info['result'] = 1
        info['msg'] = '该用户没有收藏的宠物'
        return jsonify(info)


"""
    收藏宠物
    {
        "phone":"15705213522",
        "PetCode":"2017022801",
        "star":true
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": null
    }//返回对象
"""


@app.route("/pet-star", methods=['post'])
def pet_star():
    info = {
        'result': 0,
        'msg': "成功",
        'data': None
    }
    json_data = json.loads(request.get_data())
    phone = json_data['phone']
    pet_code = json_data['PetCode']
    star = json_data['star']

    if star is "true":
        c = Collection(phone=phone, pet_code=pet_code)
        db.session.add(c)

    else:
        c = Collection(phone=phone, pet_code=pet_code)
        db.session.delete(c)

    db.session.commit()
    return jsonify(info)


"""
    查询某个宠物是否被自己收藏
    {
        "phone":"15705213522",
        "PetCode":"2017022801"
    }  //请求对象

    {
      "result": 0,
      "msg": "成功",
      "data": null
    }//返回对象
"""


@app.route('/pet-is-star', methods=['post'])
def pet_is_star():
    info = {
        'result': 0,
        'msg': "成功",
        'data': None
    }
    json_data = json.loads(request.get_data())
    phone = json_data['phone']
    pet_code = json_data['PetCode']
    c = Collection.query.filter_by(phone=phone, pet_code=pet_code).first()

    if c is not None:
        return jsonify(info)

    else:
        u = User.query.filter_by(phone=phone).first()
        info['result'] = 1
        info['msg'] = '该宠物没有被' + u.username + '收藏'
        return jsonify(info)


if __name__ == '__main__':
    app.run()
