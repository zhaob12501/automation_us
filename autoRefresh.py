from auto_us import AutoPay, UsPipeline
from auto_us.settings import os, sleep, strftime


class RunAppointment:
    """ 预约 """

    def __init__(self):
        self.data = None
        self.id = ''

    def run(self):
        while True:
            os.system("cls")
            print(f"\n{'#':=<7}#\n# 预约 #\n{'#':=<7}#")
            try:
                self.usPipe = UsPipeline()
            except Exception:
                print('数据库连接超时...重连...')
                continue
            # print('数据库连接完毕...')
            data = self.usPipe.selDBOrder()
            if data:
                # =======
                # 数据处理
                # =======

                # 判断是否需要申请
                print('有数据进行提交\n')

                # 获取需要申请的人员信息
                self.usPay = AutoPay(
                    data=self.usPipe.order_data, usPipe=self.usPipe, noWin=False)
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
            else:
                print('没有数据, 等待中...', strftime('%m/%d %H:%M:%S'))
            if hasattr(self, 'usPay') and hasattr(self.usPay, 'driver'):
                self.usPay.driver.quit()
                del self.usPay
            sleep(5)


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
    # sleep(60)
    main()
