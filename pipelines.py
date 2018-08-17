# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: pipelines.py 
Created on 2018/5/8 12:00
"""
from settings import UsError, POOL


class UsPipeline():
    def __init__(self, pool=None):
        if pool:
            self.con = pool.connection()
            self.cur = self.con.cursor()

    @property
    def selDB(self):
        '''查询数据库信息
            Returns:
                resPublic: dc_business_america_public_eng 表所有信息
                resInfo: dc_business_america_info_eng 表所有信息
                resWork: dc_business_america_work_eng 表所有信息
        '''
        # 上线使用条件
        # sql = "SELECT * FROM dc_business_america_public_eng WHERE status = 2"
        # 测试使用条件
        sql = "SELECT * FROM dc_business_america_public_eng WHERE aid = 4"
        self.cur.execute(sql)
        resPublic = self.cur.fetchone()
        if not resPublic:
            sql = "SELECT * FROM dc_business_america_public_eng WHERE status = 5"
            self.cur.execute(sql)
            resPublic = self.cur.fetchone()
            if not resPublic:
                print('无数据')
                return (0, 0, 0)

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
        
        return (resPublic, resInfo, resWork)

    def upload(self, aid=None, status=None, ques=None, aacode=None):
        '''修改数据库接口

            参数:
                aid: 公共表 aid (必须)
                status: 状态
                aacode:
        '''
        try:
            assert aid and (aacode or status or ques)
        except:
            raise UsError('未传 aid 或者 aaCode/status 无值')

        mSql = '''
            UPDATE 
                dc_business_america_public_eng, 
                dc_business_america_public 
            SET 
                dc_business_america_public_eng.{0} = '{1}',
                dc_business_america_public.{0} = '{1}'
            WHERE 
                dc_business_america_public_eng.aid = %s AND 
                dc_business_america_public.aid = %s
            ''' % (aid, aid)

        try:
            if aacode:
                sql = mSql.format('aacode', aacode)
                self.cur.execute(sql)   
            if status:
                sql = mSql.format('status', status)
                self.cur.execute(sql)   
            if ques:
                sql = mSql.format('ques', ques)
                self.cur.execute(sql) 

            self.con.commit()
        except Exception as e:
            print('数据库执行出错, 进行回滚...')
            self.con.rollback()
            raise UsError(f"{e}\n{ques}")

    def getData(self):

        self.pre_info = (
            'xia', 'chunhua', '夏春华', 'F', 'M',
            '08', 'MAR', '1974', 'henan', '122112197403082233', 
            'AA0086SCX0'
        )
        self.add_phone = (
            'haidian distirct', 'beijing', '15801235888', 'csy518@icloud.com'
        )
        self.passport_data = (
            'G59897649', 'HENAN', '06', '03', '2012', 
            '05', '03', '2022', 'N'
        )

        self.travel_data = (
            'B', 'B1-B2', '15', '9', '2018', 
            '1', 'W', 'address', 'beijing', 'AL', 
            '12345', 'S'
        )

        self.family_data = (
            'chen', 'xiaoyun', 'N', 'on', 'S', 
            'add1', 'ALABAMA', 'AL', '5555555555',
        )

        self.spouse_data = (
            'CHEN', 'XIAOYUN', '01', 'MAR', '1970', 'H',
        )

        self.new_work_data = (
            'B', 'zhongkeweihui', 'nongdadanlu', 'beijing', '18801235888', 
            '4', '2', '2008', 'To develop a small program that micro letter'
        )

        self.previous_work_data = (
           'zhongkeweihui', 'nongdananlu', 'beijing', '18801235888', 'The general manager',
           '6', '2', '2008', '10', '7',
           '2018', 'to develop a small program that micro letter' 
        )

    def __del__(self):
        try:
            if self.cur:
                self.cur.close()
            if self.con:
                self.con.close()
        except:
            pass

def us_data():
    u = UsPipeline()
    u.getData()
    data = (
        u.pre_info,
        u.add_phone,
        u.passport_data,
        u.travel_data,
        u.family_data,
        u.spouse_data,
        u.new_work_data,
        u.previous_work_data,
    )
    return data


if __name__ == "__main__":
    p = POOL()
    u = UsPipeline(p)
    sql = "SELECT * FROM dc_business_america_public_eng WHERE aid = 2"
    u.cur.execute(sql)
    resPublic = u.cur.fetchone()
    print(resPublic)
