# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: pipelines.py 
Created on 2018/5/8 12:00
"""
import pymysql


class UsPipeline():
    def __init__(self):
        self.pre_info= (
            'xia', 'chunhua', '夏春华', 'F', 'M', '08', 'MAR',
            '1974', 'henan', '122112197403082233'
        )
        self.add_phone = (
            'haidian distirct', 'beijing', '15801235888', 'csy518@ucloud.com'
        )
        self.passport_data = (
            'G59897649', 'HENAN', '06', '03', '2012', '05', '03', '2022', 'N'
        )

        self.travel_data = (
            'B'
        )


def us_data():
    u = UsPipeline()
    return (u.pre_info , u.add_phone, u.passport_data)

if __name__ == "__main__":
    pass  