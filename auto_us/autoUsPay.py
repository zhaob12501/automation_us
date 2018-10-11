import re

import requests
from PIL import Image

from .autoUS import AutoUs, Select
from .settings import (APPDAYS, MON, NC, PASSWD, USER, UsError, json, sleep,
                       strftime, time)


class AutoPay(AutoUs):
    """ 
        # =============================================== #
        #  登陆 - 填写信息 - 选择付款方式 - 获取付款号码  #
        # =============================================== #
    """
    id = 0
    def __init__(self, data=None, usPipe=None, noWin=False, noImg=False):
        data_one = tuple([data[i][0] for i in range(1, 4)])
        super().__init__(data=data_one, usPipe=usPipe)
        self.res = data[0]
        self.resPublics = data[1][1:]
        self.resInfos = data[2][1:]
        self.resWorks = data[3][1:]
        self.email = self.resInfo["home_email"]

    def register(self):
        register_id_befor = "Registration:SiteTemplate:theForm"
        self.driver.get("https://cgifederal.secure.force.com/SiteRegister?country=china&language=")
        self.Wait(xpath=f'//*[@id="{register_id_befor}"]/table/tbody/tr[7]/td/label/input')
        sleep(0.5)
        # self.Wait(f"{register_id_befor}:username", "jiu20187745re@163.com")
        # self.Wait(f"{register_id_befor}:firstname", "xiaofang")
        # self.Wait(f"{register_id_befor}:lastname", "kang")
        self.Wait(f"{register_id_befor}:username", self.resInfo["home_email"])
        self.Wait(f"{register_id_befor}:firstname", self.resInfo["english_name_s"])
        self.Wait(f"{register_id_befor}:lastname", self.resInfo["english_name"])
        while self.driver != "https://cgifederal.secure.force.com/applicanthome":
            try:
                result = self.getCaptcha(f"{register_id_befor}:theId")
                self.Wait(f"{register_id_befor}:password", PASSWD)
                self.Wait(f"{register_id_befor}:confirmPassword", PASSWD)
                self.Wait(f"{register_id_befor}:recaptcha_response_field", result)
                sleep(1)
                self.Wait(f"{register_id_befor}:submit")
            except:
                pass
            if "SiteRegister" not in self.driver.current_url: break
            sleep(0.2)
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:j_id14:j_id15:j_id26:j_id27:j_id28"]/select', text="Chinese (Simplified)")
        self.usPipe.uploadOrder(self.res["id"], register_is=1)

    def login(self):
        """ 登陆 """
        # 打开付款网址
        print("打开付款网址")
        self.driver.get(self.payUrl)
        # 输入用户名密码
        print("输入用户名密码")
        self.Wait(
            "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username", self.email)
        sleep(1)
        # 点击同意条款
        print("点击同意条款")
        self.Wait(
            xpath='//*[@id="loginPage:SiteTemplate:siteLogin:loginComponent:loginForm"]/div[2]/div[2]/table/tbody/tr[3]/td/label/input')
        # 验证码识别
        print("验证码识别")
        for _ in range(5):
            try:
                self.Wait(
                    "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password", PASSWD)
                result = self.getCaptcha(
                    "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:theId")
                self.Wait(
                    "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:recaptcha_response_field", result)
                sleep(0.5)
                # 点击登陆
                print("点击登陆")
                self.Wait(
                    "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton")
                if "无法核实验证码。请重新输入。" in self.driver.page_source:
                    continue
                else: break
                sleep(0.1)
            except:
                pass
        sleep(1)
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:j_id14:j_id15:j_id26:j_id27:j_id28"]/select', text="Chinese (Simplified)")

    def payInfo(self):
        """ 付款页面 """
        if self.driver.current_url != "https://cgifederal.secure.force.com/applicanthome":
            self.login()
        xp = '//*[@id="j_id0:SiteTemplate:j_id52:j_id53:j_id54:j_id58"]/a[contains(text(), "新的签证申请")]'
        self.Wait(xpath=xp)
        self.Wait("j_id0:SiteTemplate:theForm:ttip:2")
        for _ in range(5):
            try:
                self.Wait(xpath='/html/body/div[3]/div[3]/div/button/span')
                break
            except:
                self.Wait(
                    xpath='//*[@id="j_id0:SiteTemplate:theForm:ttip"]/tbody/tr[3]/td/label')
                sleep(1)
        # 继续
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:theForm"]/input[3]')
        lq = {
            "BEJ": 0,
            "CHE": 1,
            "GUZ": 2,
            "SHG": 3,
            "SNY": 4,
        }
        self.Wait(
            f"j_id0:SiteTemplate:j_id112:j_id165:{lq[self.resInfo['activity']]}")
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:j_id112"]/input[3]')
        purpose = json.loads(self.resPublic["america_purpose"])[0]
        if self.resInfo["activity"] in ["BEJ", "GUZ", "SHG"]:
            if purpose["one"] == "B":
                self.Wait("j_id0:SiteTemplate:j_id109:j_id162:0")
        elif self.resInfo["activity"] == "CHE":
            if purpose["one"] == "B":
                self.Wait("j_id0:SiteTemplate:j_id109:j_id162:3")
        elif self.resInfo["activity"] == "SNY":
            if purpose["one"] == "B":
                self.Wait("j_id0:SiteTemplate:j_id109:j_id162:0")
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:j_id109"]/input[3]')

        ppDic = {
            "B1-CF": '//*[@id="accordion"]/div[2]/table/tbody/tr[1]/td/input',
            "B1-B2": '//*[@id="accordion"]/div[2]/table/tbody/tr[2]/td/input',
            "B2-TM": '//*[@id="accordion"]/div[2]/table/tbody/tr[3]/td/input',
        }
        self.Wait(xpath=ppDic[purpose["two"]])
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:theForm"]/input[3]')
        try:
            self.Wait(xpath='//*[@id="ui-tooltip-5-content"]/b/button')
        except:
            pass

        try:
            Select(self.driver.find_element_by_xpath('//select')).select_by_index(1)
            self.Wait("AcceptButton")
        except:
            pass

        # 护照
        print("护照")
        try:
            self.Wait(xpath='//*[@id="thePage:SiteTemplate:theForm:j_id182:j_id183:j_id191"]',
                      text=self.resInfo["passport_number"])
            # 拼音名
            print("拼音名")
            self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id783",
                      self.resInfo["english_name_s"])
            # 拼音姓
            print("拼音姓")
            self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id792",
                      self.resInfo["english_name"])
        except:
            pass
        # 护照签发日期
        print("护照签发日期")
        y, m, d = self.resInfo["lssue_date"].split("-")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:issuanceDate",
                  text='/'.join([m, d, y]))
        # 护照失效日期
        print("护照失效日期")
        y, m, d = self.resInfo["expiration_date"].split("-")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:expirationDate",
                  text='/'.join([m, d, y]))
        # 出生日期
        print("出生日期")
        y, m, d = self.resInfo["date_of_birth"].split("-")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:birthdate",
                  text='/'.join([m, d, y]))
        aname = list(self.resInfo["username"])
        name, names = (aname[0], ''.join(aname[1:])) if len(
            aname) <= 3 else (''.join(aname[:2]), ''.join(aname[2:]))
        # 中文名
        print("中文名")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id800", names)
        # 中文姓
        print("中文姓")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id807", name)
        # 性别
        print("性别")
        gender = Select(self.driver.find_element_by_id("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1093"))
        gender.select_by_index(1 if self.resInfo["sex"] == "M" else 2)

        # AAcode
        # self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1107", "AA008BHNQC")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1107",
                  self.resPublic["aacode"])
        # 身份证/护照号码
        print("身份证/护照号码")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1114",
                  self.resInfo["identity_number"] if self.resInfo["identity_number"] else self.resInfo["passport_number"])
        # 电话号码
        print("电话号码")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1139",
                  '+86' + self.resInfo["home_telphone"])
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1146", '+86' +
                  self.resInfo["tel"] if self.resInfo["tel"] else self.resInfo["company_phone"] if self.resInfo["company_phone"] else self.resInfo["home_telphone"])
        # 邮箱
        print("邮箱")
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1153",
                  self.resInfo["home_email"])

        zhInfo = self.usPipe.selZh(self.resPublic["aid"])
        # 中文邮寄地址
        print("中文邮寄地址")
        if zhInfo["mailing_address_is"] == "Y":
            live_address = zhInfo["live_address"]
            city = zhInfo["m_city"]
            province = zhInfo["province"]
            zipCode = zhInfo["zip_code"]
        elif zhInfo["mailing_address_is"] == "N":
            live_address = zhInfo["mailing_address"]
            city = zhInfo["mailing_address_city"]
            province = zhInfo["mailing_address_province"]
            zipCode = zhInfo["mailing_address_zip"]
        self.Wait(
            "thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1168", live_address)
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1175", city)
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1182", province)
        self.Wait("thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1189", zipCode)

        self.driver.save_screenshot("usFile/table.png")
        table = self.driver.find_element("id", "profileTab")
        left, top = table.location['x'], table.location['y']
        right, bottom = left + table.size['width'], top + table.size['height']
        img = Image.open("usFile/table.png")
        img.crop((left, top, right, bottom))
        img.save("usFile/table.png")

        self.Wait(xpath='//*[@id="thePage:SiteTemplate:theForm"]/input[3]')
        try:
            err = self.driver.find_element_by_css_selector('body > div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-resizable').text
            err = '|'.join(err.replace("\nclose","").split("\n")[:3])
            self.res["exist_status"] = 1
            self.usPipe.uploadOrder(self.res["id"], exist_email=err, exist_status=1, interview_status=0)
        except:
            pass

        if self.res["exist_status"] in [1, 3]:
            return

        with open("usFile/table.png", 'rb') as f:
            files = {'file': f.read()}

        url = "https://www.mobtop.com.cn/index.php?s=/Business/Pcapi/insertlogoapi"
        res = requests.post(url, files=files).json()
        self.usPipe.uploadOrder(self.res['id'], interview_img=res)

        if self.resPublic["associate_is"] == "Y" and self.resPublic["associate_tuxedo_is"] == "N":
            relDic = {
                "S": "Spouse",
                "PF": "Father",
                "PM": "Mother",
                "CD": "Daughter",
                "DS": "Son",
            }
            # 同行人个数
            print("同行人个数")
            length = len(self.resPublics)
            # 主要人 的通行人信息
            print("主要人 的通行人信息")
            anr = json.loads(self.resPublic["associate_name_relation"])
            for i in range(length):
                self.Wait(xpath='//*[@id="create-user"]/span')
                # 同行人的 拼音 姓名
                print("同行人的 拼音 姓名")
                anri = {self.resInfos[i]["english_name"],
                        self.resInfos[i]["english_names"]}
                # 取通行人与主要人的关系
                print("取通行人与主要人的关系")
                relation = {"relation": anr[j]["relation"] for j in range(
                    length) if len(set(anr[j].values()) - anri) == 1}.get('relation')
                if not relation:
                    self.errJson([self.resInfos[i]["username"]],
                                 "同行人", status=0)
                    return
                rela = relDic.get(relation, "Other")
                self.Wait(
                    xpath='//*[@id="j_id0:SiteTemplate:showPopUp"]/table/tbody/tr[2]/td[1]/select', text=rela)
                self.Wait("j_id0:SiteTemplate:showPopUp:j_id132",
                          self.resPublics[i]["aacode"])
                self.Wait("j_id0:SiteTemplate:showPopUp:j_id144",
                          self.resInfos[i]["identity_number"])
                self.Wait("j_id0:SiteTemplate:showPopUp:j_id151",
                          self.resInfos[i]["english_names"])
                self.Wait("j_id0:SiteTemplate:showPopUp:j_id159",
                          self.resInfos[i]["english_name"])
                self.choiceSelect("j_id0:SiteTemplate:showPopUp:j_id166",
                                  "Male" if self.resInfo[i]["sex"] else "Female")
                born = self.resInfos[i]["date_of_birth"].split('-')
                born = f"{born[1]}/{born[2]}/{born[0]}"
                self.Wait("dp1537269452886", born)
                aname = list(self.resInfos[i]["username"])
                name, names = (aname[0], ''.join(aname[1:])) if len(
                    aname) <= 3 else (''.join(aname[:2]), ''.join(aname[2:]))
                self.Wait("j_id0:SiteTemplate:showPopUp:j_id184", names)
                self.Wait("j_id0:SiteTemplate:showPopUp:j_id190", name)
                self.Wait("j_id0:SiteTemplate:showPopUp:j_id486",
                          self.resInfos[i]["passport_number"])

                lssue_date = self.resInfos[i]["lssue_date"].split('-')
                lssue_date = f"{lssue_date[1]}/{lssue_date[2]}/{lssue_date[0]}"
                self.Wait("dp1537269452887", lssue_date)

                expiration_date = self.resInfos[i]["expiration_date"].split(
                    '-')
                expiration_date = f"{expiration_date[1]}/{expiration_date[2]}/{expiration_date[0]}"
                self.Wait("dp1537269452888", expiration_date)
                self.Wait(xpath='/html/body/div[3]/div[11]/div/button[1]/span')

        self.Wait("j_id0:SiteTemplate:j_id850:continueBtn")
        # 指定护照/文件送达地址
        print("指定护照/文件送达地址")
        zx = json.loads(self.resPublic["zhongxin"])
        if zx["status"] == "Y":
            self.Wait("thePage:SiteTemplate:theForm:j_id172:0")
            self.Wait(
                xpath='//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[1]', text=NC)
            Select(self.driver.find_element(
                "xpath", '//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[1]')).select_by_value(zx["city"])
            try:
                self.Wait(
                    xpath='//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[2]', text=NC)
                Select(self.driver.find_element(
                    "xpath", '//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[2]')).select_by_value(zx["area"])
                sleep(2)
                self.Wait(
                    xpath='//*[@id="addresses"]/tbody/tr[1]/td[1]/input', text=NC)
                xx = self.driver.find_elements(
                    "xpath", '//*[@id="addresses"]/tbody/tr')
                for i in range(len(xx)):
                    tx = self.driver.find_element(
                        "xpath", f'//*[@id="addresses"]/tbody/tr[{i+1}]/td[2]/strong').text
                    if tx.strip() == zx["address"].strip():
                        self.Wait(xpath=f'//*[@id="addresses"]/tbody/tr[{i+1}]/td/input')
                        break
                self.Wait(
                    xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[3]/td[2]/input')
            except:
                self.Wait(xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[6]/td[2]/input')
        elif zx["status"] == "N":
            self.Wait("thePage:SiteTemplate:theForm:j_id172:1")
            self.Wait(
                xpath='//*[@id="thePage:SiteTemplate:theForm:j_id176"]/table/tbody/tr[1]/td[2]/textarea', text=zx["mail_address"])
            self.Wait(
                xpath='//*[@id="thePage:SiteTemplate:theForm:j_id176"]/table/tbody/tr[2]/td[2]/input', text=zx["mail_city"])
            self.Wait(
                xpath='//*[@id="thePage:SiteTemplate:theForm:j_id176"]/table/tbody/tr[3]/td[2]/input', text=zx["mail_province"])
            self.Wait(
                xpath='//*[@id="thePage:SiteTemplate:theForm:j_id176"]/table/tbody/tr[4]/td[2]/input', text=zx["mail_code"])
            self.Wait(
                xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[3]/td[2]/input')
        # 付款
        print("付款")
        self.Wait(xpath='/html/body/div[2]/div[3]/div/button/span')
        # 借记卡
        print("借记卡")
        if ' USD 160 ' in self.driver.page_source:
            self.usPipe.uploadOrder(self.res["id"], interview_status=2)
            return
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:j_id118"]/table/tbody/tr[2]/td[1]/a')
        while True:
            code = self.driver.find_element("id", "referenceCell").text
            if code:
                self.usPipe.uploadOrder(
                    self.res["id"], interview_status=2, pay_code=code)
                return code

    # 爬取中信取件 市-区-地址
        # ===================================================================================================================================================== #
        # sleep(5)
        # options = etree.HTML(self.driver.page_source).xpath('//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[1]/option')
        # optDic = {}
        # print('爬')
        # try:
        #     for oin, option in enumerate(options[1:]):
        #         pvDic = {}
        #         pv = option.xpath('./text()')[0]
        #         print(pv)
        #         self.Wait(xpath='//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[1]', text=NC)
        #         pvopt = Select(self.driver.find_element_by_xpath('//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[1]'))
        #         pvopt.select_by_index(oin+1)

        #         sleep(2)
        #         citys = etree.HTML(self.driver.page_source).xpath('//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[2]/option')
        #         for ci, city in enumerate(citys[1:]):
        #             ls = []
        #             ct = city.xpath('./text()')[0]
        #             print(f"  {ct}")
        #             self.Wait(xpath='//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[2]', text=NC)
        #             ctopt = Select(self.driver.find_element_by_xpath('//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[2]'))
        #             ctopt.select_by_index(ci+1)

        #             self.Wait(xpath='//*[@id="addresses"]/tbody/tr/td/input')
        #             sleep(1)
        #             trlist = etree.HTML(self.driver.page_source).xpath('//*[@id="addresses"]//tr')
        #             for i, tr in enumerate(trlist):
        #                 tdls = [
        #                     # //*[@id="addresses"]/tbody/tr/td[1]/input
        #                     '\n'.join(tr.xpath("./td[2]//text()")),
        #                     '\n'.join(tr.xpath("./td[3]/text()")),
        #                 ]
        #                 print('    ' + tdls[0])
        #                 ls.append(tdls)
        #             pvDic[ct] = ls
        #         optDic[pv] = pvDic
        # except:
        #     pass

        # with open('addressEMS.json', 'w', encoding="utf8")as f:
        #     json.dump(optDic, f)
        # ===================================================================================================================================================== #

    def getDate(self):
        """ 预约 """
        self.id = self.res["id"]
        try:
            # 点击继续
            self.Wait(
                xpath='//*[@id="j_id0:SiteTemplate:j_id52:j_id53:j_id54:j_id58"]/a[contains(text(), "继续")]')
            jx = 1
        except:
            self.Wait(
                xpath='//*[@id="j_id0:SiteTemplate:j_id52:j_id53:j_id54:j_id58"]/a[contains(text(), "重新预约")]')
            jx = 0

        sleep(2)
        try:
            self.driver.find_element_by_xpath('//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[6]/td[2]/input').click()
            sleep(2)
        except:
            pass
        try:
            self.driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/button/span').click()
        except:
            pass
        if jx:
            try:
                self.Wait(xpath='/html/body/div[2]/div[3]/div/button')
            except:
                pass
            sleep(1)
            try:
                self.driver.find_element_by_xpath(
                    '/html/body/div[4]/div[3]/div/button[1]/span')
            except:
                pass
            try:
                self.Wait("j_id0:SiteTemplate:theForm:continue_btn")
            except:
                self.Wait("")
        sleep(1)
        reg = r"myDayHash\['(.*?)'\] = true;"
        data = re.findall(reg, self.driver.page_source)
        # 返回可预约日期
        self.usPipe.uploadDays(",".join(data), self.resInfo["activity"])
        self.usPipe.uploadOrder(self.res["id"], python_status=0)
        return data

    def appointment(self):
        if self.id != self.res["id"]:
            data = self.getDate()
            self.id = self.res["id"]
        else:
            reg = r"myDayHash\['(.*?)'\] = true;"
            data = re.findall(reg, self.driver.page_source)
        upinfodate = {i: "" for i in data}
        userDate = json.loads(self.res["interview_time"])

        userDate["day"] = userDate["day"].split(",")
        tim = {
            "am": APPDAYS[:5],
            "pm": APPDAYS[-4:],
            "am,pm": APPDAYS
        }

        for day in userDate["day"]:
            if day in data:
                d = f'{day.split("-")[0]:0>2}'
                mo = f'{day.split("-")[1]:0>2}'
                try:
                    Select(self.driver.find_element_by_xpath(
                        '//select')).select_by_index(1)
                except:
                    pass
                while 1:
                    try:
                        self.Wait(xpath=f'//*[@id="datepicker"]/div/div/div/div/span[contains(text(), {MON[mo]})]', text=NC)
                        break
                    except:
                        self.Wait(xpath='//*[@id="datepicker"]/div/div[3]/div/a')

                divs = self.driver.find_elements_by_css_selector('#datepicker > div > div.ui-datepicker-group')
                for div in divs:
                    if div.find_element_by_xpath('./div/div/span').text == MON[mo]:
                        div.find_element_by_xpath(f".//a[contains(text(), {int(d)})]").click()
                        break

                self.Wait(xpath=f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{MON[mo]} {int(d)}")]', text=NC)
                for mi in tim[userDate["t"]]:
                    self.Wait(
                        xpath=f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{mi}")]/preceding-sibling::td[1]/input')
                    s_time = self.driver.find_element_by_xpath(
                        f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{mi}")]').text
                    self.Wait("thePage:SiteTemplate:theForm:addItem")
                    self.Wait(
                        xpath='//*[@id="j_id0:SiteTemplate:j_id107:j_id109"]/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a')
                    self.Wait(
                        xpath='//*[@id="j_id0:SiteTemplate:j_id107:j_id109"]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/a')
                    file = {
                        "file": (
                            "AppointmentConfirmation.pdf",
                            open("./usFile/AppointmentConfirmation.pdf", "rb"),
                            "application/pdf"
                        )
                    }
                    url = "https://www.mobtop.com.cn/index.php?s=/Business/Pcapi/insertlogoapi"
                    res = requests.post(url, files=file).json()
                    success_time = f"{'-'.join([day.split('-')][::-1])} {s_time}"
                    # 存入数据库
                    self.usPipe.uploadOrder(ids=self.res["id"],interview_success=success_time, interview_status="6", interview_pdf=res, interview_num=self.res["interview_num"]-1)
                    print("预约成功")
                    return
                else:
                    upinfodate[day] = "pm" if userDate["t"] == "am" else "am"
        else:
            self.usPipe.uploadOrder(self.res["id"], interview_times=json.dumps(upinfodate) if upinfodate else "", interview_status='5')

    def cancel(self):
        self.login()
        self.Wait(xpath='//a[contains(text(),"取消预约")]')
        self.Wait(xpath='//*[@id="j_id0:SiteTemplate:j_id120"]/table/tbody/tr[14]/td/input[1]')
        print("取消成功")
