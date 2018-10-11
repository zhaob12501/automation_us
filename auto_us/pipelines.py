# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: pipelines.py 
Created on 2018/5/8 12:00
"""
from .settings import UsError, POOL, time
import sys


class UsPipeline():
    def __init__(self, pool=None):
        if pool:
            self.con = pool.connection()
            self.cur = self.con.cursor()

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
        # 上线使用条件
        sql = "SELECT * FROM dc_business_america_public_eng WHERE status = 2"
        # 测试使用条件
        # sql = "SELECT * FROM dc_business_america_public_eng WHERE aid = 3"
        self.cur.execute(sql)
        resPublic = self.cur.fetchone()
        if not resPublic:
            sql = "SELECT * FROM dc_business_america_public_eng WHERE status = 5"
            self.cur.execute(sql)
            resPublic = self.cur.fetchone()
            if not resPublic:
                print('无数据')
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

        apeSql = ', '.join([f"ape.{key}='{val}'" for key, val in kwargs.items()])
        apSql = ', '.join([f"ap.{key}='{val}'" for key, val in kwargs.items()])

        sql = f'''UPDATE dc_business_america_public_eng AS ape, dc_business_america_public AS ap SET {apeSql}, {apSql} WHERE  ape.aid = {aid} AND  ap.aid = {aid}''' 
        print(repr(sql))
        # sys.exit(1)
        try:
            self.cur.execute(sql) 
            self.con.commit()
        except Exception as e:
            print('数据库执行出错, 进行回滚...')
            self.con.rollback()
            raise UsError(f"{e}\n{kwargs.get('ques', 'ques is null')}")

    def selDBOrder(self, usql=None):
        """ 预约表查询 """
        sql = "SELECT * FROM dc_business_america_order WHERE interview_status=4 or python_status=1"
        sql = sql if not usql else usql
        # sql = "SELECT * FROM dc_business_america_order WHERE id=16"
        self.cur.execute(sql)
        res = self.cur.fetchone()
        print(res)
        if res:
            sql = "SELECT * FROM dc_business_america_public_eng WHERE order_id = %s" % res["id"]
            self.cur.execute(sql)
            resPublics = self.cur.fetchall()
            sql = "SELECT * FROM dc_business_america_info_eng WHERE aid = %s" % resPublics[0]["aid"]
            self.cur.execute(sql)
            resInfos = self.cur.fetchall()
            sql = "SELECT * FROM dc_business_america_work_eng WHERE aid = %s" % resPublics[0]["aid"]
            self.cur.execute(sql)
            resWorks = self.cur.fetchall()
            self.data = res, resPublics, resInfos, resWorks
            return 1
        return 0

    def selAppointment(self):
        # sql = f"SELECT * FROM dc_business_america_order WHERE interview_status=1"
        sql = f"SELECT * FROM dc_business_america_order WHERE id=31"
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
        sql = f"UPDATE dc_business_america_order SET {cSql} WHERE id = {ids}"
        try:
            self.cur.execute(sql) 
            self.con.commit()
        except Exception as e:
            print('数据库执行出错, 进行回滚...')
            self.con.rollback()
            raise UsError(e)
        
    def uploadDays(self, date, country):
        """ 更新可预约时间表 """
        sql = f"UPDATE dc_america_interview_days SET interview_days='{date}', utime='{int(time())}' WHERE activity='{country}'"
        try:
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            print('数据库执行出错, 进行回滚...')
            self.con.rollback()
            raise UsError(f"{e}\n{country}")

    def __del__(self):
        try:
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
        except:
            pass


if __name__ == "__main__":
    u = UsPipeline()
    u.upload('123', name="bob", xx="daf", asd="adsdf")