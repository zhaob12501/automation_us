from auto_us import AutoPay, UsPipeline
from auto_us.settings import POOL, os, sleep, strftime


class RunAppointment:
    """ 预约 """

    def __init__(self):
        self.pool = POOL()
        self.data = None
        self.id = ''

    def __del__(self):
        del self.usPipe
        self.pool.close()

    def run(self):
        while True:
            print(f"\n{'#':=<7}#\n# 预约 #\n{'#':=<7}#")
            try:
                self.usPipe = UsPipeline(self.pool)
            except:
                print('数据库连接超时...重连...')
                continue
            # print('数据库连接完毕...')
            data = self.usPipe.selDBOrder()
            if not data:
                if hasattr(self, "usPay"):
                    del self.usPay
                print('没有数据, 等待中...', strftime('%m/%d %H:%M:%S'))
                sleep(5)
                continue

            # =======
            # 数据处理
            # =======

            # 判断是否需要申请
            print('有数据进行提交\n')

            # 获取需要申请的人员信息
            self.usPay = AutoPay(
                data=self.usPipe.order_data, usPipe=self.usPipe)
            email_info = self.usPipe.get_group_email(
                self.usPipe.order_data[0]["mpid"])
            if email_info["status"] != 1:
                if self.id != self.usPay.res["id"]:
                    self.id = self.usPay.res["id"]
                    self.usPay.login()
                if self.usPay.res["python_status"] == 1 or self.usPay.res["interview_status"] == 4:
                    self.usPay.getDate()
                if self.usPay.res["interview_status"] == 4:
                    self.usPay.appointment()
                elif self.usPay.res["interview_status"] == 9:
                    self.usPay.cancel()
            else:
                self.usPay.group_pay_over()


def main():
    while True:
        try:
            r = RunAppointment()
            r.run()
        except Exception as e:
            if hasattr(r, 'usPay') and hasattr(r.usPay, 'driver'):
                r.usPay.driver.quit()
            print("====")
            print(e)
            print("====")
        finally:
            sleep(10)


if __name__ == '__main__':
    main()
