#!/usr/bin/env python
# -*-coding:utf-8-*-

from qiniu import Auth, put_file, etag, urlsafe_base64_encode

QINIU_ACCESS_KEY = '0jAQdT6nr4h5M6jj_kqpg9SHY5L64OU9wQ2NJoNs'
QINIU_SECRET_KEY = 'Qttd5PDhmhrOGYrNBUp0tXMBqHkdyw-S9gdXWkYA'
QINIU_BUCKET_NAME = 'avatar'
QINIU_BUCKET_DOMAIN = '7xsgma.com1.z0.glb.clouddn.com'

q = Auth(access_key=QINIU_ACCESS_KEY, secret_key=QINIU_SECRET_KEY)

bucket_name = 'avatar'

key = 'ironMan.jpg'
token = q.upload_token(bucket_name, key, 3600)

print token

localfile = './1.jpg'

ret, info = put_file(token, key, localfile)

print ret
print info
