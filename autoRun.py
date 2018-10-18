# coding: utf-8
"""
@Author: ZhaoBin 
@Date: 2018-08-05 13:30:41 
@Last Modified by:   ZhaoBin 
@Last Modified time: 2018-08-08 17:00:41 
"""
from time import time

from auto_us import AllPage, UsPipeline
from auto_us.settings import (POOL, UsError, glob, json, os, sleep, strftime,
                              sys)
st = 0


class UsRun:
    '''美国签证自动化录入程序逻辑控制模块
    '''

    def __init__(self):
        self.pool = POOL()
        self.au = AllPage(usPipe=UsPipeline(self.pool))
        self.control = {
            0: self.con0,
            1: self.con1,
            2: self.con2,
        }
        self.urList = [
            "Personal1", "Personal2", "AddressPhone", "PptVisa", "Travel",
            "TravelCompanions", "PreviousUSTravel", "USContact", "Relatives",
            "Spouse", "DeceasedSpouse", "PrevSpouse", "WorkEducation1",
            "WorkEducation2", "WorkEducation3", "SecurityandBackground1",
            "SecurityandBackground2", "SecurityandBackground3",
            "SecurityandBackground4", "SecurityandBackground5", "UploadPhoto",
            "ConfirmPhoto", "ReviewPersonal", "ReviewTravel", "ReviewUSContact",
            "ReviewFamily", "ReviewWorkEducation", "ReviewSecurity",
            "ReviewLocation", "SignCertify"
        ]

    def fillInfo(self):
        if self.au.resPublic['aacode']:
            self.au.continueGo()
        else:
            self.au.default

    def sendInfo(self):
        ans = self.au.run
        with open("all_url.json", "w+", encoding="utf8") as f:
            json.dump(self.au.allUrl, f)
        if ans:
            return 1
        return 0

    def done(self):
        self.au.signCertify()
        self.au.done()
        self.au.uploadPdf
        print('upload Pdf file over')

    def con0(self):
        global st
        st = time()
        if self.au.getNode not in self.urList:
            self.fillInfo()
        self.sendInfo()

    def con1(self):
        # self.fillInfo()
        self.done()

    def con2(self):
        global st
        self.au.renamePdf()
        self.au.uploadPdf
        print('=' * 20, "End time :" + time() - st, '=' * 20, '\n\n')

    @property
    def run(self):
        pool = POOL()
        # ========
        # 开始执行
        # ========
        while True:
            print('\nin run...')
            try:
                self.auto = UsPipeline(pool)
            except:
                if self.auto:
                    del self.auto
                print('数据库连接超时...重连...')
                continue
            print('数据库连接完毕...')

            # 获取数据库信息
            data = self.auto.selDBInfo
            print(f"data: {data}")
            # 判断是否需要申请
            if data:
                # =======
                # 数据处理
                # =======
                print('\n有数据进行提交\n')
                # self.au = AllPage(data=self.auto.data, usPipe=UsPipeline(self.pool))
                self.au.resPublic, self.au.resInfo, self.au.resWork = self.auto.data
                try:
                    self.control[self.au.resPublic["visa_status"]]()
                except Exception as e:
                    print(e)
                    if hasattr(self.au, 'driver'):
                        self.au.driver.quit()
                        self.au.getDriver

                if self.auto:
                    del self.auto
            elif not data:
                print('没有数据, 准备刷新...')
                try:
                    self.au.driver.get(self.au.usUrl)
                except:
                    if hasattr(self.au, 'driver'):
                        self.au.driver.quit()
                #     self.au.getDriver
                print(strftime('%m/%d %H:%M:%S'))
                sleep(5)
                continue


    def __del__(self):
        try:
            if self.pool:
                self.pool.close()
        except:
            pass


def main():
    r = UsRun()
    while True:
        # r.run
        try:
            r.run
        except UsError as ue:
            print("in ue error")
            print(ue)
        except Exception as e:
            print("in e error")
            print(f"other:\n{e}")
            print("sleep 30s")
        sleep(5)


if __name__ == '__main__':
    print(strftime("%Y-%m-%d %H-%M-%S"))
    main()
    # import requests
    # with open("./usFile/AppointmentConfirmation.pdf", "rb") as f:
    #     files = {'file': ("AppointmentConfirmation.pdf", f.read(), "application/pdf")}

    # url = "https://www.mobtop.com.cn/index.php?s=/Business/Pcapi/insertlogoapi"
    # res = requests.post(url, files=files).json()
    # print(res)
