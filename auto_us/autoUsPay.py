import re

import requests
from PIL import Image

from .autoUS import EC, AutoUs, Select, WebDriverWait, webdriver
from .fateadm import Captcha
from .settings import (APPDAYS, MON, MON_ANTI, NC, PASSWD, USER, UsError, json,
                       mktime, sleep, strftime, strptime, time)


class AutoPay(AutoUs):
    """ 
        # =============================================== #
        #  登陆 - 填写信息 - 选择付款方式 - 获取付款号码  #
        # =============================================== #
    """
    id = 0

    def __init__(self, data=None, usPipe=None, noWin=False, noImg=False):
        self.all_data = data
        data_one = tuple([data[i][0] for i in range(1, 4)]) if data else None
        super().__init__(data=data_one, usPipe=usPipe, noWin=noWin)
        if data:
            self.res = data[0]
            self.resPublics = data[1][1:]
            self.resInfos = data[2][1:]
            self.resWorks = data[3][1:]
            self.email = self.resInfo["home_email"]
            self.group_email_info = self.usPipe.get_group_email(
                self.res["mpid"])

    def register(self):
        register_id_befor = "Registration:SiteTemplate:theForm"
        self.driver.get(
            "https://cgifederal.secure.force.com/SiteRegister?country=china&language=")
        self.Wait(
            xpath=f'//*[@id="{register_id_befor}"]/table/tbody/tr[7]/td/label/input')
        sleep(0.5)
        # self.Wait(f"{register_id_befor}:username", "ming62401suan@163.com")
        # self.Wait(f"{register_id_befor}:firstname", "xiaofang")
        # self.Wait(f"{register_id_befor}:lastname", "kang")
        self.Wait(f"{register_id_befor}:username", self.resInfo["home_email"])
        self.Wait(f"{register_id_befor}:firstname",
                  self.resInfo["english_name_s"])
        self.Wait(f"{register_id_befor}:lastname",
                  self.resInfo["english_name"])
        for _ in range(5):
            try:
                self.Wait(f"{register_id_befor}:password", PASSWD)
                self.Wait(f"{register_id_befor}:confirmPassword", PASSWD)
                # result = self.getCaptcha(f"{register_id_befor}:theId")
                # self.Wait(f"{register_id_befor}:recaptcha_response_field", result)
                rsp = self.getCaptcha(f"{register_id_befor}:theId", pred_type="20500")
                self.Wait(f"{register_id_befor}:recaptcha_response_field", rsp.pred_rsp.value)
                sleep(1)
                self.Wait(f"{register_id_befor}:submit")
            except:
                pass
            if "SiteRegister" not in self.driver.current_url:
                break
            sleep(2)
            if self.driver != "https://cgifederal.secure.force.com/applicanthome":
                break
            if "无法核实验证码。请重新输入。" in self.driver.page_source:
                    Captcha(4, rsp=rsp)
                    continue
        else:
            print("验证码 5 次错误, 重启")
            return 1
            
        Select(self.Wait(xpath='//select', text=NC)).select_by_index(1)
        self.usPipe.uploadOrder(self.res["id"], register_is=1)

    def login(self, pwd=PASSWD):
        """ 登陆 """
        # 打开付款网址
        print("打开付款网址")
        self.driver.get(self.payUrl)
        # 输入用户名密码
        print("输入用户名密码")
        # self.Wait("loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username", "janice.fu@lettours.com")
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
                # self.Wait("loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password", "janice522")
                self.Wait("loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password", pwd)
                # result = self.getCaptcha("loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:theId")
                # result = result.replace("1", "l")
                rsp = self.getCaptcha("loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:theId", pred_type="20500")
                self.Wait("loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:recaptcha_response_field", rsp.pred_rsp.value)
                sleep(0.5)
                # 点击登陆
                print("点击登陆")
                self.Wait("loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton")
                if "无法核实验证码。请重新输入。" in self.driver.page_source:
                    Captcha(4, rsp=rsp)
                    continue
                elif "确保用户名和密码正确" in self.driver.page_source:
                    self.usPipe.uploadOrder(
                        self.res["id"], ques="邮箱用户名或密码不正确", interview_status="0")
                    return 1
                else:
                    break
                sleep(0.1)
            except:
                pass
        sleep(1)
        # Select(self.driver.find_element("xpath", "//select")).select_by_index(1)
        Select(self.Wait(xpath='//select', text=NC)).select_by_index(1)

    def payInfo(self):
        """ 付款页面 """
        if self.driver.current_url != "https://cgifederal.secure.force.com/applicanthome":
            if self.login():
                return 1
        xp = '//*[@id="j_id0:SiteTemplate:j_id52:j_id53:j_id54:j_id58"]/a[contains(text(), "新的签证申请")]'
        self.Wait(xpath=xp)
        self.Wait("j_id0:SiteTemplate:theForm:ttip:2")
        for _ in range(5):
            try:
                wait = WebDriverWait(self.driver, 2, 0.1)
                locator = ("xpath", '/html/body/div[3]/div[3]/div/button/span')
                wait.until(EC.presence_of_element_located(locator)).click()
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
            wait = WebDriverWait(self.driver, 2, 0.1)
            locator = ("xpath", '//*[@id="ui-tooltip-5-content"]/b/button')
            wait.until(EC.presence_of_element_located(locator)).click()
        except:
            pass

        try:
            self.Wait("AcceptButton")
            self.Wait(xpath='//select', text=NC)
            Select(self.driver.find_element_by_xpath(
                '//select')).select_by_index(1)
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
        gender = Select(self.driver.find_element_by_id(
            "thePage:SiteTemplate:theForm:j_id182:j_id183:j_id1093"))
        gender.select_by_value(
            "Male" if self.resInfo["sex"] == "M" else "Female")

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
            sleep(3)
            err = self.driver.find_element_by_css_selector(
                'body > div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-resizable').text
            # if self.res["exist_status"] == 2:
            #     self.Wait(xpath='/html/body/div[3]/div[11]/div/button[1]/span')
            #     self.Wait(xpath='//*[@id="thePage:SiteTemplate:theForm"]/input[3]')
            #     self.Wait(xpath='//*[@id="j_id0:SiteTemplate:j_id113:j_id114"]/div/div/strong', text=NC)
            #     text = self.driver.find_element('xpath', '//*[@id="j_id0:SiteTemplate:j_id113:j_id114"]/div/div/strong').text
            #     textlist = f"警告:{text}"
            #     self.usPipe.uploadOrder(self.res['id'], interview_img=textlist)
            #     return
            # else:
            err = '|'.join(err.replace("\nclose", "").split("\n")[:3])
            self.usPipe.uploadOrder(
                self.res["id"], exist_email=err, exist_status=1, interview_status=0)
            return 0
        except:
            pass
        with open("usFile/table.png", 'rb') as f:
            files = {'file': f.read()}

        url = "https://www.mobtop.com.cn/index.php?s=/Business/Pcapi/insertlogoapi"
        res = requests.post(url, files=files).json()
        self.usPipe.uploadOrder(self.res['id'], interview_img=res)

        if self.resPublic["associate_is"] == "Y" and self.resPublic["associate_tuxedo_is"] == "N":
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
                self.Wait(
                    xpath='//*[@id="j_id0:SiteTemplate:showPopUp"]/table/tbody/tr[2]/td[1]/select', text="Other")
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
                        self.Wait(
                            xpath=f'//*[@id="addresses"]/tbody/tr[{i+1}]/td/input')
                        break
                self.Wait(
                    xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[3]/td[2]/input')
            except:
                self.Wait(
                    xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[6]/td[2]/input')
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
        self.Wait(
            xpath='//*[@id="j_id0:SiteTemplate:j_id118"]/table/tbody/tr[2]/td[1]/a')
        while True:
            code = self.driver.find_element("id", "referenceCell").text
            if code:
                self.usPipe.uploadOrder(
                    self.res["id"], interview_status=2, pay_code=code)
                return code

    def getDate(self):
        """ 预约 """
        self.id = self.res["id"]
        try:
            # 点击继续
            wait = WebDriverWait(self.driver, 2, 0.1)
            locator = (
                "xpath", '//*[@id="j_id0:SiteTemplate:j_id52:j_id53:j_id54:j_id58"]/a[contains(text(), "继续")]')
            wait.until(EC.presence_of_element_located(locator)).click()
            jx = 1
        except:
            self.Wait(
                xpath='//*[@id="j_id0:SiteTemplate:j_id52:j_id53:j_id54:j_id58"]/a[contains(text(), "重新预约")]')
            jx = 0

        sleep(2)
        try:
            self.driver.find_element_by_xpath(
                '//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[6]/td[2]/input').click()
            sleep(2)
        except:
            pass
        try:
            self.driver.find_element_by_xpath(
                '/html/body/div[2]/div[3]/div/button/span').click()
        except:
            pass
        if jx:
            try:
                wait = WebDriverWait(self.driver, 2, 0.1)
                locator = ("xpath", '/html/body/div[2]/div[3]/div/button')
                wait.until(EC.presence_of_element_located(locator)).click()
            except:
                pass
            sleep(1)
            try:
                self.driver.find_element_by_xpath(
                    '/html/body/div[4]/div[3]/div/button[1]/span')
            except:
                pass
            try:
                wait = WebDriverWait(self.driver, 2, 0.1)
                locator = ("id", 'j_id0:SiteTemplate:theForm:continue_btn')
                wait.until(EC.presence_of_element_located(locator)).click()
            except:
                self.Wait("")
        sleep(1)
        reg = r"myDayHash\['(.*?)'\] = true;"
        data = re.findall(reg, self.driver.page_source)
        # 返回可预约日期
        self.usPipe.uploadDays(",".join(data), self.resInfo["activity"])
        self.usPipe.uploadOrder(self.res["id"], python_status=0)
        return data

    # 预约 / 抢预约
    def reservation(self, data):
        """ 预约: {"day":"30-10-2018","t":"08:30"} 
        抢预约: {"day":"22-11-2018,23-11-2018","z":"2018-11-25"} """
        userDate = json.loads(self.res["interview_time"])
        days = userDate.get("day").split(",")
        t = userDate.get("t")
        z = userDate.get("z")
        for day in days:
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
                        self.Wait(
                            xpath=f'//*[@id="datepicker"]/div/div/div/div/span[contains(text(), {MON[mo]})]', text=NC)
                        break
                    except:
                        self.Wait(
                            xpath='//*[@id="datepicker"]/div/div[3]/div/a')

                divs = self.driver.find_elements_by_css_selector(
                    '#datepicker > div > div.ui-datepicker-group')
                for div in divs:
                    if div.find_element_by_xpath('./div/div/span').text == MON[mo]:
                        div.find_element_by_xpath(
                            f".//a[contains(text(), {int(d)})]").click()
                        break

                self.Wait(
                    xpath=f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{MON[mo]} {int(d)}")]', text=NC)
                reg = r'<td>(\d\d:\d\d)</td>'
                times = re.findall(reg, self.driver.page_source)
                if t in times:
                    self.Wait(
                        xpath=f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{t}")]/preceding-sibling::td[1]/input')
                    s_time = self.driver.find_element_by_xpath(
                        f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{t}")]').text
                    self.Wait("thePage:SiteTemplate:theForm:addItem")
                    self.Wait(
                        xpath='//*[@id="j_id0:SiteTemplate:j_id107:j_id109"]/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a')
                    self.Wait(
                        xpath='//*[@id="j_id0:SiteTemplate:j_id107:j_id109"]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/a')
                    with open("./usFile/AppointmentConfirmation.pdf", "rb") as f:
                        file = {"file": ("AppointmentConfirmation.pdf",
                                         f.read(), "application/pdf")}
                    url = "https://www.mobtop.com.cn/index.php?s=/Business/Pcapi/insertlogoapi"
                    res = requests.post(url, files=file).json()
                    success_time = f"{'-'.join([userDate['day'].split('-')][::-1])} {s_time}"
                    # 存入数据库
                    self.usPipe.uploadOrder(ids=self.res["id"], interview_success=success_time,
                                            interview_status="6", interview_pdf=res, interview_num=self.res["interview_num"]-1)
                    print("预约成功")
                    return 1
                elif z:
                    self.Wait(
                        xpath=f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{MON[mo]} {int(d)}")]/preceding-sibling::td[1]/input')
                    s_time = self.driver.find_element_by_xpath(
                        f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{MON[mo]} {int(d)}")]/preceding-sibling::td[2]').text
                    self.Wait("thePage:SiteTemplate:theForm:addItem")
                    self.Wait(
                        xpath='//*[@id="j_id0:SiteTemplate:j_id107:j_id109"]/table/tbody/tr[4]/td/table/tbody/tr/td[1]/a')
                    self.Wait(
                        xpath='//*[@id="j_id0:SiteTemplate:j_id107:j_id109"]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/a')
                    with open("./usFile/AppointmentConfirmation.pdf", "rb") as f:
                        file = {"file": ("AppointmentConfirmation.pdf",
                                         f.read(), "application/pdf")}
                    url = "https://www.mobtop.com.cn/index.php?s=/Business/Pcapi/insertlogoapi"
                    res = requests.post(url, files=file).json()
                    success_time = f"{'-'.join([userDate['day'].split('-')][::-1])} {s_time}"
                    # 存入数据库
                    self.usPipe.uploadOrder(ids=self.res["id"], interview_success=success_time,
                                            interview_status="8", interview_pdf=res, interview_num=self.res["interview_num"]-1)
                    print("预约成功")
                    return 1
        else: 
            if not z or time() - mktime(strptime(z, "%Y-%m-%d")) > 0:
                self.usPipe.uploadOrder(ids=self.res["id"], interview_status="5")
            self.getDates(1)
        return 0

    def appointment(self, data=None):
        if not data:
            if self.id != self.res["id"]:
                data = self.getDate()
                self.id = self.res["id"]
            else:
                reg = r"myDayHash\['(.*?)'\] = true;"
                data = re.findall(reg, self.driver.page_source)
        if self.reservation(data):
            return 1
        self.getDates(error=True)
        self.usPipe.uploadOrder(self.res["id"], interview_status='5')

    def cancel(self):
        if self.login():
            return 1
        self.Wait(xpath='//a[contains(text(),"取消预约")]')
        self.Wait(
            xpath='//*[@id="j_id0:SiteTemplate:j_id120"]/table/tbody/tr[14]/td/input[1]')
        print("取消成功")

    # 新增
    def groupLogin(self):
        pwd = PASSWD
        if self.group_email_info["status"] == 1:
            self.email = self.group_email_info["email"]
            pwd = self.group_email_info["password"]
        if self.login(pwd):
            return 1
        return 0

    # 查询预约付款号
    def groupAppointment(self):
        if self.groupLogin():
            return 1
        self.Wait(
            css='#nav_side > div > ul > span:nth-child(1) > li:nth-child(1) > a')
        # 中间操作
        self.middle()
        if self.add_user():
            self.selApp()
            self.middle()
        self.mail()
        self.receipt()
        self.driver.quit()

    def add_user(self):
        self.Wait(css="#summary", text=NC)
        lis = self.driver.find_elements_by_css_selector("#summary > ul > li")
        for _ in range(len(lis)):
            self.Wait(css=".ui-icon-close:nth-child(1)")
            self.Wait(xpath='/html/body/div[7]/div[3]/div/button[1]/span')

        for i in range(len(self.all_data[2])):
            pub = self.all_data[1][i]
            info = self.all_data[2][i]
            work = self.all_data[3][i]
            user = (pub, info, work)
            try:
                # if self.res["interview_status"] == 1:
                #     self.add_new_user(user)
                # else:
                #     self.add_old_user(user)
                if self.add_old_user(user):
                    if self.add_new_user(user):
                        return 1
            except:
                if self.add_new_user(user):
                    return 1

            sleep(3)
        # 截图
        self.pay_user_img()
        # 下一步
        self.driver.find_element_by_css_selector(
            "input[type='button']").click()

    def add_new_user(self, user):
        resPublic, resInfo, _ = user
        self.Wait(css='#create-user > span')
        self.Wait(css="select.formRelationship", text="Other")
        self.Wait(css=".requiredInput > .formDs160", text=resPublic["aacode"])
        self.Wait(css=".requiredInput > .formNationalId",
                  text=resInfo["identity_number"])
        self.Wait(css="span >.requiredInput > .requiredInput > .formFirstName",
                  text=resInfo["english_name_s"])
        self.Wait(css=".requiredInput > .formLastName",
                  text=resInfo["english_name"])
        gender = Select(self.driver.find_element(
            "css selector", ".requiredInput > select.formGender"))
        gender.select_by_value("Male" if resInfo["sex"] == "M" else "Female")
        year, month, day = resInfo["date_of_birth"].split("-")
        self.Wait(css="#datepicker > input", text=f"{month}/{day}/{year}")
        country = "China"
        self.Wait(css='.requiredInput > .formCountryOfBirth', text=country)
        self.Wait(css='.requiredInput > span > select', text=country)
        self.Wait(css='#issuancePlace > span > .formNationality', text=country)
        self.Wait(css='.requiredInput > .formPassport',
                  text=resInfo["passport_number"])
        year, month, day = resInfo["lssue_date"].split("-")
        self.Wait(css='.requiredInput > div > .formPassportDate',
                  text=f"{month}/{day}/{year}")
        year, month, day = resInfo["expiration_date"].split("-")
        self.Wait(css='.requiredInput > div > .formPassportExpirationDate',
                  text=f"{month}/{day}/{year}")
        self.Wait(css='.requiredInput > .formMobilePhone',
                  text='+86' + resInfo["home_telphone"])
        standby_phone = resInfo["tel"] if resInfo["tel"] else resInfo[
            "company_phone"] if resInfo["company_phone"] else resInfo["home_telphone"]
        self.Wait(css='.requiredInput > .formPhone',
                  text='+86' + standby_phone)
        self.Wait(css='.requiredInput > .formEmail', text=self.email)
        # 确认
        self.Wait(xpath='/html/body/div[3]/div[11]/div/button[1]/span')
        try:
            wait = WebDriverWait(self.driver, 3, 0.2, "添加新用户失败")
            locator = ("css selector", "form >ul > li")
            if wait.until(EC.presence_of_element_located(locator)).text == "Applicant already has an appointment.":
                self.Wait(xpath="/html/body/div[3]/div[1]/a/span")
                return 1
        except:
            pass

    def add_old_user(self, user):
        self.Wait(css="#create-addApplicants > span")
        self.Wait(xpath='//div[@id="dialog-formAddExisting"]//table')
        eng_names = f'{user[1]["english_name_s"]} {user[1]["english_name"]}'
        divs = self.driver.find_elements_by_xpath(
            f'//div[@id="dialog-formAddExisting"]//div')
        div = [i for i in divs if i.text.strip() == eng_names]
        if not div:
            self.Wait(xpath='/html/body/div[6]/div[1]/a/span')
            return 1
        div = div[0]
        div.find_element_by_css_selector("input").click()
        self.driver.find_element_by_xpath(
            '/html/body/div[6]/div[3]/div/button[1]/span').click()
        self.Wait(xpath='//*[@id="summary"]/ul/li[1]/div[2]/span')
        self.Wait(css=".requiredInput > .formDs160", text=user[0]["aacode"])
        self.Wait(xpath='/html/body/div[3]/div[11]/div/button[1]/span')
        return 0

    # 保存截图
    def pay_user_img(self):
        # 客户信息资料查看
        self.Wait(css="div#summary > ul", text=NC)
        self.driver.save_screenshot("usFile/info.png")
        info = self.driver.find_element_by_css_selector("div#summary > ul")
        info_left = info.location['x']
        info_top = info.location['y']
        info_right = info.location['x'] + info.size['width']
        info_bottom = info.location['y'] + info.size['height']
        img = Image.open("usFile/info.png")
        img = img.crop((info_left, info_top,
                        info_right, info_bottom))
        img.save("usFile/info.png")
        sleep(1)
        with open("usFile/info.png", "rb") as f:
            img = {"file": ("info.png", f.read(), "image/png")}
        url = "https://www.mobtop.com.cn/index.php?s=/Business/Pcapi/insertlogoapi"
        res = requests.post(url, files=img).json()
        self.usPipe.uploadOrder(self.res['id'], interview_img=res)
        # 确认
        sleep(1)

    # 中间操作
    def middle(self):
        radio = self.Wait(
            css='table > tbody > tr:nth-child(2) > td > input', text=NC)
        if not radio.is_selected():
            radio.click()
            self.Wait(xpath='/html/body/div[3]/div[3]/div/button/span')
        self.Wait(css='input.continue')
        lq = {"BEJ": 1, "CHE": 2, "GUZ": 3, "SHG": 4, "SNY": 5, }
        self.Wait(
            css=f"table > tbody > tr:nth-child({lq[self.resInfo['activity']]}) > td > input")
        self.Wait(css='input.continue')
        purpose = json.loads(self.resPublic["america_purpose"])[0]
        if self.resInfo["activity"] in ["BEJ", "GUZ", "SHG", "SNY"]:
            if purpose["one"] == "B":
                self.Wait(css='table > tbody > tr:nth-child(1) > td > input')
        elif self.resInfo["activity"] == "CHE":
            if purpose["one"] == "B":
                self.Wait(css='table > tbody > tr:nth-child(4) > td > input')
        self.Wait(css='input.continue')
        ppDic = {
            "B1-CF": '#accordion > div:nth-child(2) > table > tbody > tr:nth-child(1) > td > input',
            "B1-B2": '#accordion > div:nth-child(2) > table > tbody > tr:nth-child(2) > td > input',
            "B2-TM": '#accordion > div:nth-child(2) > table > tbody > tr:nth-child(3) > td > input',
        }
        self.Wait(css=ppDic[purpose["two"]])
        self.Wait(css='input.continue')

    # 中信取件或邮寄
    def mail(self):
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
                wait = WebDriverWait(self.driver, 2, 0.1)
                locator = (
                    'xpath', '//*[@id="thePage:SiteTemplate:theForm:pickupBlocks"]/div[1]/select[2]')
                wait.until(EC.presence_of_element_located(locator))
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
                        self.Wait(
                            xpath=f'//*[@id="addresses"]/tbody/tr[{i+1}]/td/input')
                        break
                # self.Wait(
                #     xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[3]/td[2]/input')
            except:
                self.Wait(
                    xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[6]/td[2]/input')
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
            # self.Wait(
            #     xpath='//*[@id="thePage:SiteTemplate:theForm:thePage"]/table/tbody/tr[3]/td[2]/input')

    # 付款填写收据 | 返回付款编号
    def receipt(self, code=''):
        try:
            wait = WebDriverWait(self.driver, 2, 0.1)
            locator = ("css selector",
                       "tr > td:last-child > input[type='submit']")
            wait.until(EC.presence_of_element_located(locator)).click()
        except:
            pass
        sleep(1)
        if code:
            print("付款填写收据")
            self.Wait(xpath='/html/body/div[2]/div[1]/a')
            self.Wait(css='dd > span > input', text=code)
            self.Wait(css='input.continue')
        else:
            print("返回付款编号")
            try:
                wait = WebDriverWait(self.driver, 2, 0.1)
                locator = ('xpath', '/html/body/div[2]/div[3]/div/button/span')
                wait.until(EC.presence_of_element_located(locator)).click()
            except:
                pass
            try:
                wait = WebDriverWait(self.driver, 2, 0.1)
                locator = (
                    'xpath', '/html/body/div[4]/div[3]/div/button[1]/span')
                wait.until(EC.presence_of_element_located(locator)).click()
            except:
                pass
            try:
                wait = WebDriverWait(self.driver, 2, 0.1)
                locator = (
                    'css selector', 'table > tbody > tr:nth-child(2) > td:first-child > a')
                wait.until(EC.presence_of_element_located(locator)).click()

                self.Wait(css='#referenceCell', text=NC)
                code = self.driver.find_element_by_css_selector(
                    '#referenceCell').text
                if code:
                    self.usPipe.uploadOrder(
                        self.res["id"], interview_status=2, pay_code=code, python_status=0)
                    return code
            except: 
                pass
        return 0

    # 预约查询
    def selApp(self, cancel=False):
        if self.history():
            return 1
        # self.driver.get("https://cgifederal.secure.force.com/ApplicantHome")
        self.Wait(
            css='#nav_side > div > ul > span:nth-child(1) > li:nth-child(2) > a')
        trs = self.driver.find_elements_by_xpath('//table[1]//tr')[1:]
        for i in range(len(self.all_data[2])):
            info = self.all_data[2][i]
            for tr in trs:
                if f'{info["english_name_s"]} {info["english_name"]}' in tr.text and "*Updated*" in tr.text:
                    # 撤销
                    if cancel == 1:
                        tr.find_element_by_xpath(".//li//ul/li[2]/a").click()

                    elif cancel:
                        tr.find_element_by_xpath(".//li//ul/li[5]/a").click()
                        if cancel == 3:
                            times = self.driver.find_element_by_xpath(
                                '//table[@role="presentation"]').text.split('\n')
                            date_times = {}
                            for time in times:
                                date = time.split(' ')
                                day = f"{int(date[3].strip(','))}-{MON_ANTI[date[2]]}-{date[4]}"
                                ti = date[0]
                                if not date_times.get(day):
                                    date_times[day] = [ti]
                                else:
                                    date_times[day].append(ti)
                            dates = '|'.join(
                                [f"{i}&{','.join(date_times[i])}" for i in date_times])
                            self.usPipe.uploadDays(
                                info["activity"], replace_interview_days=dates)

                        elif cancel == 2 and self.res["interview_time"]:
                            userDate = json.loads(self.res["interview_time"])
                            userDateDay = userDate["day"].split('-')
                            userDateDay[1] = f"{userDateDay[1]:0>2}"
                            date = f'{MON[userDateDay[1]]} {userDateDay[0]}, {userDateDay[2]}'
                            tds = self.driver.find_elements_by_xpath(
                                '//table[@role="presentation"]//td')
                            [td.find_element_by_xpath(
                                "./input").click for td in tds if date and userDate["t"] in td.find_element_by_xpath("./lable").text]
                            self.driver.find_element_by_xpath(
                                '/html/body/div[3]/div[3]/div/button[1]/span').click()

                    tds = tr.text.split("\n")
                    _, month, day, year = tds[0].split(' ')
                    success_time = f"{year}-{MON_ANTI[month]}-{day} {tds[1]}"
                    self.usPipe.uploadOrder(
                        self.res["id"], interview_status=6, python_status=0, interview_success=success_time)
                    return 1

        if cancel == 1:
            self.usPipe.uploadOrder(
                self.res["id"], interview_status=9, replace=0, interview_success=None)
            return 1
        self.Wait(css='#dashboard > span > form > input[type="text"]:nth-child(2)',
                  text=f'{self.resInfo["english_name_s"]} {self.resInfo["english_name"]}')
        self.Wait(
            css='#dashboard > span > form > input[type="submit"]:nth-child(3)')
        self.Wait(xpath='//table[1]', text=NC)
        try:
            self.driver.find_element_by_css_selector(
                'table > tbody > tr > td:nth-child(2) > span > a').click()
        except:
            self.driver.find_element_by_css_selector(
                '#nav_side > div > ul > span:nth-child(1) > li:nth-child(1) > a').click()

    def history(self):
        history_element = self.Wait(
            css="#ctl00_nav_side1 > ul > li:nth-child(3) > a", text=NC)
        # self.Wait(css="#ctl00_nav_side1 > ul > li:nth-child(3) > a")
        print(history_element.text)
        if history_element.text != "预约历史":
            return
        history_element.click()
        for i in range(len(self.all_data[2])):
            info = self.all_data[2][i]
            self.Wait(
                css='input[type="text"]', text=f'{info["english_name_s"]} {info["english_name"]}')
            sleep(1)
            trs = self.driver.find_elements_by_css_selector(
                "#appointmentHistoryTable > tbody > tr")
            for tr in trs:
                status = tr.find_element_by_css_selector("td:last-child").text
                if "Scheduled" == status:
                    _, month, day, year, time = tr.find_element_by_css_selector(
                        "td:nth-child(2)").text.split(' ')
                    success_time = f"{year}-{MON_ANTI[month]}-{day.strip(',')} {time}"
                    self.usPipe.uploadOrder(
                        self.res["id"], interview_status="6", interview_success=success_time, python_status=0)
                    return 1
        return 0

    # 开始预约
    def group_pay_over(self, rob=0):
        if self.groupLogin():
            return
        if self.selApp(self.res["replace"]):
            return
        self.middle()
        self.add_user()
        # self.Wait(css="input[type='button']")
        self.mail()
        if self.receipt():
            return
        if not rob:
            self.AppLast()
        else:
            # 抢预约
            start_time = time()
            while time() - start_time < 3600:
                if self.reservation(self.getDates()):
                    return 1
            else:
                return 0
        self.driver.quit()

    def getDates(self, error=False):
        reg = r"myDayHash\['(.*?)'\] = true;"
        dates = re.findall(reg, self.driver.page_source)
        if self.res["python_status"] == 1 or error:
            reg = r'<td>(\d\d:\d\d)</td>'
            appointment_dates = {}
            elements = self.driver.find_elements_by_css_selector(
                "td > a.ui-state-default")
            for index in range(len(elements)):
                try:
                    d, m, _ = dates[index].split("-")
                    m = f"{m:0>2}"
                    elements[index].click()
                    self.Wait(
                        xpath=f'//*[@id="myCalendarTable"]/tbody//td[contains(text(),"{MON[m]} {int(d)}")]', text=NC)
                    times = re.findall(reg, self.driver.page_source)
                    appointment_dates[dates[index]] = ','.join(times)
                    elements = self.driver.find_elements_by_css_selector(
                        "td > a.ui-state-default")
                except Exception as e:
                    print(e)
                    continue

            upload_dates = '|'.join(
                [f"{i}&{appointment_dates[i]}" for i in appointment_dates])
            self.usPipe.uploadDays(
                self.resInfo["activity"], interview_days=upload_dates)
            self.usPipe.uploadOrder(self.res["id"], python_status=0)
        return dates

    def AppLast(self):
        # =====
        try:
            sleep(2)
            # 预约-未付款-待完善
            self.Wait(xpath='//*[@id="mainContent"]/div/form/div/input[2]')
        except:
            sleep(2)
            # 预约-未付款-待完善
            self.Wait(xpath='//*[@id="mainContent"]/div/form/div/input[2]')
        sleep(1)
        dates = self.getDates()
        if self.res["interview_status"] == 4:
            self.appointment(dates)

    # def group_cancel(self):
        # self.groupLogin()
        # self.selApp(True)
