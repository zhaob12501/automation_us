# coding: utf-8
"""
@Author: ZhaoBin 
@Date: 2018-08-05 13:30:41 
@Last Modified by:   ZhaoBin 
@Last Modified time: 2018-08-08 17:00:41 
"""
from autoUS import AutoUs
from pipelines import UsPipeline
from settings import POOL, sleep, UsError


class Run:
    '''美国签证自动化录入程序逻辑控制模块
    '''

    def __init__(self):
        self.pool = POOL()

    @property
    def getData(self):
        up = UsPipeline(pool=self.pool)
        alldata = up.selDB
        del up
        return alldata

    @property
    def run(self):
        resPublic, resInfo, resWork = self.getData
        if resPublic:
            au = AutoUs(resPublic=resPublic, resInfo=resInfo,
                        resWork=resWork, usPipe=UsPipeline(pool=self.pool))
            if resPublic['aacode']:
                au.continueGo()
            else:
                au.default
            au.run
            sleep(1200)

    def __del__(self):
        try:
            if self.pool:
                self.pool.close()
        except:
            pass


def main():
    r = Run()
    r.run


if __name__ == '__main__':
    main()
	# Unable to read image memory into DibImage.