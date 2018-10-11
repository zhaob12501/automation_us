# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: settings.py 
Created on 2018/5/5 16:44
"""
import glob
import json
import os
import sys
from time import sleep, strftime, time

import pymysql
from DBUtils.PooledDB import PooledDB


try:
    with open("veri.json") as f: pass
except:
    with open("veri.json", "w") as f: pass

NC = 'noClick'

# BASEDIR = "F:\\usFile"
BASEDIR = os.path.dirname(os.path.dirname(__file__))
LogDir = ".\\us_log"
if not os.path.isdir(BASEDIR):
    os.mkdir(BASEDIR)
if not os.path.isdir(LogDir):
    os.mkdir(LogDir)


USER = "csy518@icloud.com"
USERPHOTO = "18801235888"
USERDB = "mobtop"
PASSWD = "5678tyui"
MONTH = {
    "01": "JAN",
    "02": "FEB",
    "03": "MAR",
    "04": "APR",
    "05": "MAY",
    "06": "JUN",
    "07": "JUL",
    "08": "AUG",
    "09": "SEP",
    "10": "OCT",
    "11": "NOV",
    "12": "DEC",
}
MON = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}

APPDAYS = ["07", "08", "09", "10", "11", "13", "14", "15", "16"]

def POOL():
    return PooledDB(
        pymysql,
        mincached=1,
        host='60.205.119.77',
        user=USERDB,
        passwd='CC5t6y7u8iCC',
        db=USERDB,
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8"
    )


class UsError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)  # 初始化父类
        self.errorinfo = ErrorInfo
        self._log()

    def _log(self):
        with open(f'us_log/{strftime("%Y%m%d")}.log', 'a', encoding='utf8') as f:
            text = f"{strftime('%Y-%m-%d %H:%M:%S')}\t" + \
                self.errorinfo + '\n\n'
            f.write(text)

    def __str__(self):
        return self.errorinfo


""" 
北京: "j_id0:SiteTemplate:j_id112:j_id165:0"
	商务: "j_id0:SiteTemplate:j_id109:j_id162:0"
	学生和访问学者: "j_id0:SiteTemplate:j_id109:j_id162:1"
	L签证: "j_id0:SiteTemplate:j_id109:j_id162:2"
	短期工作签证(Petition based H/LO/P/Q):
		"j_id0:SiteTemplate:j_id109:j_id162:3"

成都: "j_id0:SiteTemplate:j_id112:j_id165:1"
	短期工作签证(H/O/P/Q): "j_id0:SiteTemplate:j_id109:j_id162:0"
	学生/访问学者(F/M/J): "j_id0:SiteTemplate:j_id109:j_id162:1"
	L签证: "j_id0:SiteTemplate:j_id109:j_id162:2"
	其它类型签证: "j_id0:SiteTemplate:j_id109:j_id162:3"
		商务/旅游签证(B1/B2)
		过境/船员和机组人员签证(C1/D)

广州: "j_id0:SiteTemplate:j_id112:j_id165:2"
	同北京

上海: "j_id0:SiteTemplate:j_id112:j_id165:3"
	同北京

沈阳: "j_id0:SiteTemplate:j_id112:j_id165:4"
	其它类型签证: "j_id0:SiteTemplate:j_id109:j_id162:0"
	学生/访问学者(F/M/J): "j_id0:SiteTemplate:j_id109:j_id162:1"
	短期工作签证(H/O/P/Q): "j_id0:SiteTemplate:j_id109:j_id162:2"
	L签证: "j_id0:SiteTemplate:j_id109:j_id162:3"
"""


""" interview_status    预约状态 0:无AA码 1:获取付款码 2: 付款完成 3:预约 4:预约失败 5: 预约成功 """
