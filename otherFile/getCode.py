from time import sleep
import pymysql
import requests
import re
errinfo = {}
errcode = []
class Requ:
    req = requests.Session()
    req.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    }
    url = "http://code.mcdvisa.com/save.php?action=getcode&i=1&w=%s"
        
    def __init__(self):
        self.pipe = Pipe()

    def getcode(self):
        global errcode
        nofond = {f"{i:0>4}" for i in range(10000)} - self.pipe.select 
        # for i in range(1, 10000):
        for i in [9986]:
            print(i, " -- ", end="")
            try:
                url = self.url % f"{self.url}{i:0>4}"
                res = self.req.get(url).text
                reg = r'<ul><li>(.*?)：(.*?)</li></ul>'
                codes = re.findall(reg, res)[0]
                print(codes)
                if codes[1] == '未找到': continue
                self.pipe.update(*codes)
            except:
                errcode.append(i)


class Pipe:
    con = pymysql.connect(
        host='60.205.119.77',
        user='mobtop', 
        passwd='CC5t6y7u8iCC',
        db='mobtop', 
        port=3306, 
        charset="utf8",
        # cursorclass=pymysql.cursors.DictCursor
    )

    @property
    def select(self):
        sql = 'SELECT chinese_code FROM dc_chinese_code_list'
        cur = self.con.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        return {i[0] for i in res}

    def update(self, chinese_code, chinese):
        cur = self.con.cursor()
        sql = f"REPLACE INTO dc_chinese_code_list SET chinese_code='{chinese_code}', chinese='{chinese}'"
        try:
            cur.execute(sql)
            self.con.commit()
        except:
            self.con.rollback()
            global errinfo
            errinfo[chinese_code] = chinese
        finally:
            cur.close()

    def __del__(self):
        if hasattr(self, "con"):
            self.con.close()

def main():
    r = Requ()
    r.getcode()
    print('-' * 50)
    print("err")
    print(errinfo)
    print('-' * 50)
    print("errcode")
    print(errcode)
    # p = Pipe()
    # # nofond = {f"{i:0>4}" for i in range(10000)} - p.select 
    # print(len([f"{i:0>4}" for i in range(10000)]))
    # print(len(p.select))

if __name__ == '__main__':
    main()
