# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: yunsu.py
Created on 2018/5/5 16:05
"""
# !/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib, os, urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, json
from datetime import datetime
import operator
import requests

from .settings import USERDB, PASSWD


class APIClient(object):
    def http_request(self, url, paramDict):
        response = requests.post(url, data=paramDict, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        return response.text

    def http_upload_image(self, url, paramKeys, paramDict, filebytes):
        timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        boundary = '------------' + hashlib.md5(timestr.encode('utf8')).hexdigest().lower()
        boundarystr = '\r\n--%s\r\n' % (boundary)

        bs = b''
        for key in paramKeys:
            bs = bs + boundarystr.encode('ascii')
            param = "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s" % (key, paramDict[key])
            # print param
            bs = bs + param.encode('utf8')
        bs = bs + boundarystr.encode('ascii')

        header = 'Content-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/gif\r\n\r\n' % (
        'sample')
        bs = bs + header.encode('utf8')

        bs = bs + filebytes
        tailer = '\r\n--%s--\r\n' % (boundary)
        bs = bs + tailer.encode('ascii')

        import requests
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
                   'Connection': 'Keep-Alive',
                   'Expect': '100-continue',
                   }
        response = requests.post(url, params='', data=bs, headers=headers)
        return response.text


def arguments_to_dict(args):
    argDict = {}
    if args is None:
        return argDict

    count = len(args)
    if count <= 1:
        print('exit:need arguments.')
        return argDict

    for i in [1, count - 1]:
        pair = args[i].split('=')
        if len(pair) < 2:
            continue
        else:
            argDict[pair[0]] = pair[1]

    return argDict


def upload(typeid=3000):
    client = APIClient()
    paramDict = {}
    result = ''
    while 1:
        paramDict['username'] = USERDB
        paramDict['password'] = PASSWD
        paramDict['typeid'] = typeid
        paramDict['timeout'] = 90
        paramDict['softid'] = '72395'
        paramDict['softkey'] = 'd9c016640d33412ca0dacd23a0091f5c'
        paramKeys = ['username',
                     'password',
                     'typeid',
                     'timeout',
                     'softid',
                     'softkey'
                     ]
        from PIL import Image
        imagePath = 'code.png'
        img = Image.open(imagePath)
        if img is None:
            print('get file error!')
            continue
        img.save("upload.gif", format="gif")
        filebytes = open("upload.gif", "rb").read()
        result = client.http_upload_image("http://api.ysdm.net/create.xml", paramKeys, paramDict, filebytes)
        result = result.split('<Result>')[1].split('</Result>')[0]
        os.remove('upload.gif')
        data = {'type': '3', 'num': f'{len(result) * 2.5}'}
        requests.post("http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/useInterface", data=data)
        return result
