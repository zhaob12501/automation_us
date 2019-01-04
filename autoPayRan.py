from auto_us import AutoPay, UsPipeline
from auto_us.settings import os, sleep, strftime


class RunPayInfo:
    """ 填写付款信息 """

    def __init__(self):
        self.data = None

    def register(self):
        self.usPay.register()

    def run(self):
        while True:
            print(f"\n{'#':=<9}#\n# 预约前 #\n{'#':=<9}#")
            self.usPipe = UsPipeline()

            # print('数据库连接完毕...')
            data = self.usPipe.selAppointment()
            if not data:
                if hasattr(self, "usPay"):
                    del self.usPay
                print('没有数据, 等待中...', strftime('%m/%d %H:%M:%S'))
                sleep(5)
                os.system("cls")
                continue

            # =======
            # 数据处理
            # =======

            # 判断是否需要申请
            print('有数据进行提交\n')

            # 获取需要申请的人员信息
            self.usPay = AutoPay(
                data=self.usPipe.order_data, 
                usPipe=self.usPipe,  # noWin=True
            )
            email_info = self.usPipe.get_group_email(
                self.usPipe.order_data[0]["mpid"])
            if not email_info and email_info["status"] != 1:
                if not self.usPay.res["register_is"]:
                    self.register()
                self.usPay.payInfo()
            else:
                self.usPay.groupAppointment()


def main():
    while True:
        # r.run()
        try:
            r = RunPayInfo()
            r.run()
        except Exception as e:
            print("=" * 20)
            print(e)
            if hasattr(r, 'usPay') and hasattr(r.usPay, 'driver'):
                    r.usPay.driver.quit()
            print("=" * 20)
        finally:
            sleep(10)


if __name__ == '__main__':
    main()
