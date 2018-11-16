from queue import Queue
from threading import Lock, Thread

from auto_us import AutoPay, UsPipeline
from auto_us.settings import os, sleep, strftime

# 锁
lock = Lock()
# 抢预约的数据队列
app_datas = Queue(10)
ids = set()


def get_datas():
    global app_datas, ids
    usPipe = UsPipeline()
    while 1:
        if lock.acquire():
            sql = "SELECT id FROM dc_business_america_order WHERE interview_status=%s"
            all_id = usPipe.getAll(sql, 7)
            for i in all_id:
                if app_datas.full():
                    break
                if i["id"] in ids:
                    continue
                print("队列填充中: + ", i["id"])
                ids.add(i["id"])
                app_datas.put(i["id"], timeout=1)
                # sleep(0.1)
            lock.release()


def appointment(name):
    global app_datas, ids
    while 1:
        usPipe = UsPipeline()
        if app_datas.qsize():
            oid = app_datas.get(timeout=1)
            sql = "SELECT * FROM dc_business_america_order WHERE id=%s AND interview_status=7"
            order = usPipe.getOne(sql, oid)
            if not order:
                continue
            print(name, "有数据提交 order表 id:", oid)
            sql = "SELECT * FROM dc_business_america_public_eng WHERE order_id=%s"
            publics = usPipe.getAll(sql, order["id"])
            if not publics:
                continue
            infos = []
            works = []
            for i in publics:
                sql = "SELECT * FROM dc_business_america_info_eng WHERE aid=%s"
                infos.append(usPipe.getOne(sql, i["aid"]))
                sql = "SELECT * FROM dc_business_america_work_eng WHERE aid=%s"
                works.append(usPipe.getOne(sql, i["aid"]))

            autoPay = AutoPay(
                data=[order, publics, infos, works], usPipe=usPipe, noWin=True)
            if autoPay.group_pay_over(1):
                sleep(1)
                print(f"{name} - remove {oid}")
                ids.remove(oid)
        else:
            print(f"\n{name} No Datas ...", strftime("%m-%d %H:%M:%S"))
            sleep(30)


def main():
    producer = Thread(target=get_datas)
    print("开启主线程")
    producer.start()
    lis = ["线程1", "线程2"]
    threads = []
    for i in lis:
        thread = Thread(target=appointment, args=(i,))
        thread.start()
        print("开启", i)
        threads.append(thread)


if __name__ == '__main__':
    main()
