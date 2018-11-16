# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: pipelines.py 
Created on 2018/5/8 12:00
"""
import sys

import pymysql
from DBUtils.PooledDB import PooledDB
from pymysql.cursors import DictCursor

from .settings import (DBCHAR, DBHOST, DBNAME, DBPORT, DBPWD, DBUSER,
                       UsError, time)

travel_names = None


class Mysql(object):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self):
        self.getConn()

    def getConn(self):
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = Mysql.__getConn()

    @staticmethod
    def __getConn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if Mysql.__pool is None:
            Mysql.__pool = PooledDB(
                creator=pymysql, mincached=1, maxcached=20,
                host=DBHOST, port=DBPORT,
                user=DBUSER, passwd=DBPWD,
                db=DBNAME, use_unicode=True,
                charset=DBCHAR, cursorclass=DictCursor
            )
        return Mysql.__pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询 sql ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        self._cursor = self._conn.cursor()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = []
        self._cursor.close()
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询 sql ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        self._cursor = self._conn.cursor()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        self._cursor.close()
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询 sql ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        self._cursor = self._conn.cursor()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        self._cursor.close()
        return result

    def insertOne(self, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的 sql 格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        self._cursor = self._conn.cursor()
        self._cursor.execute(sql, value)
        self._cursor.close()
        return self.__getInsertId()

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的 sql 格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        self._cursor = self._conn.cursor()
        count = self._cursor.executemany(sql, values)
        self._cursor.close()
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor = self._conn.cursor()
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        self._cursor.close()
        return result[0]['id']

    def __query(self, sql, param=None):
        self._cursor = self._conn.cursor()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        self._cursor.close()
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql:  sql 格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql:  sql 格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._conn.close()


class UsPipeline(Mysql):
    def __init__(self, *args):
        super().__init__()
        self.cur = self._conn.cursor()

    def selZh(self, aid=None):
        sql = f"SELECT * FROM dc_business_america_info WHERE aid = {aid}"
        self.cur.execute(sql)
        return self.cur.fetchone()

    @property
    def selDBInfo(self):
        '''查询数据库信息
            Returns:
                resPublic: dc_business_america_public_eng 表所有信息
                resInfo: dc_business_america_info_eng 表所有信息
                resWork: dc_business_america_work_eng 表所有信息
        '''
        # 线上使用条件
        sql = "SELECT * FROM dc_business_america_public_eng WHERE status = 2"
        # 测试使用条件
        # sql = "SELECT * FROM dc_business_america_public_eng WHERE aid = 4"
        self.cur.execute(sql)
        resPublic = self.cur.fetchone()
        if not resPublic:
            sql = "SELECT * FROM dc_business_america_public_eng WHERE status = 5"
            self.cur.execute(sql)
            resPublic = self.cur.fetchone()
            if not resPublic:
                # print('无数据')
                return 0

        sql = f"SELECT * FROM dc_business_america_info_eng WHERE aid = {resPublic['aid']}"
        self.cur.execute(sql)
        resInfo = self.cur.fetchone()
        if not resInfo:
            raise UsError('info 表无数据')

        sql = f"SELECT * FROM dc_business_america_work_eng WHERE aid = {resPublic['aid']}"
        self.cur.execute(sql)
        resWork = self.cur.fetchone()
        if not resWork:
            raise UsError('work 表无数据')

        self.data = (resPublic, resInfo, resWork)
        return 1

    def upload(self, aid=None, **kwargs):
        '''修改数据库接口

            参数:
                aid: 公共表 aid (必须)
                status: 状态
                aacode:
        '''
        try:
            assert aid and kwargs
        except:
            raise UsError('未传 aid 或者 aaCode/status 无值')

        apeSql = ', '.join(
            [f'ape.{key}="{val}"' for key, val in kwargs.items()])
        apSql = ', '.join([f'ap.{key}="{val}"' for key, val in kwargs.items()])

        sql = f'''UPDATE dc_business_america_public_eng AS ape, dc_business_america_public AS ap SET {apeSql}, {apSql} WHERE  ape.aid = {aid} AND  ap.aid = {aid}'''
        print(kwargs.get("progress"))
        # sys.exit(1)
        try:
            self.cur.execute(sql)
            self._conn.commit()
        except Exception as e:
            print('数据库执行出错, 进行回滚...')
            self._conn.rollback()
            raise UsError(f"{e}\n{kwargs.get('ques', 'ques is null')}")

    def selDBOrder(self, usql=None):
        """ 预约表查询 """
        sql = "SELECT * FROM dc_business_america_order WHERE interview_status=4 or python_status=1"
        sql = sql if not usql else usql
        # 测试
        sql = "SELECT * FROM dc_business_america_order WHERE id=74"
        self.cur.execute(sql)
        res = self.cur.fetchone()
        if res:
            print(res)
            sql = "SELECT * FROM dc_business_america_public_eng WHERE order_id = %s" % res["id"]
            self.cur.execute(sql)
            resPublics = self.cur.fetchall()
            aids = tuple([i['aid'] for i in resPublics] + [0, 0])
            sql = f"SELECT * FROM dc_business_america_info_eng WHERE aid IN {aids}"
            self.cur.execute(sql)
            resInfos = self.cur.fetchall()
            sql = f"SELECT * FROM dc_business_america_work_eng WHERE aid IN {aids}"
            self.cur.execute(sql)
            resWorks = self.cur.fetchall()
            self.order_data = res, resPublics, resInfos, resWorks
            return 1
        return 0

    def selAppointment(self):
        sql = f"SELECT * FROM dc_business_america_order WHERE interview_status=1"
        # sql = f"SELECT * FROM dc_business_america_order WHERE id=59"
        if self.selDBOrder(sql):
            return 1
        return 0

    def uploadOrder(self, ids=None, **kwargs):
        """ 预约表数据修改/提交 
            interview_status 「2, 3, 4」
            interview_pdf pdf_url_link
            pay_code 付款码
            register_is 1 注册状态
        """
        if not (ids and kwargs):
            raise UsError("数据库修改值不能为空")
        cSql = ', '.join([f"{key}='{val}'" for key, val in kwargs.items()])
        sql = f'UPDATE dc_business_america_order SET {cSql} WHERE id = "{ids}"'
        try:
            self.cur.execute(sql)
            self._conn.commit()
        except Exception as e:
            print('数据库执行出错, 进行回滚...')
            self._conn.rollback()
            raise UsError(e)

    def uploadDays(self, activity, **kwargs):
        """ 更新可预约时间表 """
        if not (activity and kwargs):
            raise UsError("数据库修改值不能为空")
        cSql = ', '.join([f"{key}='{val}'" for key, val in kwargs.items()])
        if kwargs.get("interview_days"):
            cSql += f', utime={int(time())}'
        if kwargs.get("replace_interview_days"):
            cSql += f", replace_utime='{int(time())}'"
        sql = f'UPDATE dc_america_interview_days SET {cSql} WHERE activity="{activity}"'
        try:
            self.cur.execute(sql)
            self._conn.commit()
        except Exception as e:
            print('数据库执行出错, 进行回滚...')
            self._conn.rollback()
            raise UsError(f"{e}\n{activity}")

    def get_group_email(self, mpid):
        sql = "SELECT * FROM dc_business_america_email WHERE mpid=%s"
        return self.getOne(sql, mpid)

    def __del__(self):
        try:
            if self.cur:
                self.cur.close()
            if self._conn:
                self._conn.close()
            
        except:
            pass


if __name__ == "__main__":
    # pass
    u = UsPipeline()
    u.uploadDays(250)
    print(u)
    # u.upload('123', name="bob", xx="daf", asd="adsdf")
