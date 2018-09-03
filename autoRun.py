# coding: utf-8
"""
@Author: ZhaoBin 
@Date: 2018-08-05 13:30:41 
@Last Modified by:   ZhaoBin 
@Last Modified time: 2018-08-08 17:00:41 
"""
from autoUS import AllPage, Base
from pipelines import UsPipeline
from settings import POOL, UsError, json, sleep, strftime, os, glob


class UsRun:
    '''美国签证自动化录入程序逻辑控制模块
    '''

    def __init__(self):
        self.pool = POOL()
        self.chrome = Base()
        self.driver = self.chrome.driver
        self.control = {
            1: self.fillInfo,
            2: self.lastDone,
            3: self.usPay,
            4: self.appointment,
        }
        self.au = AllPage(usPipe=UsPipeline(pool=self.pool), driver=self.driver)

    def fillInfo(self):
        if self.au.resPublic['aacode']:
            self.au.continueGo()
        else:
            self.au.default

        ans = self.au.run
        with open("all_ url.json", "w+", encoding="utf8") as f:
            json.dump(self.au.allUrl, f)
        if ans:
            return 1
        return 0

    def lastDone(self):
        if self.au.getNode != "":
            self.au.continueGo()
        self.au.signCertify()
        self.au.done()
        self.au.uploadPdf
        print('upload Pdf file over')

    def usPay(self):
        code = self.au.login()
        return code
        # self.au.citicPay('730192030365')

    def appointment(self, data=None):
        self.au.appointment(data)

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
            self.data = self.auto.selDB

            # 判断是否需要申请
            if not self.data:
                print('没有数据, 准备刷新...')
                print(strftime('%m/%d %H:%M:%S'))
                path = '.\\usFile'
                try:
                    for infile in glob.glob(os.path.join(path, '*.pdf') ):  
                        os.remove(infile) 
                except:
                    print('.pdf no del')

                sleep(5)
                continue

            # =======
            # 数据处理
            # =======
            print('\n有数据进行提交\n')
            self.au.resPublic, self.au.resInfo, self.au.resWork = self.data
            self.control[self.au.resPublic["america_visa_status"]]()

            if self.auto:
                del self.auto

    def __del__(self):
        try:
            if self.pool:
                self.pool.close()
        except:
            pass


def main():
    r = UsRun()
    while True:
        try:
            r.run
        except UsError as ue:
            print(ue)
        except Exception as e:
            print(f"other:\n{e}")
        print("sleep 30s")
        sleep(30)


if __name__ == '__main__':
    main()
