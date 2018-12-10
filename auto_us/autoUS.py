#!/usr/bin/env python
# coding: utf-8
"""
@Author: ZhaoBin 
@Date: 2018-08-05 13:30:41 
@Last Modified by:   ZhaoBin 
@Last Modified time: 2018-08-08 17:00:41
"""
import glob
import re

import requests
from lxml import etree
from PIL import Image

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .fateadm import Captcha
from .settings import (BASEDIR, MON, MONTH, NC, PASSWD, USER, USERPHOTO,
                       UsError, json, os, sleep, strftime, sys)
from .yunsu import upload

nodeInfo = {
    "Personal1": "5% 个人信息1",
    "Personal2": "10% 个人信息2",
    "AddressPhone": "15% 地址和电话页",
    "PptVisa": "20% 护照页",
    "Travel": "25% 旅行页",
    "TravelCompanions": "30% 旅行同伴页",
    "PreviousUSTravel": "35% 以前美国之行",
    "USContact": "40% 美国联系人信息",
    "Relatives": "45% 家庭/亲属页",
    "Spouse": "50% 配偶页",
    "DeceasedSpouse": "50% 丧偶页",
    "PrevSpouse": "50% 离异页",
    "WorkEducation1": "55% 工作教育",
    "WorkEducation2": "60% 以前的工作/培训页",
    "WorkEducation3": "65% 工作补充页",
    "SecurityandBackground1": "70% 安全与背景页",
    "SecurityandBackground2": "70% 安全与背景页",
    "SecurityandBackground3": "70% 安全与背景页",
    "SecurityandBackground4": "70% 安全与背景页",
    "SecurityandBackground5": "70% 安全与背景页",
    "UploadPhoto": "80% 上传照片页",
    "ConfirmPhoto": "80% 上传照片页",
    "ReviewPersonal": "90% 审查页面",
    "ReviewTravel": "90% 审查页面",
    "ReviewUSContact": "90% 审查页面",
    "ReviewFamily": "90% 审查页面",
    "ReviewWorkEducation": "90% 审查页面",
    "ReviewSecurity": "90% 审查页面",
    "ReviewLocation": "90% 审查页面",
    "SignCertify": "95% 最后确认页面",
}

class Base:
    """ 浏览器基类, 保持同一个 driver """

    def __init__(self, noWin=False, noImg=False):
        self.path = sys.path[0] + '\\'
        # 设置 chrome_options 属性
        self.chrome_options = webdriver.ChromeOptions()
        # 不加载图片
        if noImg:
            self.chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # 无界面
        if noWin:
            self.chrome_options.add_argument('--headless')
        # 设置代理
        # self.chrome_options.add_argument('--proxy-server=http://127.0.0.1:1080')
        # 设置浏览器窗口大小
        self.chrome_options.add_argument('window-size=800x3000')
        # for linux/*nix, download_dir="/usr/Public"
        download_dir = os.path.join(BASEDIR, 'usFile') 
        # ----------页面打印版pdf下载-----------------
        appState = { 
            "recentDestinations": [ 
                { 
                    "id": "Save as PDF", 
                    "origin": "local" 
                } 
            ], 
            "selectedDestinationId": "Save as PDF", 
            "version": 2 
        } 
        # ----------网页版pdf直接下载-----------------
        profile = {
            "plugins.plugins_list": [{
                "enabled": False, "name": "Chrome PDF Viewer"
            }],  # Disable Chrome's PDF Viewer
            "download.default_directory": download_dir, 
            "download.extensions_to_open": "applications/pdf",
            'printing.print_preview_sticky_settings.appState': json.dumps(appState),
            'savefile.default_directory': download_dir
        }
        self.chrome_options.add_experimental_option("prefs", profile)
        self.chrome_options.add_argument('--kiosk-printing')
        self.driver = webdriver.Chrome(
            executable_path=self.path + 'chromedriver', chrome_options=self.chrome_options)
        # 设置隐性等待时间, timeout = 20
        self.driver.implicitly_wait(5)
        # self.driver.maximize_window()
        # 设置显性等待时间, timeout = 10, 间隔 0.3s 检查一次
        self.wait = WebDriverWait(self.driver, 5, 0.2, "请求超时")

    def getDriver(self, noWin=True):
        # 无界面
        if noWin:
            self.chrome_options.add_argument('--headless')
        else:
            self.chrome_options._arguments.remove('--headless')
        self.driver = webdriver.Chrome(
            executable_path=self.path + 'chromedriver', chrome_options=self.chrome_options)
        # 设置隐性等待时间, timeout = 20
        self.driver.implicitly_wait(5)
        # self.driver.maximize_window()
        # 设置显性等待时间, timeout = 10, 间隔 0.3s 检查一次
        self.wait = WebDriverWait(self.driver, 5, 0.2, "请求超时")

    # 获取验证码
    def getCaptcha(self, id='', element=None, a=0, pred_type="306005000"):
        """ 验证码识别
            根据页面验证码元素位置, 截取验证码图片
            发送验证码识别请求,返回验证码文字

            Returns: result (str)
        """
        print("正在识别验证码...")
        if element:
            captcha = element
        else:
            self.Wait(id, NC)
            captcha = self.driver.find_element_by_id(id)

        self.driver.save_screenshot('captcha.png')
        captcha_left = captcha.location['x']
        top = 0 if captcha.location['y'] < 1200 else 910
        captcha_top = captcha.location['y'] - top
        captcha_right = captcha.location['x'] + captcha.size['width'] + a
        captcha_bottom = captcha.location['y'] + captcha.size['height'] - top + a
        img = Image.open('captcha.png')
        img = img.crop((captcha_left, captcha_top,
                        captcha_right, captcha_bottom))
        img.save('code.png')
        sleep(0.5)
        # result = upload()
        rsp = Captcha(2, path='code.png', pred_type=pred_type)
        print(f"验证码为: {rsp.pred_rsp.value}")
        return rsp

    # 检测元素 / 点击 / 发送字符 / 选择下拉框
    def Wait(self, idName=None, text=None, xpath=None, css=None):
        """ 设置显性等待, 每 0.3s 检查一次
            Parameter:
                idName, xpath, className: 选择器规则, 默认idName
                text: 需要发送的信息 (非 NC --> 'noClick')
        """
        # try:
        #     assert idName or xpath or css
        # except AssertionError:
        #     raise UsError('未传选择器')
        if idName:
            locator = ("id", idName)
        elif xpath:
            locator = ("xpath", xpath)
        elif css:
            locator = ("css selector", css)

        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            if not text and not element.is_selected():
                element.click()
            elif text and text != NC:
                try:
                    element.clear()
                except Exception:
                    pass
                finally:
                    element.send_keys(text)
            try:
                return element
            except Exception:
                pass
        except Exception as e:
            raise UsError(f"{e}\n{locator[0]}: {locator[1]}\n" +
                          f"value : {text if text and text != NC else 'None'}\n\n")
        return 0

    def choiceSelect(self, selectid=None, value=None, t=0.2):
        """ 下拉框选择器
            根据 value 选择下拉框
        """
        # try:
        #     assert selectid and value
        # except AssertionError:
        #     raise UsError(
        #         f'下拉框选择器 ID 和 value 不能为空\nselectid: {selectid}\nvalue   : {value}')
        sleep(t)
        try:
            element = Select(self.Wait(selectid, text=NC))
            element.select_by_value(value)
        except Exception as e:
            raise UsError(f"{e}\nidName: {selectid}\nvalue : {value}\n\n")

        return 0

    def waitIdSel(self, idlist=None, selist=None):
        """ 对 idlist 进行点击/发送字符串 或对 selist 进行选择
            Returns: 
                [] 空列表
        """
        if idlist:
            for idName, value in idlist:
                self.Wait(idName, value)
        if selist:
            for idName, value in selist:
                self.choiceSelect(idName, value)

        return []

    def __del__(self):
        self.driver.quit()

class AutoUs(Base):
    """ 自动化录入程序基类
        Parameter:
            resInfo:    数据库 dc_business_america_info_eng 信息
            resPublic:  数据库 dc_business_america_public_eng 信息
            resWork:    数据库 dc_business_america_work_eng 信息
    """
    answer = "A"
    usUrl = 'https://ceac.state.gov/GenNIV/Default.aspx'
    payUrl = 'https://cgifederal.secure.force.com/'
    baseID = "ctl00_SiteContentPlaceHolder_"

    def __init__(self, data=None, usPipe=None, noWin=False, noImg=False):
        super().__init__(noWin=noWin, noImg=noImg)
        self.resPublic, self.resInfo, self.resWork = data if data else (
            0, 0, 0)
        self.usPipe = usPipe
        self.AAcode = "" if not self.resPublic else self.resPublic["aacode"]
        self.nodeDict = {}
        self.old_page = 1

    # 回到个人信息页1
    def comeBack(self):
        print("回到个人信息页1")
        self.driver.get(
            "https://ceac.state.gov/GenNIV/General/complete/complete_personal.aspx?node=Personal1")

    # 获取网页标示「网址最后一个单词」
    @property
    def getNode(self):
        node = self.driver.current_url.split("node=")[-1]
        return node if "http" not in node and "data:," != node else ""

    # 开始的验证
    def start_captcha(self):
        one = False
        rsp = None
        try:
            wait = WebDriverWait(self.driver, 2, 0.2, "请求超时")
            wait.until(EC.presence_of_element_located(("id", "clntcap_frame")))

            self.driver.switch_to.frame(0)
            for _ in range(10):
                img = wait.until(EC.presence_of_element_located(("xpath", "//img")))
                print("开始的验证")
                if one:
                    Captcha(4, rsp=rsp)
                # res = self.getCaptcha(element=img, a=10)
                rsp = self.getCaptcha(element=img, a=10, pred_type="30600")
                res = rsp.pred_rsp.value
                self.driver.find_element("id", "ans").send_keys(res)
                self.driver.find_element("id", "jar").click()
                sleep(2)
                try:
                    wait.until(EC.presence_of_element_located(("id", f"{self.baseID}ucLocation_ddlLocation")))
                    break
                except Exception:
                    pass
                one = True
        except Exception:
            pass

    # 开始一个新的签证
    @property
    def default(self):
        """ 开始一个新的签证 """
        print("开始一个新的签证")
        # 请求首页
        self.driver.get(self.usUrl)
        self.start_captcha()
        # 选择中文简体
        # self.choiceSelect("ctl00_ddlLanguage", "zh-CN")
        # 选择领区
        print("选择领区")
        if self.resInfo['activity']:
            self.choiceSelect(f"{self.baseID}ucLocation_ddlLocation", self.resInfo['activity'])
        else:
            self.errJson([], '领区未选')
        # self.choiceSelect(f"{self.baseID}ucLocation_ddlLocation", 'BEJ')
        # 识别验证码
        for _ in range(5):
            try:
                # result = self.getCaptcha('c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage')
                # self.Wait(f'{self.baseID}ucLocation_IdentifyCaptcha1_txtCodeTextBox', result)
                rsp = self.getCaptcha('c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage')
                self.Wait(f'{self.baseID}ucLocation_IdentifyCaptcha1_txtCodeTextBox', rsp.pred_rsp.value)
                sleep(1)
                self.Wait(f'{self.baseID}lnkNew')
            except Exception:
                pass
            sleep(2)
            if self.driver.current_url in self.usUrl:
                Captcha(4, rsp=rsp)
                continue
            break
        else:
            print("验证码 5 次错误, 重启")
            return 1

        self.Wait(f"{self.baseID}txtAnswer", self.answer)
        self.Wait(f"{self.baseID}btnContinue")
        return 0

    # 继续一个旧的签证
    def continueGo(self, noback=1):
        self.old_page = noback
        """ 继续一个旧的签证信息 """
        print("继续一个旧的签证信息")
        self.driver.get(self.usUrl)
        self.start_captcha()
        # 选择中文简体
        # self.choiceSelect("ctl00_ddlLanguage", "zh-CN")
        # 选择领区
        print("选择领区")
        if self.resInfo['activity']:
            self.choiceSelect(f"{self.baseID}ucLocation_ddlLocation", self.resInfo['activity'])
        else:
            self.errJson([], '领区未选')

        for _ in range(5):
            try:
                # result = self.getCaptcha(f'c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage')
                # self.Wait(f'{self.baseID}ucLocation_IdentifyCaptcha1_txtCodeTextBox', result)
                rsp = self.getCaptcha(f'c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage')
                self.Wait(f'{self.baseID}ucLocation_IdentifyCaptcha1_txtCodeTextBox', rsp.pred_rsp.value)
                self.Wait(f'{self.baseID}lnkRetrieve')
                if self.driver.current_url == "https://ceac.state.gov/GenNIV/common/Recovery.aspx": 
                    break
            except Exception: 
                pass
            sleep(2)
            if self.driver.current_url in self.usUrl:
                Captcha(4, rsp=rsp)
                continue
            break
        else:
            print("验证码 5 次错误, 重启")
            return 1

        self.Wait(f"{self.baseID}ApplicationRecovery1_tbxApplicationID", self.resPublic['aacode'])

        ids = [
            (f"{self.baseID}ApplicationRecovery1_btnBarcodeSubmit", ""),
            (f"{self.baseID}ApplicationRecovery1_txbSurname", self.resInfo['english_name'][:5]),
            (f'{self.baseID}ApplicationRecovery1_txbDOBYear', self.resInfo['date_of_birth'].split('-')[0]),
            (f'{self.baseID}ApplicationRecovery1_txbAnswer', self.answer),
            (f'{self.baseID}ApplicationRecovery1_btnRetrieve', ""),
        ]
        self.waitIdSel(ids)
        for _ in range(2):
            if self.getNode != "":
                break
            sleep(1)
        else:
            try: 
                self.Wait("ctl00_SiteContentPlaceHolder_ApplicationRecovery1_pnlSubmittedApp", text=NC)
                self.usPipe.upload(self.resPublic["aid"], status="4")
                return 1
            except Exception:
                pass

        if noback:
            self.Wait(f"{self.baseID}UpdateButton3")
        else:
            self.comeBack()

    # 错误信息字典
    @property
    def errDict(self):
        """ 错误信息提示
            Returns:
                err (dict) 美签官网大部分错误信息的提示
        """
        err = {
            "The Visa Number that you have entered is invalid.": "签证号码请输入签证右下角显示为红色的8位数字。 如果您以前的签证是边境检票卡，请输入机读区第一行的最后12位数字。",
            "Date of Arrival in U.S. is invalid. Month, Day, and Year are required.": "到达日期有误",
            "Date of Departure from U.S. is invalid. Month, Day, and Year are required.": "离美日期有误",
            "Phone Number accepts only numbers (0-9).": "电话只能为数字 0-9",
            "Primary Phone Number accepts only numbers (0-9).": "主要电话只能为数字 0-9",

            "Present Employer or School Name is invalid. Only the following characters are valid for this field: A-Z, 0-9, hypen (-), "
            "apostrophe ('), ampersand (&) and single spaces in between names.": 
            "公司/学校名称只有以下字符对此字段有效：A-Z，0-9，(-)，撇号(')，符号(＆)和名称之间的单个空格",

            "Primary Phone Number has not been completed.": "主要电话未填",
            "Alias matches Given Name.": "曾用名有误",
            "National Identification Number is invalid. Only the following characters are valid for this field: A-Z, 0-9 and single "
            "spaces in between letters/numbers.": "身份证号码只能为 A-Z, 0-9 和单个空格",

            "Surnames has not been completed.": "姓氏未填",
            "Given Names has not been completed.": "名字未填",
            "Full Name in Native Alphabet has not been completed.": "原名未填",
            "The question \"Have you ever used other names (i.e., maiden, religious,...?\" has not been answered.": "曾用名未选",
            "Other Surnames Used (maiden, religious, professional, aliases, etc.) has not been completed.": "曾用姓氏未填",
            "Other Given Names Used has not been completed.": "曾用名未填",
            "The question \"Do you have a telecode that represents your name?\" has not been answered.": "姓名电码未选",
            "Telecode Surnames has not been completed.": "姓氏的电码未填",
            "Telecode Surnames must only contain sets of four numbers separated by spaces.": "姓氏的电码未填正确",
            "Sex has not been completed.": "性别未选",
            "Marital Status has not been completed.": "婚姻状况未选",
            "Date has not been completed.": "生日未正确填写",
            "City has not been completed.": "城市未填",
            "State/Province has not been completed.": "州/省尚未填",
            "Country/Region has not been completed.": "国家/地区尚未选",
            "The question \"Are you a permanent resident of a country/region other...?\" has not been answered.": "是否永久居民未选",
            "National Identification Number has not been completed.": "身份证未填",
            "U.S. Social Security Number has not been completed.": "安全号码未填",
            "U.S. Taxpayer ID Number has not been completed.": "美国身份号码未填",
            "Country/Region of Origin (Nationality) has not been completed.": "所属国家/地区（国籍）未选",
            "The question \"Do you hold or have you held any nationality other than...?\" has not been answered.": "其它国籍未选",
            "U.S. Social Security Number accepts only numbers (0-9) and must be exactly nine (9) digits.": "美国安全号只能为9位数字",
            "U.S. Taxpayer ID Number accepts only numbers (0-9).": "美国身份证号只能为数字",
            "Street Address (Line 1) has not been completed.": "街道地址未填",
            "The question \"Is your Mailing Address the same as your Home Address?\" has not been answered.": "邮寄地址未选",
            "Email Address has not been completed.": "电子邮件地址未填",
            "Secondary Phone Number accepts only numbers (0-9).": "次要电话只能是数字",
            "Work Phone Number accepts only numbers (0-9).": "工作电话只能是数字",
            "Email Address is invalid. Verify the format is correct.": "电子邮箱不可用",
            "Passport/Travel Document Type has not been completed.": "护照类型未选",
            "Passport/Travel Document Number has not been completed.": "护照号未填",
            "Passport Book Number has not been completed.": "护照本编号未填",
            "Issuance Date is invalid. Month, Day, and Year are required.": "签发日期未填",
            "Expiration Date is invalid. Month, Day, and Year are required.": "失效日期未填",
            "The question \"Have you ever lost a passport or had one stolen?\" has not been answered.": "曾遗失/被盗？",
            "The explanation for question \"Explain\" has not been completed.": "遗失/被盗原因未填",
            "The question \"Have you made specific travel plans?\" has not been answered.": "访美目的|旅行计划 未选",
            "Specify has not been completed.": "访美目的(详细)未选",
            "Person/Entity Paying for Your Trip has not been selected.": "支付方式未选",
            "Intended Date of Arrival is invalid. Month and Year are required.": "抵达日期无效",
            "Intended Length of Stay in U.S. has not been completed.": "预计停留时间未填",
            "Surnames of Person Paying for Trip has not been completed.": "付款人姓未填",
            "Given Names of Person Paying for Trip has not been completed.": "付款人名未填",
            "Telephone Number has not been completed.": "付款人电话号未填",
            "Relationship to You has not been selected.": "与您的关系未选",
            "The question \"Is the address of the party paying for your trip the...?\" has not been answered.": "支付人地址未选",
            "The question \"Are there other persons traveling with you?\" has not been answered.": "同行人未选择",
            "The question \"Have you ever been in the U.S.?\" has not been answered.": "您是否曾经在美国停留过？",
            "The question \"Have you ever been issued a U.S. Visa?\" has not been answered.": "您是否曾经获得过美国签证?",
            "The question \"Have you ever been refused a U.S. Visa, or been refused...?\" has not been answered.": "您被拒签过吗？ 或在入境口岸被拒入境，或被撤销入境申请？",
            "The question \"Has anyone ever filed an immigrant petition on your...?\" has not been answered.": "曾有人在公民及移民服务局为您申请过移民吗？",
            "The question \"Do you or did you ever hold a U.S. Driver’s License?\" has not been answered.": "有无驾照未选",
            "Date Last Visa Was Issued is invalid. Month, Day, and Year are required.": "签发日期未填",
            "Visa Number has not been completed.": "护照号未填",
            "The question \"Are you applying for the same type of visa?\" has not been answered.": "是否申请同一类型的签证未选",
            "The question \"Are you applying in the same country or location where...?\" has not been answered.": "是否在同一个国家或地点申请未选",
            "The question \"Have you been ten-printed?\" has not been answered.": "是否留取过十指指纹未选",
            "The question \"Has your U.S. Visa ever been lost or stolen?\" has not been answered.": "美国签证是否丢失或被盗未选",
            "The question \"Has your U.S. Visa ever been cancelled or revoked?\" has not been answered.": "美国签证是否曾被取消或撤销未选",
            "The explanation for question \"Have you ever been refused a U.S. Visa, or been refused...?\" has not been completed.": "有没有被拒签未选",
            "The explanation for question \"Has anyone ever filed an immigrant petition on your...?\" has not been completed.": "曾有人在公民及移民服务局为您申请过移民吗?未选",
            "Date Arrived is invalid. Year is required.": "抵达日期未填",
            "Length of Stay has not been completed.": "停留时间未填",
            "Organization Name has not been completed.": "组织名未填",
            "Relationship to You has not been completed.": "关系未选",
            "'Relationship to You' cannot be 'Spouse', 'Relative', or 'Friend' if only the Organization Name is selected.": "组织名称不能是\"配偶\",\"亲属\"或\"朋友\".",
            "U.S. Street Address (Line 1) has not been completed.": "美国地址未填",
            "State has not been completed.": "美国州未填",
            "Phone Number has not been completed.": "电话未填",
            "Date of Birth has not been completed.": "生日未填",
            "The question \"Is your father in the U.S.?\" has not been answered.": "父亲是否在美未选",
            "The question \"Is your mother in the U.S.?\" has not been answered.": "母亲是否在美未选",
            "The question \"Do you have any immediate relatives, not including...?\" has not been answered.": "是否有直系亲属在美?",
            "Father's Date of Birth must be earlier than your Date of Birth.": "父亲的生日必须早于您",
            "Mother's Date of Birth must be earlier than your Date of Birth.": "母亲的生日必须早于您",
            "The question \"Do you have any other relatives in the United States?\" has not been answered.": "您在美国是否有其它亲属未选",
            "Number of Former Spouses: has not been completed.": "离异人数未填",
            "Date of Marriage has not been completed.": "结婚日期未填",
            "Date Marriage Ended has not been completed.": "离婚日期未填",
            "The explanation for question \"How the Marriage Ended\" has not been completed.": "婚姻怎样终止的未填",
            "Country/Region Marriage was Terminated has not been completed.": "离婚所在国家未选",
            "Primary Occupation has not been completed.": "主要职业未选",
            "The question \"Were you previously employed?\" has not been answered.": "之前有否工作未选",
            "The question \"Have you attended any educational institutions at a...?\" has not been answered.": "是否在中学水平或以上的教育机构里学习过？",
            "Supervisor's Surname has not been completed.": "主管姓氏未填",
            "Supervisor's Given Names has not been completed.": "主管名字未填",
            "Employer Name has not been completed.": "单位名称未填",
            "Employer Street Address (Line 1) has not been completed.": "单位街道地址未填",
            "Job Title has not been completed.": "职务名称未填",
            "Employment Date From is invalid. Year is required.": "入职时间未填",
            "Employment Date To is invalid. Year is required.": "离职时间未填",
            "Briefly describe your duties: has not been completed.": "工作职责未填",
            "Name of Institution has not been completed.": "机构名称未填",
            "Postal Zone/ZIP Code has not been completed.": "邮编未填",
            "Course of Study has not been completed.": "课程名未填",
            "Date of Attendance From is invalid. Month and Year are required.": "入学时间未填",
            "Date of Attendance To is invalid. Month and Year are required.": "毕业时间未填",
            "Employer Name is invalid. Only the following characters are valid for this field: A-Z, 0-9, hypen (-), apostrophe (\'), ampersand (&) and single spaces in between names.": "公司名称只能为: A-Z, 0-9, -, \', & 和 空格",
            "The question \"Do you have any specialized skills or training, such as...?\" has not been answered.": "是否具有特殊技能/培训",
            "Organization Name is invalid. Only the following characters are valid for this field: A-Z, 0-9, hypen (-), apostrophe (\'), ampersand (&) and single spaces in between names.": "组织名无效(与公司名要求一致)",
            "The submitted photo did not meet the image quality requirements.": "照片不合格",
            "Unable to read image memory into DibImage.": "无法读取图像",
            "Telephone Number accepts only numbers (0-9).": "电话只能是数字 0-9",
            "Date is invalid.": "日期无效",
            "Name of Institution is invalid. Only the following characters are valid for this field: A-Z, 0-9, hypen (-), apostrophe (\'), ampersand (&) and single spaces in between names.": "公司名或学校名只能为:(A-Z) 或 (0-9) 或 (') 或 (-) 或 (&)"
        }
        return err

    # 将错误信息存入数据库「json 数据」
    def errJson(self, errlist=None, errInfo=None, status=1):
        """ 将错误信息封装成 json 数据进行返回 """
        ls = []
        ls.append(errInfo)
        for i in errlist[1:]:
            ls.append(self.errDict.get(i, i))
        # err = json.dumps(ls).replace('\\', '\\\\')
        err = '|'.join(ls)
        self.usPipe.upload(self.resPublic['aid'], status="6", ques=err)
        # if self.resPublic["conditions"] == 0:
        #     self.usPipe.upload(self.resPublic['aid'], status="6", ques=err)
        # elif self.resPublic["conditions"] < 0:
        #     self.usPipe.upload(self.resPublic['aid'], conditions=self.resPublic["conditions"]+1, ques=err)
        # elif self.resPublic["conditions"] > 0:
        #     self.usPipe.upload(self.resPublic['aid'], conditions=0)

    # 进度条
    def progress(self, info):
        self.usPipe.upload(self.resPublic["aid"], progress=info)

    def urlButton(self):
        self.Wait(f"{self.baseID}UpdateButton3")

    def printPdf(self):
        self.driver.execute_script("window.print()")
        sleep(2)

    def renamePdf(self, path=os.path.join(BASEDIR, 'usFile')):
        for infile in os.listdir(path):
            if infile[-3:] != 'pdf':
                continue  # 过滤掉改名的.py文件
            name = f'''{self.resInfo["username"]}{self.resInfo["date_of_birth"].split("-")[0]}美国%s页_{self.AAcode if self.AAcode else self.resPublic["aacode"]}.pdf'''
            oldname = os.path.join(path, infile)
            if "Nonimmigrant Visa" in infile:
                newname = os.path.join(path, name % "确认")
                os.rename(oldname, newname)
            elif "Consular Electronic" in infile:
                newname = os.path.join(path, name % "信息")
                os.rename(oldname, newname)

    @property
    def uploadPdf(self):
        """ 上传「PDF」文件 """
        url = "http://www.mobtop.com.cn/index.php?s=/Api/MalaysiaApi/AmericaInsertPdf/"
        dic = {1: "确认", 2: "信息"}
        i = 1
        while i < 3:
            filename = f'''{self.resInfo["username"]}{self.resInfo["date_of_birth"].split("-")[0]}美国%s页_{self.AAcode if self.AAcode else self.resPublic["aacode"]}.pdf''' % dic[i]
            print(os.path.join(BASEDIR, 'usFile', filename))
            with open(os.path.join(BASEDIR, 'usFile', filename), "rb") as f:
                files = {"file": f.read()}
            data = {"aid": self.resInfo["aid"], "type": i}
            res = requests.post(url, data=data, files=files)
            print(res.json())
            if res.json()["status"] == 1:
                i += 1
        self.usPipe.upload(self.resPublic["aid"], status=4, visa_status=3)
        try:
            for infile in glob.glob(os.path.join(BASEDIR, 'usFile\\*.pdf')):
                if "AppointmentConfirmation" in infile: continue
                os.remove(infile)
        except Exception:
            pass        
        return 0

    def cos(self, s, school=1):
        """ 公司/学校名称只有以下字符对此字段有效：A-Z，0-9，(-)，撇号(')，符号(＆)和名称之间的单个空格 
        电话只能为 0-9
        """
        if school:
            return re.sub(r"[^A-Z0-9&\-'\s]|\s[\s]+", lambda x: "" if len(x.group()) == 1 else " ", s.upper())
        else:
            return re.sub(r"[^0-9]+", "", s)

class AllPage(AutoUs):
    """ 逻辑 """
    # 入口函数 -- 程序执行开始
    @property
    def run(self):
        """ 根据 node 来选择具体函数 """
        self.nodeDict = {
            "Personal1": self.personal1,
            "Personal2": self.personal2,
            "AddressPhone": self.addPhone,
            "PptVisa": self.pptVisa,
            "Travel": self.travel,
            "TravelCompanions": self.travelCompanions,
            "PreviousUSTravel": self.previousUSTravel,
            "USContact": self.usContact,
            "Relatives": self.relatives,
            "Spouse": self.family,
            "DeceasedSpouse": self.family,
            "PrevSpouse": self.family,
            "WorkEducation1": self.workEducation1,
            "WorkEducation2": self.workEducation2,
            "WorkEducation3": self.workEducation3,
            "SecurityandBackground1": self.securityAndBackground,
            "SecurityandBackground2": self.securityAndBackground,
            "SecurityandBackground3": self.securityAndBackground,
            "SecurityandBackground4": self.securityAndBackground,
            "SecurityandBackground5": self.securityAndBackground,
            "UploadPhoto": self.uploadPhoto,
            "ConfirmPhoto": self.urlButton,
            "ReviewPersonal": self.urlButton,
            "ReviewTravel": self.urlButton,
            "ReviewUSContact": self.urlButton,
            "ReviewFamily": self.urlButton,
            "ReviewWorkEducation": self.urlButton,
            "ReviewSecurity": self.urlButton,
            "ReviewLocation": self.urlButton,
            "SignCertify": self.signCertify,
        }
        if self.resPublic["inspect"] and self.getNode in ["ReviewPersonal", "ReviewTravel", "ReviewUSContact", "ReviewFamily", "ReviewWorkEducation", "ReviewSecurity", "ReviewLocation", "SignCertify"]:
            self.usPipe.upload(self.resPublic["aid"], status=4, visa_status=3)
            return 1

        try:
            while self.getNode and self.getNode != 'SignCertify':
                self.progress(nodeInfo[self.getNode])
                if self.nodeDict[self.getNode]():
                    return 1
            if self.getNode == 'SignCertify':
                self.usPipe.upload(self.resPublic["aid"], visa_status="1")
            return 0
        except Exception:
            self.errJson(["信息有误"], nodeInfo[self.getNode])

    # ================== #
    #    各个页面函数    #
    # ================== #

    def personal1(self):
        """ 填写个人信息页一 (Personal1) """
        print("填写个人信息页一 (Personal1)")
        # 拼音姓 拼音名 中文姓名
        ids = [
            (f"{self.baseID}FormView1_tbxAPP_SURNAME", self.resInfo['english_name']),
            (f"{self.baseID}FormView1_tbxAPP_GIVEN_NAME", self.resInfo['english_name_s']),
            (f"{self.baseID}FormView1_tbxAPP_FULL_NAME_NATIVE", self.resInfo['username'])
        ]

        # 判断是否有曾用名
        if self.resInfo['former_name_is'] == "N":
            ids.append((f"{self.baseID}FormView1_rblOtherNames_1", ""))
        elif self.resInfo['former_name_is'] == "Y":
            surNames = json.loads(self.resInfo['former_name'])
            names = json.loads(self.resInfo['former_names'])
            for index in range(len(names)):
                if index and self.old_page:
                    ids.append((f"{self.baseID}FormView1_DListAlias_ctl0{index}_InsertButtonAlias", ""))
                ids += [
                    (f"{self.baseID}FormView1_rblOtherNames_0", ""),
                    (f"{self.baseID}FormView1_DListAlias_ctl0{index}_tbxSURNAME", surNames[index]),
                    (f"{self.baseID}FormView1_DListAlias_ctl0{index}_tbxGIVEN_NAME", names[index])
                ]

        # 判断是否有中文姓名电码
        if self.resInfo['code_name_is'] == "N":
            ids.append((f"{self.baseID}FormView1_rblTelecodeQuestion_1", ""))
        elif self.resInfo['code_name_is'] == "Y":
            lsCodeName = [
                (f"{self.baseID}FormView1_rblTelecodeQuestion_0", ""),
                (f"{self.baseID}FormView1_tbxAPP_TelecodeSURNAME", self.resInfo['code_name']),
                (f"{self.baseID}FormView1_tbxAPP_TelecodeGIVEN_NAME", self.resInfo['code_names'])
            ]
            ids += lsCodeName

        year, mon, day = self.resInfo['date_of_birth'].split('-')
        # 判断性别-生日 日-月-年
        ids += [
            (f"{self.baseID}FormView1_rblAPP_GENDER_{0 if self.resInfo['sex'] == 'M' else 1}", ""),
            (f"{self.baseID}FormView1_tbxDOBYear", year),
            (f"{self.baseID}FormView1_ddlDOBMonth", MONTH[mon]),
            (f"{self.baseID}FormView1_tbxAPP_POB_CITY", self.resInfo['date_of_address']),
            (f"{self.baseID}FormView1_tbxAPP_POB_ST_PROVINCE", self.resInfo['date_of_province'])
        ]

        # 婚姻状况-国家
        seList = [
            (f"{self.baseID}FormView1_ddlDOBDay", day),
            (f"{self.baseID}FormView1_ddlAPP_MARITAL_STATUS", self.resInfo['marriage']),
            (f"{self.baseID}FormView1_ddlAPP_POB_CNTRY", self.resInfo['date_of_country'])
        ]
        if self.resInfo["marriage"] == "O":
            ids.append((f"{self.baseID}FormView1_tbxOtherMaritalStatus", self.resInfo["marriage_info"]))
        self.waitIdSel(idlist=ids, selist=seList)
        self.urlButton()

        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '个人信息一:')
            return 1
        except Exception:
            pass
        self.progress("5% 个人信息1 完成")
        return 0

    def personal2(self):
        """ 填写个人信息页二 (Personal2) """
        print("填写个人信息页一 (Personal2)")
        self.choiceSelect(f"{self.baseID}FormView1_ddlAPP_NATL", self.resInfo['nationality'])

        self.AAcode = self.driver.find_element_by_id('ctl00_lblAppID').text
        with open("veri.json", "r+") as f:
            if self.AAcode not in f.read():
                f.write(',\n')
                veri = [
                    self.resPublic["id"], 
                    self.AAcode, 
                    self.resInfo["english_name"][:5], 
                    self.resInfo['date_of_birth'].split('-')[0], 
                    self.answer
                    ]
                json.dump(veri, f)
        self.usPipe.upload(self.resPublic['aid'], aacode=self.AAcode)

        ids = []

        # 判断是否拥有其它国籍
        if self.resInfo['nationality_other_is'] == 'N':
            ids.append((f"{self.baseID}FormView1_rblAPP_OTH_NATL_IND_1", ""))
        elif self.resInfo['nationality_other_is'] == 'Y':
            raise UsError("有其他国籍")

        # 判断是否持有其它国家的永久居住权身份
        if self.resInfo['nationality_live_is'] == 'N':
            ids.append((f"{self.baseID}FormView1_rblPermResOtherCntryInd_1", ""))
        elif self.resInfo['nationality_live_is'] == 'Y':
            raise UsError("持有其它国家的永久居住权身份")

        # 身份证号
        if self.resInfo['identity_number']:
            ids.append((f"{self.baseID}FormView1_tbxAPP_NATIONAL_ID", self.resInfo['identity_number']))
        # if self.resPublic['pay_personal_address']:
        #     ids.append((f"{self.baseID}FormView1_tbxAPP_NATIONAL_ID", self.resPublic['pay_personal_address']))
        else:
            ids.append((f"{self.baseID}FormView1_cbexAPP_NATIONAL_ID_NA", ""))

        # 美国安全号
        if self.resInfo['social_security_number']:
            ids += [
                (f"{self.baseID}FormView1_tbxAPP_SSN1", self.resInfo['social_security_number'][:3]),
                (f"{self.baseID}FormView1_tbxAPP_SSN2", self.resInfo['social_security_number'][3:5]),
                (f"{self.baseID}FormView1_tbxAPP_SSN3", self.resInfo['social_security_number'][5:9]),
            ]
        else:
            ids.append((f"{self.baseID}FormView1_cbexAPP_SSN_NA", ""))

        # 美国纳税人身份号
        if self.resInfo['taxpayer_number']:
            ids.append((f"{self.baseID}FormView1_tbxAPP_TAX_ID", self.resInfo['taxpayer_number']))
        else:
            ids.append((f"{self.baseID}FormView1_cbexAPP_TAX_ID_NA", ""))

        self.waitIdSel(idlist=ids)

        self.urlButton()

        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '个人信息二:')
            return 1
        except Exception:
            pass

        self.progress("10% 个人信息2 完成")

        return 0

    def addPhone(self):
        """ 地址和电话页 """
        print("地址和电话页")
        # 街道/城市
        ids = [
            (f"{self.baseID}FormView1_tbxAPP_ADDR_LN1", self.resInfo['live_address'][:40]),
            (f"{self.baseID}FormView1_tbxAPP_ADDR_LN2", self.resInfo['live_address'][40:]),
            (f"{self.baseID}FormView1_tbxAPP_ADDR_CITY", self.resInfo['m_city']),
        ]
        seList = []
        # 省份
        if self.resInfo['province']:
            ids.append((f"{self.baseID}FormView1_tbxAPP_ADDR_STATE", self.resInfo['province']))
        else:
            ids.append((f"{self.baseID}FormView1_cbexAPP_ADDR_STATE_NA", ""))
        # 邮编
        if self.resInfo['zip_code']:
            ids.append((f"{self.baseID}FormView1_tbxAPP_ADDR_POSTAL_CD", self.resInfo['zip_code']))
        else:
            ids.append((f"{self.baseID}FormView1_cbexAPP_ADDR_POSTAL_CD_NA", ""))

        # 国家
        self.choiceSelect(f"{self.baseID}FormView1_ddlCountry", self.resInfo['date_of_country'])

        # 邮寄地址
        if self.resInfo['mailing_address_is'] == 'Y':
            ids.append((f"{self.baseID}FormView1_rblMailingAddrSame_0", ""))
        elif self.resInfo['mailing_address_is'] == 'N':
            ids += [
                (f"{self.baseID}FormView1_rblMailingAddrSame_1", ""),
                (f"{self.baseID}FormView1_tbxMAILING_ADDR_LN1", self.resInfo['mailing_address'][:40]),
                (f"{self.baseID}FormView1_tbxMAILING_ADDR_LN2", self.resInfo['mailing_address'][40:]),
                (f"{self.baseID}FormView1_tbxMAILING_ADDR_CITY", self.resInfo['mailing_address_city']),
            ]
            # 省份
            if self.resInfo['mailing_address_province']:
                ids.append((f"{self.baseID}FormView1_tbxMAILING_ADDR_STATE", self.resInfo['mailing_address_province']))
            else:
                ids.append((f"{self.baseID}FormView1_cbexMAILING_ADDR_STATE_NA", ""))
            # 邮编
            if self.resInfo['mailing_address_zip']:
                ids.append((f"{self.baseID}FormView1_tbxMAILING_ADDR_POSTAL_CD", self.resInfo['mailing_address_zip']))
            else:
                ids.append((f"{self.baseID}FormView1_cbexMAILING_ADDR_POSTAL_CD_NA", ""))

            seList.append((f"{self.baseID}FormView1_ddlMailCountry", self.resInfo['mailing_address_nationality']))

        # 主要电话
        ids.append((f"{self.baseID}FormView1_tbxAPP_HOME_TEL", self.cos(self.resInfo['home_telphone'], 0)))
        # 次要电话
        if self.resInfo['tel']:
            ids.append((f"{self.baseID}FormView1_tbxAPP_MOBILE_TEL", self.cos(self.resInfo['tel'], 0)))
        else:
            ids.append((f"{self.baseID}FormView1_cbexAPP_MOBILE_TEL_NA", ""))
        # 工作电话
        if self.resInfo['company_phone']:
            ids.append((f"{self.baseID}FormView1_tbxAPP_BUS_TEL", self.cos(self.resInfo['company_phone'], 0)))
        else:
            ids.append((f"{self.baseID}FormView1_cbexAPP_BUS_TEL_NA", ""))

        self.waitIdSel(idlist=ids, selist=seList)
        self.Wait(f"{self.baseID}FormView1_tbxAPP_EMAIL_ADDR", self.resInfo['home_email'])
        self.urlButton()

        while True:
            try:
                errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
                assert len(errInfos) > 1
                if "Email Address is invalid. Verify the format is correct." == errInfos[1]:
                    self.driver.find_element("id", f"{self.baseID}FormView1_tbxAPP_EMAIL_ADDR").clear()
                    self.Wait(f"{self.baseID}FormView1_tbxAPP_EMAIL_ADDR", self.resInfo['home_email'])
                    self.Wait(f"{self.baseID}UpdateButton3")
                else:
                    self.errJson(errInfos, '地址和电话:')
                    return 1
            except Exception:
                break

        self.progress("15% 地址和电话页 完成")

        return 0

    def pptVisa(self):
        """ 护照页 """
        print("护照")
        ids = []
        seList = []
        # 护照本编号「默认不填」
        if self.resInfo['passport_papers_number']:
            ids.append((f"{self.baseID}FormView1_tbxPPT_BOOK_NUM", self.resInfo['passport_papers_number']))
        else:
            ids.append(
                (f"{self.baseID}FormView1_cbexPPT_BOOK_NUM_NA", ""))

        iYear, iMon, iDay = self.resInfo['lssue_date'].split('-')
        eYear, eMon, eDay = self.resInfo['expiration_date'].split('-')
        print(eYear, eMon, eDay)
        ids += [
            #　护照类型/护照号
            (f"{self.baseID}FormView1_tbxPPT_NUM", self.cos(self.resInfo['passport_number'])),
            # (f"{self.baseID}FormView1_cbexPPT_BOOK_NUM_NA", ""),
            # 护照签发城市
            (f"{self.baseID}FormView1_tbxPPT_ISSUED_IN_CITY", self.resInfo['place_of_issue']),
            # 护照签发省
            (f"{self.baseID}FormView1_tbxPPT_ISSUED_IN_STATE", self.resInfo['place_issue_province']),
            # 护照 签发日期
            (f"{self.baseID}FormView1_ddlPPT_TYPE", self.resInfo['passport_category']),
            (f"{self.baseID}FormView1_tbxPPT_ISSUEDYear", iYear),
            (f"{self.baseID}FormView1_ddlPPT_ISSUED_DTEMonth", MONTH[iMon]),
            # 护照 失效日期
            (f"{self.baseID}FormView1_tbxPPT_EXPIREYear", eYear),
            (f"{self.baseID}FormView1_ddlPPT_EXPIRE_DTEMonth", MONTH[eMon]),
        ]
        seList += [
            (f"{self.baseID}FormView1_ddlPPT_ISSUED_DTEDay", iDay),
            (f"{self.baseID}FormView1_ddlPPT_EXPIRE_DTEDay", eDay),
        ]
        # 护照是否遗失或被盗过
        if self.resInfo['passport_loss'] == 'N':
            ids.append((f"{self.baseID}FormView1_rblLOST_PPT_IND_1", ""))
        elif self.resInfo['passport_loss'] == 'Y':
            ids.append((f"{self.baseID}FormView1_rblLOST_PPT_IND_0", ""))
            for index, value in enumerate(json.loads(self.resInfo["passport_loss_yes"])):
                if index and self.old_page:
                    ids.append((f"{self.baseID}FormView1_dtlLostPPT_ctl0{index - 1}_InsertButtonLostPPT", ""))
                # 是否记得护照号
                if value["number"]:
                    ids.append((f"{self.baseID}FormView1_dtlLostPPT_ctl0{index}_tbxLOST_PPT_NUM", value["number"]))
                else:  # 忘记了/未知的
                    ids.append((f"{self.baseID}FormView1_dtlLostPPT_ctl0{index}_cbxLOST_PPT_NUM_UNKN_IND", ""))
                ids.append((f"{self.baseID}FormView1_dtlLostPPT_ctl0{index}_tbxLOST_PPT_EXPL", value["infos"]))
                seList += [(f"{self.baseID}FormView1_dtlLostPPT_ctl00_ddlLOST_PPT_NATL", value["office"])]
                ids = self.waitIdSel(ids)

        self.waitIdSel(selist=seList)
        self.Wait(f"{self.baseID}FormView1_tbxPPT_ISSUEDYear")
        self.waitIdSel(ids)

        # self.choiceSelect(sel[0], sel[1])
        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '护照:')
            return 1
        except Exception:
            pass

        self.progress("20% 护照页 完成" )

        return 0

    def travel(self):
        """ 旅行页 """
        print("旅行页")
        ids = []
        seList = []
        purpose = json.loads(self.resPublic['america_purpose'])
        for index, value in enumerate(purpose):
            if index and self.old_page:
                seList.append((f"{self.baseID}FormView1_dlPrincipalAppTravel_ctl0{index - 1}_InsertButtonAlias", ""))
            seList += [
                (f"{self.baseID}FormView1_dlPrincipalAppTravel_ctl0{index}_ddlPurposeOfTrip", value["one"]),
                (f"{self.baseID}FormView1_dlPrincipalAppTravel_ctl0{index}_ddlOtherPurpose", value["two"]),
            ]
            seList = self.waitIdSel(selist=seList)
        sleep(1)
        sel = Select(self.driver.find_element_by_id(f"{self.baseID}FormView1_ddlWhoIsPaying"))
        sel.select_by_value(self.resPublic['travel_cost_pay'])

        # is_child = False
        # birth = self.resInfo["date_of_birth"]

        if self.resPublic['travel_plans_is'] == "N":
            year, mon, day = self.resPublic['arrive_time'].split('-')
            try:
                self.driver.find_element_by_id(f"{self.baseID}FormView1_rblSpecificTravel_1").click()
            except Exception:
                pass
            ids = [
                (f"{self.baseID}FormView1_tbxTRAVEL_DTEYear", year),
                (f"{self.baseID}FormView1_ddlTRAVEL_DTEMonth", MONTH[mon]),
                (f"{self.baseID}FormView1_tbxTRAVEL_LOS", self.resPublic['stay_time']),
            ]
            ids = self.waitIdSel(ids)

            self.choiceSelect(f"{self.baseID}FormView1_ddlTRAVEL_DTEDay", f"{int(day)}")
            self.choiceSelect(f"{self.baseID}FormView1_ddlTRAVEL_LOS_CD", self.resPublic['stay_times'])

        elif self.resPublic['travel_plans_is'] == "Y":
            # 到达美国日期/航班/到达城市/离美日期/航班/离美城市/请提供您在美期间计划访问的地点名称
            plans = json.loads(self.resPublic['plans_info'])
            aYear, aMon, aDay = plans["arrive_time"].split('-')
            dYear, dMon, dDay = plans["leave_time"].split('-')
            ids += [
                (f"{self.baseID}FormView1_rblSpecificTravel_0", ""),
                (f"{self.baseID}FormView1_tbxARRIVAL_US_DTEYear", aYear),
                (f"{self.baseID}FormView1_ddlARRIVAL_US_DTEMonth", MONTH[aMon]),
                (f"{self.baseID}FormView1_tbxArriveFlight", plans["arrive_fly"]),
                (f"{self.baseID}FormView1_tbxArriveCity", plans["arrive_city"]),
                (f"{self.baseID}FormView1_tbxDEPARTURE_US_DTEYear", dYear),
                (f"{self.baseID}FormView1_ddlDEPARTURE_US_DTEMonth", MONTH[dMon]),
                (f"{self.baseID}FormView1_tbxDepartFlight", plans["leave_fly"]),
                (f"{self.baseID}FormView1_tbxDepartCity", plans["leave_city"]),
            ]
            seList = [
                (f"{self.baseID}FormView1_ddlARRIVAL_US_DTEDay", f"{int(aDay)}"),
                (f"{self.baseID}FormView1_ddlDEPARTURE_US_DTEDay", f"{int(dDay)}")
            ]
            for index, value in enumerate(json.loads(self.resPublic["plans_access"])):
                if index and self.old_page:
                    ids.append((f"{self.baseID}FormView1_dtlTravelLoc_ctl0{index - 1}_InsertButtonTravelLoc", ""))
                ids.append((f"{self.baseID}FormView1_dtlTravelLoc_ctl0{index}_tbxSPECTRAVEL_LOCATION", value["city"]))
            try:
                ids = self.waitIdSel(ids, seList)
                seList = []
            except Exception:
                year, mon, day = self.resPublic['arrive_time'].split('-')
                ids = [
                    (f"{self.baseID}FormView1_tbxTRAVEL_DTEYear", year),
                    (f"{self.baseID}FormView1_ddlTRAVEL_DTEMonth", MONTH[mon]),
                    (f"{self.baseID}FormView1_tbxTRAVEL_LOS", self.resPublic['stay_time']),
                ]
                ids = self.waitIdSel(ids)
                self.choiceSelect(f"{self.baseID}FormView1_ddlTRAVEL_DTEDay", f"{int(day)}")
                self.choiceSelect(f"{self.baseID}FormView1_ddlTRAVEL_LOS_CD", self.resPublic['stay_times'])

        # 在美停留期间的住址
        ids += [
            (f"{self.baseID}FormView1_tbxStreetAddress1", self.resPublic['stay_address'][:40]),
            (f"{self.baseID}FormView1_tbxStreetAddress2", self.resPublic['stay_address'][40:]),
            (f"{self.baseID}FormView1_tbxCity", self.resPublic['stay_city']),
            (f"{self.baseID}FormView1_tbZIPCode", self.resPublic['stay_zip']),
        ]
        ids = self.waitIdSel(ids)
        if self.resPublic['travel_cost_pay'] == 'O':
            try: self.Wait(f"{self.baseID}FormView1_tbxPayerSurname", self.resPublic['pay_personal_name'])
            except Exception: 
                sel.select_by_index(0)
                sel.select_by_value(self.resPublic['travel_cost_pay'])
                ids.append((f"{self.baseID}FormView1_tbxPayerSurname", self.resPublic['pay_personal_name']))
            ids += [
                (f"{self.baseID}FormView1_tbxPayerGivenName", self.resPublic['pay_personal_names']),
                (f"{self.baseID}FormView1_tbxPayerPhone", self.cos(self.resPublic['pay_personal_phone'], 0)),
                (f"{self.baseID}FormView1_tbxPayerPhone", self.cos(self.resPublic['pay_personal_phone'], 0)),
            ]
            if self.resPublic['pay_personal_email']:
                ids.append((f"{self.baseID}FormView1_tbxPAYER_EMAIL_ADDR", self.resPublic['pay_personal_email']))
            else:
                ids.append((f"{self.baseID}FormView1_cbxDNAPAYER_EMAIL_ADDR_NA", ""))
            # 与您的关系
            ids = self.waitIdSel(ids)
            # self.choiceSelect(f"{self.baseID}FormView1_ddlPayerRelationship", self.resPublic['pay_personal_relation'])
            s = Select(self.driver.find_element_by_id(f"{self.baseID}FormView1_ddlPayerRelationship"))
            s.select_by_value(self.resPublic['pay_personal_relation'])
            # 为您支付旅行费用的一方，其地址是否与您的家庭地址或邮寄地址相同？
            if self.resPublic['pay_personal_address_is'] == 'Y':
                ids.append((f"{self.baseID}FormView1_rblPayerAddrSameAsInd_0", ""))
            elif self.resPublic['pay_personal_address_is'] == 'N':
                ids += [
                    (f"{self.baseID}FormView1_rblPayerAddrSameAsInd_1", ""),
                    (f"{self.baseID}FormView1_tbxPayerStreetAddress1", self.resPublic['pay_personal_address'][:40]),
                    (f"{self.baseID}FormView1_tbxPayerStreetAddress2", self.resPublic['pay_personal_address'][40:]),
                    (f"{self.baseID}FormView1_tbxPayerCity", self.resPublic['pay_personal_city']),
                ]
                if self.resPublic['pay_personal_province']:
                    ids.append((f"{self.baseID}FormView1_tbxPayerStateProvince",self.resPublic['pay_personal_province']))
                else:
                    ids.append((f"{self.baseID}FormView1_cbxDNAPayerStateProvince", ""))
                if self.resPublic['pay_personal_zip']:
                    ids.append((f"{self.baseID}FormView1_tbxPayerPostalZIPCode",self.resPublic['pay_personal_zip']))
                else:
                    ids.append((f"{self.baseID}FormView1_cbxDNAPayerPostalZIPCode", ""))

                ids = self.waitIdSel(ids)
                self.choiceSelect(f"{self.baseID}FormView1_ddlPayerCountry", self.resPublic['pay_personal_country'])
            else:
                self.errJson(["为您支付旅行费用的一方未填写"], '同行人:')
        # 其它公司机构
        if self.resPublic['travel_cost_pay'] == 'C':
            ids += [
                # 承担您旅行费用的公司或组织名称
                (f"{self.baseID}FormView1_tbxPayingCompany", self.cos(self.resPublic["pay_group_name"])),
                # 电话号码
                (f"{self.baseID}FormView1_tbxPayerPhone", self.cos(self.resPublic["pay_group_phone"], 0)),
                # 与您的关系
                (f"{self.baseID}FormView1_tbxCompanyRelation", self.resPublic["pay_group_relation"]),
                # 街道地址（第一行）
                (f"{self.baseID}FormView1_tbxPayerStreetAddress1", self.resPublic["pay_group_address"][:40]),
                # 街道地址（第二行）
                (f"{self.baseID}FormView1_tbxPayerStreetAddress2", self.resPublic["pay_group_address"][40:]),
                # 城市
                (f"{self.baseID}FormView1_tbxPayerCity", self.resPublic["pay_group_city"]),
            ]
            # 州/省份
            if "N":
                ids.append((f"{self.baseID}FormView1_cbxDNAPayerStateProvince", ""))
            elif "Y":
                ids.append((f"{self.baseID}FormView1_tbxPayerStateProvince", self.resPublic["pay_group_province"]))

            # 邮政区域/邮政编码
            if "N":
                ids.append((f"{self.baseID}FormView1_cbxDNAPayerPostalZIPCode", ""))
            elif "Y":
                ids.append((f"{self.baseID}FormView1_tbxPayerPostalZIPCode", self.resPublic["pay_group_zip"]))
            # 国家/地区
            seList += [(f"{self.baseID}FormView1_ddlPayerCountry", self.resPublic["pay_group_country"])]
        ids = self.waitIdSel(ids, seList)

        # 州
        self.choiceSelect(f"{self.baseID}FormView1_ddlTravelState", self.resPublic['stay_province'])
        sleep(1)
        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '旅行:')
            return 1
        except Exception:
            pass

        self.progress("25% 旅行页 完成")

        return 0

    def travelCompanions(self):
        """ 旅行同伴页 """
        print('旅行同伴页')
        if self.resPublic["associate_is"] == "N":
            self.Wait(f"{self.baseID}FormView1_rblOtherPersonsTravelingWithYou_1")
        elif self.resPublic["associate_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblOtherPersonsTravelingWithYou_0")
            # 您是否作为一个团队或者组织的成员去旅行？
            if self.resPublic["associate_tuxedo_is"] == 'Y':
                self.Wait(f"{self.baseID}FormView1_rblGroupTravel_0", "")
                self.Wait(f"{self.baseID}FormView1_tbxGroupName", self.resPublic["associate_tuxedo_name"])
            elif self.resPublic["associate_tuxedo_is"] == 'N':
                self.Wait(f"{self.baseID}FormView1_rblGroupTravel_1")
                # 同行人姓(拼音) 、同行人名(拼音) 、 关系
                associate = json.loads(self.resPublic["associate_name_relation"])
                for index, value in enumerate(associate):
                    if index and self.old_page:
                        self.Wait(f"{self.baseID}FormView1_dlTravelCompanions_ctl0{index - 1}_InsertButtonPrincipalPOT")
                    self.Wait(f"{self.baseID}FormView1_dlTravelCompanions_ctl0{index}_tbxSurname", value['name'])
                    self.Wait(f"{self.baseID}FormView1_dlTravelCompanions_ctl0{index}_tbxGivenName", value['names'])
                    self.choiceSelect(f"{self.baseID}FormView1_dlTravelCompanions_ctl0{index}_ddlTCRelationship", value['relation'][0])

        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '同行人:')
            return 1
        except Exception:
            pass

        self.progress("30% 旅行同伴页 完成")
        return 0

    def previousUSTravel(self):
        """ 以前美国之行 """
        print("以前美国之行")
        # 您是否曾经在美国停留过？
        if self.resPublic["old_stay_is"] == 'N':
            self.Wait(f"{self.baseID}FormView1_rblPREV_US_TRAVEL_IND_1")
        elif self.resPublic["old_stay_is"] == 'Y':
            self.Wait(f"{self.baseID}FormView1_rblPREV_US_TRAVEL_IND_0")
            """ 
            {"arrived":[{"arrived_time":"2004-10-12","time":"12","times":"\u5929"},{"arrived_time":"2004-10-13","time":"12","times":"\u5929"}]}
             """
            stay_info = json.loads(self.resPublic["old_stay_info"]).get("arrived")
            # 抵达日期
            for index, value in enumerate(stay_info):
                year, month, day = value["arrived_time"].split("-")
                if index and self.old_page:
                    self.Wait(f"{self.baseID}FormView1_dtlPREV_US_VISIT_ctl0{index-1}_InsertButtonPREV_US_VISIT")
                self.choiceSelect(f"{self.baseID}FormView1_dtlPREV_US_VISIT_ctl0{index}_ddlPREV_US_VISIT_DTEDay", f"{int(day)}")
                self.Wait(f"{self.baseID}FormView1_dtlPREV_US_VISIT_ctl0{index}_ddlPREV_US_VISIT_DTEMonth", MONTH[month])
                self.Wait(f"{self.baseID}FormView1_dtlPREV_US_VISIT_ctl0{index}_tbxPREV_US_VISIT_DTEYear", year)
                self.Wait(f"{self.baseID}FormView1_dtlPREV_US_VISIT_ctl0{index}_tbxPREV_US_VISIT_LOS", value["time"])
                self.choiceSelect(f"{self.baseID}FormView1_dtlPREV_US_VISIT_ctl0{index}_ddlPREV_US_VISIT_LOS_CD", value["times"])

            # 您是否持有或者曾经持有美国驾照
            driver = json.loads(self.resPublic["old_stay_info"]).get("驾照")
            if not driver:
                self.Wait(f"{self.baseID}FormView1_rblPREV_US_DRIVER_LIC_IND_1")
            elif driver:
                self.Wait(f"{self.baseID}FormView1_rblPREV_US_DRIVER_LIC_IND_0")
                for index, value in enumerate(driver):
                    if index and self.old_page:
                        self.Wait(f"{self.baseID}FormView1_dtlUS_DRIVER_LICENSE_ctl0{index-1}_InsertButtonUS_DRIVER_LICENSE")
                    if "驾照号":
                        self.Wait(f"{self.baseID}FormView1_dtlUS_DRIVER_LICENSE_ctl0{index}_tbxUS_DRIVER_LICENSE", value["驾照号"]) # 驾照号
                    else:
                        self.Wait(f"{self.baseID}FormView1_dtlUS_DRIVER_LICENSE_ctl0{index}_cbxUS_DRIVER_LICENSE_NA")
                    self.choiceSelect(f"{self.baseID}FormView1_dtlUS_DRIVER_LICENSE_ctl0{index}_ddlUS_DRIVER_LICENSE_STATE", value["驾照所属州"]) # 驾照所属州

        # 您是否曾经获得过美国签证?
        if self.resPublic["old_visa_is"] == 'N':
            self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_IND_1")
        elif self.resPublic["old_visa_is"] == 'Y':
            self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_IND_0")
            year, month, day = self.resPublic["old_visa_time"].split("-")
            self.choiceSelect(f"{self.baseID}FormView1_ddlPREV_VISA_ISSUED_DTEDay", f"{int(day)}")
            self.Wait(f"{self.baseID}FormView1_ddlPREV_VISA_ISSUED_DTEMonth", MONTH[month])
            self.Wait(f"{self.baseID}FormView1_tbxPREV_VISA_ISSUED_DTEYear", year)
            # 签证号码
            if self.resPublic["old_visa_number"]:
                self.Wait(f"{self.baseID}FormView1_tbxPREV_VISA_FOIL_NUMBER", self.resPublic["old_visa_number"])
            else:
                self.Wait(f"{self.baseID}FormView1_cbxPREV_VISA_FOIL_NUMBER_NA")

            # 您此次是否申请同类签证？
            if self.resPublic["old_visa_type_is"] == "N":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_SAME_TYPE_IND_1")
            elif self.resPublic["old_visa_type_is"] == "Y":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_SAME_TYPE_IND_0")

            # 您现在申请签证的所在国家或地点同于您上个签证颁发所在国或地点吗? 此国家或地点是您主要居住地吗?
            if self.resPublic["old_visa_country_is"] == "N":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_SAME_CNTRY_IND_1")
            elif self.resPublic["old_visa_country_is"] == "Y":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_SAME_CNTRY_IND_0")

            # 您是否留取过十指指纹？
            if self.resPublic["old_visa_fingerprint_is"] == "N":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_TEN_PRINT_IND_1")
            elif self.resPublic["old_visa_fingerprint_is"] == "Y":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_TEN_PRINT_IND_0")

            # 您的美国签证是否曾经遗失或者被盗？
            if self.resPublic["old_visa_lost_is"] == "N":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_LOST_IND_1")
            elif self.resPublic["old_visa_lost_is"] == "Y":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_LOST_IND_0")
                self.Wait(f"{self.baseID}FormView1_tbxPREV_VISA_LOST_YEAR", self.resPublic["old_visa_lost_time"])
                self.Wait(f"{self.baseID}FormView1_tbxPREV_VISA_LOST_EXPL", self.resPublic["old_visa_lost_info"])

            # 您的美国签证是否曾经被注销或撤销过？
            if self.resPublic["old_visa_undo_is"] == "N":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_CANCELLED_IND_1")
            elif self.resPublic["old_visa_undo_is"] == "Y":
                self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_CANCELLED_IND_0")
                self.Wait(f"{self.baseID}FormView1_tbxPREV_VISA_CANCELLED_EXPL", self.resPublic["old_visa_undo_info"])

        # 您被拒签过吗？ 或在入境口岸被拒入境，或被撤销入境申请？
        if self.resPublic["old_visa_refused_is"] == 'Y':
            self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_REFUSED_IND_0")
            self.Wait(f"{self.baseID}FormView1_tbxPREV_VISA_REFUSED_EXPL", self.resPublic['old_visa_refused_info'])
        elif self.resPublic["old_visa_refused_is"] == 'N':
            self.Wait(f"{self.baseID}FormView1_rblPREV_VISA_REFUSED_IND_1")

        # 曾有人在公民及移民服务局为您申请过移民吗？
        if self.resPublic["old_visa_emigrate_is"] == 'Y':
            self.Wait(f"{self.baseID}FormView1_rblIV_PETITION_IND_0")
            self.Wait(f"{self.baseID}FormView1_tbxIV_PETITION_EXPL", self.resPublic['old_visa_emigrate_info'])
        elif self.resPublic["old_visa_emigrate_is"] == 'N':
            self.Wait(f"{self.baseID}FormView1_rblIV_PETITION_IND_1")

        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '以往赴美:')
            return 1
        except Exception:
            pass

        self.progress("35% 以前美国之行 完成")

        return 0

    def usContact(self):
        """ 美国联系人信息 """
        print("美国联系人信息")
        self.choiceSelect(f"{self.baseID}FormView1_ddlUS_POC_REL_TO_APP", self.resPublic["contact_relation"])

        ids = [
            (f"{self.baseID}FormView1_tbxUS_POC_ADDR_LN1", self.resPublic["contact_address"][:40]),
            (f"{self.baseID}FormView1_tbxUS_POC_ADDR_LN2", self.resPublic["contact_address"][40:]),
            (f"{self.baseID}FormView1_tbxUS_POC_ADDR_CITY", self.resPublic["contact_city"]),
            (f"{self.baseID}FormView1_tbxUS_POC_ADDR_POSTAL_CD", self.resPublic["contact_zip"]),
            (f"{self.baseID}FormView1_tbxUS_POC_HOME_TEL", self.cos(self.resPublic["contact_phone"], 0)),

        ]

        if self.resPublic["contact_email"]:
            ids.append((f"{self.baseID}FormView1_tbxUS_POC_EMAIL_ADDR", self.resPublic["contact_email"]))
        else:
            ids.append((f"{self.baseID}FormView1_cbexUS_POC_EMAIL_ADDR_NA", ""))

        if self.resPublic["contact_name"] and self.resPublic["contact_names"]:
            self.Wait(f"{self.baseID}FormView1_cbxUS_POC_ORG_NA_IND")
            ids += [
                (f"{self.baseID}FormView1_tbxUS_POC_SURNAME", self.resPublic["contact_name"]),
                (f"{self.baseID}FormView1_tbxUS_POC_GIVEN_NAME", self.resPublic["contact_names"]),
            ]
        else:
            self.Wait(f"{self.baseID}FormView1_cbxUS_POC_NAME_NA")
            ids += [
                (f"{self.baseID}FormView1_tbxUS_POC_ORGANIZATION", self.resPublic["contact_group_name"])
            ]

        sleep(1)
        self.waitIdSel(ids)
        self.choiceSelect(f"{self.baseID}FormView1_ddlUS_POC_ADDR_STATE", self.resPublic["contact_province"])
        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '美国联系人信息:')
            return 1
        except Exception:
            pass

        self.progress("40% 美国联系人信息 完成")

        return 0

    def relatives(self):
        ''' 家庭/亲属 '''
        print("家庭/亲属")
        ids = []
        seList = []
        # 父亲
        if not (self.resInfo['father_name'] or self.resInfo['father_names']):
            ids += [
                (f"{self.baseID}FormView1_cbxFATHER_SURNAME_UNK_IND", ""),
                (f"{self.baseID}FormView1_cbxFATHER_GIVEN_NAME_UNK_IND", ""),
            ]
        else:
            ids += [
                (f"{self.baseID}FormView1_tbxFATHER_SURNAME", self.resInfo["father_name"]),
                (f"{self.baseID}FormView1_tbxFATHER_GIVEN_NAME", self.resInfo["father_names"]),
            ]
            if not self.resInfo["father_birth"]:
                ids.append((f"{self.baseID}FormView1_cbxFATHER_DOB_UNK_IND", ""))
            else:
                year, month, day = self.resInfo["father_birth"].split("-")
                ids += [
                    (f"{self.baseID}FormView1_tbxFathersDOBYear", year),
                    (f"{self.baseID}FormView1_ddlFathersDOBMonth",
                     MONTH[month]),
                ]
                seList.append((f"{self.baseID}FormView1_ddlFathersDOBDay", day))
        seList = self.waitIdSel(selist=seList)
        ids = self.waitIdSel(ids)
        # 母亲
        if not (self.resInfo['mother_name'] or self.resInfo['mother_names']):
            ids += [
                (f"{self.baseID}FormView1_cbxMOTHER_SURNAME_UNK_IND", ""),
                (f"{self.baseID}FormView1_cbxMOTHER_GIVEN_NAME_UNK_IND", ""),
            ]
        else:
            ids += [
                (f"{self.baseID}FormView1_tbxMOTHER_SURNAME", self.resInfo["mother_name"]),
                (f"{self.baseID}FormView1_tbxMOTHER_GIVEN_NAME", self.resInfo["mother_names"]),
            ]
            if not self.resInfo["mother_birth"]:
                ids.append((f"{self.baseID}FormView1_cbxMOTHER_DOB_UNK_IND", ""))
            else:
                year, month, day = self.resInfo["mother_birth"].split("-")
                ids += [
                    (f"{self.baseID}FormView1_tbxMothersDOBYear", year),
                    (f"{self.baseID}FormView1_ddlMothersDOBMonth",
                     MONTH[month]),
                ]
                seList.append((f"{self.baseID}FormView1_ddlMothersDOBDay", day))

        seList = self.waitIdSel(selist=seList)
        ids = self.waitIdSel(ids)

        # 父母是否在美国
        if self.resInfo["father_america_is"] == "N":
            self.driver.execute_script(f'document.getElementById("{self.baseID}FormView1_rblFATHER_LIVE_IN_US_IND_1").checked = true')
        elif self.resInfo["father_america_is"] == "Y":
            ids += [
                (f"{self.baseID}FormView1_rblFATHER_LIVE_IN_US_IND_0", ""),
                (f"{self.baseID}FormView1_ddlFATHER_US_STATUS", self.resInfo["father_america_identity"])
            ]
        if self.resInfo["mother_america_is"] == "N":
            self.driver.execute_script(f'document.getElementById("{self.baseID}FormView1_rblMOTHER_LIVE_IN_US_IND_1").checked = true')
        elif self.resInfo["mother_america_is"] == "Y":
            ids += [
                (f"{self.baseID}FormView1_rblMOTHER_LIVE_IN_US_IND_0", ""),
                (f"{self.baseID}FormView1_ddlMOTHER_US_STATUS", self.resInfo["mother_america_identity"])
            ]
        ids = self.waitIdSel(ids)

        # 其它直系亲属
        if self.resInfo["other_america_is"] == "N":
            ids.append((f"{self.baseID}FormView1_rblUS_IMMED_RELATIVE_IND_1", ""))
            if self.resInfo["others_america_is"] == "Y":
                ids.append((f"{self.baseID}FormView1_rblUS_OTHER_RELATIVE_IND_0", ""))
            elif self.resInfo["others_america_is"] == "N":
                ids.append((f"{self.baseID}FormView1_rblUS_OTHER_RELATIVE_IND_1", ""))
        elif self.resInfo["other_america_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblUS_IMMED_RELATIVE_IND_0")
            immediate_family = json.loads(self.resInfo["immediate_family"])
            for index, val in enumerate(immediate_family):
                if index and self.old_page:
                    self.Wait(f"{self.baseID}FormView1_dlUSRelatives_ctl0{index - 1}_InsertButtonUSRelative")
                ids += [
                    # 姓氏
                    (f"{self.baseID}FormView1_dlUSRelatives_ctl00_tbxUS_REL_SURNAME", val["name"]),
                    # 名字
                    (f"{self.baseID}FormView1_dlUSRelatives_ctl00_tbxUS_REL_GIVEN_NAME", val["names"]),
                ]
                seList += [
                    # 与您的关系
                    (f"{self.baseID}FormView1_dlUSRelatives_ctl00_ddlUS_REL_TYPE", val["relation"]),
                    # 在美身份
                    (f"{self.baseID}FormView1_dlUSRelatives_ctl00_ddlUS_REL_STATUS", val["identity"]),
                ]

        seList = self.waitIdSel(selist=seList)
        ids = self.waitIdSel(ids)
        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '家庭/亲属:')
            return 1
        except Exception:
            pass

        self.progress("45% 家庭/亲属页 完成")

        return 0

    def family(self):
        familyDict = {
            "M": self.spouse,
            "C": self.spouse,
            "P": self.spouse,
            "S": lambda: 0,
            "O": lambda: 0,
            "L": self.spouse,
            "W": self.deceasedSpouse,
            "D": self.prevSpouse,
        }
        node = self.getNode
        if self.resInfo["marriage"] in ["S", "O"] or (self.resInfo["marriage"] in ["M", "C", "P", "L"] and node != "Spouse") or (self.resInfo["marriage"] == "W" and node != "DeceasedSpouse") or (self.resInfo["marriage"] == "D" and node != "PrevSpouse"):
            self.driver.get("https://ceac.state.gov/GenNIV/General/complete/complete_personal.aspx?node=Personal1")
            self.choiceSelect("ctl00_SiteContentPlaceHolder_FormView1_ddlAPP_MARITAL_STATUS", self.resInfo["marriage"])
            if self.resInfo["marriage"] == "O":
                self.Wait(f"{self.baseID}FormView1_tbxOtherMaritalStatus", self.resInfo["marriage_info"])
            self.urlButton()
            self.driver.get("https://ceac.state.gov/GenNIV/General/complete/complete_family1.aspx?node=Relatives")
            self.urlButton()
        return familyDict[self.resInfo["marriage"]]()

    def spouse(self):
        """ 配偶 """
        print("配偶")
        year, month, day = self.resInfo["spouse_birth"].split("-")
        ids = [
            # 配偶姓氏
            (f"{self.baseID}FormView1_tbxSpouseSurname", self.resInfo["spouse_name"]),
            # 配偶名字
            (f"{self.baseID}FormView1_tbxSpouseGivenName", self.resInfo["spouse_names"]),
            # 配偶生日: 年
            (f"{self.baseID}FormView1_tbxDOBYear", year),
            # 配偶出生城市
            (f"{self.baseID}FormView1_tbxSpousePOBCity", self.resInfo["spouse_birth_city"]),
            # 配偶生日: 月
            (f"{self.baseID}FormView1_ddlDOBMonth", MONTH[month]),
        ]
        seList = [
            # 配偶生日: 日
            (f"{self.baseID}FormView1_ddlDOBDay", day),
            # 配偶的所属国家/地区（国籍）(比如：中国大陆=“China”)
            (f"{self.baseID}FormView1_ddlSpouseNatDropDownList", self.resInfo["spouse_nation"]),
            # 配偶的出生国家/地区
            (f"{self.baseID}FormView1_ddlSpousePOBCountry", self.resInfo["spouse_birth_country"]),
            # 配偶的联系地址
            (f"{self.baseID}FormView1_ddlSpouseAddressType", self.resInfo["spouse_address_select"]),
        ]
        ids = self.waitIdSel(ids, seList)
        seList = []
        # 配偶地址(选择其它时)
        if self.resInfo["spouse_address_select"] == "O":
            ids += [
                # 街道地址（第一行）
                (f"{self.baseID}FormView1_tbxSPOUSE_ADDR_LN1", self.resInfo["spouse_address"][:40]),
                # 街道地址（第二行）
                (f"{self.baseID}FormView1_tbxSPOUSE_ADDR_LN2", self.resInfo["spouse_address"][40:]),
                # 城市
                (f"{self.baseID}FormView1_tbxSPOUSE_ADDR_CITY", self.resInfo["spouse_address_city"]),
            ]
            if self.resInfo["spouse_address_province"]:
                # 州/省
                ids.append((f"{self.baseID}FormView1_tbxSPOUSE_ADDR_STATE", self.resInfo["spouse_address_province"]))
            else:
                ids.append((f"{self.baseID}FormView1_cbexSPOUSE_ADDR_STATE_NA", ""))

            if self.resInfo["spouse_address_code"]:
                # 邮编
                ids.append((f"{self.baseID}FormView1_tbxSPOUSE_ADDR_POSTAL_CD", self.resInfo["spouse_address_code"]))
            else:
                ids.append((f"{self.baseID}FormView1_cbexSPOUSE_ADDR_POSTAL_CD_NA", ""))
            # 国家
            seList.append((f"{self.baseID}FormView1_ddlSPOUSE_ADDR_CNTRY", self.resInfo["spouse_address_country"]))

        self.waitIdSel(ids, seList)

        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '家庭/配偶:')
            return 1
        except Exception:
            pass

        self.progress("50% 配偶页 完成")

        return 0

    def deceasedSpouse(self):
        """ 丧偶 """
        year, month, day = self.resInfo["spouse_birth"].split("-")
        ids = [
            (f"{self.baseID}FormView1_tbxSURNAME", self.resInfo["spouse_name"]),
            (f"{self.baseID}FormView1_tbxGIVEN_NAME", self.resInfo["spouse_names"]),
            (f"{self.baseID}FormView1_tbxDOBYear", year),
            (f"{self.baseID}FormView1_ddlDOBMonth", MONTH[month]),
        ]
        seList = [(f"{self.baseID}FormView1_ddlDOBDay", day)]
        ids = self.waitIdSel(ids, seList)
        self.choiceSelect(f"{self.baseID}FormView1_ddlSpouseNatDropDownList", self.resInfo["spouse_birth_country"])
        if self.resInfo["spouse_birth_city"]:
            self.Wait(f"{self.baseID}FormView1_tbxSpousePOBCity", self.resInfo["spouse_birth_city"])
        else:
            self.Wait(f"{self.baseID}FormView1_cbxSPOUSE_POB_CITY_NA")
        self.choiceSelect(f"{self.baseID}FormView1_ddlSpousePOBCountry", self.resInfo["spouse_birth_country"])

        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '家庭/配偶「丧偶」:')
            return 1
        except Exception:
            pass

        self.progress("50% 丧偶页 完成")

        return 0

    def prevSpouse(self):
        ''' 离异 '''
        info = json.loads(self.resInfo["spouse_former_info"])
        print("离异人数", self.resInfo["spouse_former_count"])
        self.Wait(f"{self.baseID}FormView1_tbxNumberOfPrevSpouses", str(
            self.resInfo["spouse_former_count"]))
        self.Wait(f"{self.baseID}FormView1_DListSpouse_ctl00_tbxSURNAME", info[0]["former_name"])
        self.Wait(f"{self.baseID}FormView1_DListSpouse_ctl00_tbxGIVEN_NAME", info[0]["former_names"])
        sleep(2)
        for no, human in enumerate(info):
            idName = f"{self.baseID}FormView1_DListSpouse_ctl0{no}_"
            if no and self.old_page:
                self.Wait(f"{idName}InsertButtonSpouse", "")
            year, month, day = human["former_birth_date"].split("-")
            wYear, wMonth, wDay = human["wedding_date"].split("-")
            dYear, dMonth, dDay = human["divorce_date"].split("-")
            self.Wait(f"{idName}tbxSURNAME", human["former_name"])
            self.Wait(f"{idName}tbxGIVEN_NAME", human["former_names"])
            self.choiceSelect(f"{idName}ddlDOBDay", day)
            self.Wait(f"{idName}tbxDOBYear", year)
            self.Wait(f"{idName}ddlDOBMonth", MONTH[month])
            self.choiceSelect(f"{idName}ddlDomDay", str(int(wDay)))
            self.Wait(f"{idName}txtDomYear", wYear)
            self.Wait(f"{idName}ddlDomMonth", MONTH[wMonth])
            self.choiceSelect(f"{idName}ddlDomEndDay", str(int(dDay)))
            self.Wait(f"{idName}txtDomEndYear", dYear)
            self.Wait(f"{idName}ddlDomEndMonth", MONTH[dMonth])
            self.Wait(f"{idName}tbxHowMarriageEnded", human["divorce_info"])
            if human["former_city"]:
                self.Wait(f"{idName}tbxSpousePOBCity", human["former_city"])
            else:
                self.Wait(f"{idName}cbxSPOUSE_POB_CITY_NA", "")
            self.choiceSelect(f"{idName}ddlSpouseNatDropDownList", human["former_country"])
            self.choiceSelect(f"{idName}ddlSpousePOBCountry", human["former_birth_country"])
            self.choiceSelect(f"{idName}ddlMarriageEnded_CNTRY", human["divorce_country"])

        self.urlButton()
        try:
            errInfos = self.Wait(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '离异:')
            return 1
        except Exception:
            pass

        self.progress("50% 离异页 完成")

        return 0

    def workEducation1(self):
        """ 工作教育 """
        print("工作教育")
        over = False
        self.choiceSelect(f"{self.baseID}FormView1_ddlPresentOccupation", self.resWork["professional_types"])
        if self.resWork["professional_types"] == "N":
            self.Wait(f"{self.baseID}FormView1_tbxExplainOtherPresentOccupation", self.resWork["professional_info"])
            over = True
        if self.resWork["professional_types"] == "O":
            self.Wait(f"{self.baseID}FormView1_tbxExplainOtherPresentOccupation", self.resWork["professional_info"])
        if self.resWork["professional_types"] in ["H", "RT"]:
            over = True
        if over:
            self.urlButton()
            try:
                errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
                assert len(errInfos) > 1
                self.errJson(errInfos, '工作教育:')
                return 1
            except Exception:
                pass

            return 0

        seList = []

        year, month, day = self.resWork["induction_time"].split("-") if len(self.resWork["induction_time"]) > 3 else (0, 0, 0)

        ids = [
            # 当前工作单位或学校的名称
            (f"{self.baseID}FormView1_tbxEmpSchName", self.cos(self.resWork["company_name"])),
            # 街道地址（第一行）
            (f"{self.baseID}FormView1_tbxEmpSchAddr1", self.resWork["company_address"].strip()[:40]),
            # 街道地址（第二行）
            (f"{self.baseID}FormView1_tbxEmpSchAddr2", self.resWork["company_address"][40:]),
            # 城市
            (f"{self.baseID}FormView1_tbxEmpSchCity", self.resWork["company_city"]),
            # 电话号码
            (f"{self.baseID}FormView1_tbxWORK_EDUC_TEL", self.cos(self.resWork["company_phone"], 0)),
            # 入职年份
            (f"{self.baseID}FormView1_tbxEmpDateFromYear", year),
            # 所属月份
            (f"{self.baseID}FormView1_ddlEmpDateFromMonth", MONTH[month]),
            # 请简要描述您的工作职责：
            (f"{self.baseID}FormView1_tbxDescribeDuties", self.resWork["responsibility"]),
        ]

        # 州/省份
        if self.resWork["company_province"]:
            ids.append((f"{self.baseID}FormView1_tbxWORK_EDUC_ADDR_STATE", self.resWork["company_province"]))
        else:
            ids.append((f"{self.baseID}FormView1_cbxWORK_EDUC_ADDR_STATE_NA", ""))

        # 邮政区域/邮政编码
        if self.resWork["company_zip"]:
            ids.append((f"{self.baseID}FormView1_tbxWORK_EDUC_ADDR_POSTAL_CD", self.resWork["company_zip"]))
        else:
            ids.append((f"{self.baseID}FormView1_cbxWORK_EDUC_ADDR_POSTAL_CD_NA", ""))

        # 月收入
        if self.resWork["month_income"]:
            ids.append((f"{self.baseID}FormView1_tbxCURR_MONTHLY_SALARY", self.resWork["month_income"]))
        else:
            ids.append((f"{self.baseID}FormView1_cbxCURR_MONTHLY_SALARY_NA", ""))

        seList += [
            # 所属日期
            (f"{self.baseID}FormView1_ddlEmpDateFromDay", f"{int(day)}"),
            # 所属国家
            (f"{self.baseID}FormView1_ddlEmpSchCountry", self.resWork["company_country"]),
        ]

        self.waitIdSel(ids, seList)

        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '工作教育:')
            return 1
        except Exception:
            pass

        self.progress("55% 工作教育 完成")

        return 0

    def workEducation2(self):
        """ 以前的工作/培训 """
        print("以前的工作/培训")
        ids = []
        seList = []

        # 您之前有工作吗？
        if self.resWork["five_work_is"] == "N":
            ids.append((f"{self.baseID}FormView1_rblPreviouslyEmployed_1", ""))
        elif self.resWork["five_work_is"] == "Y":
            ids.append((f"{self.baseID}FormView1_rblPreviouslyEmployed_0", ""))
            for no, work in enumerate(json.loads(self.resWork["five_work_info"])):
                ferId = f"{self.baseID}FormView1_dtlPrevEmpl_ctl0{no}_"
                if no and self.old_page:
                    ids.append((f"{self.baseID}FormView1_dtlPrevEmpl_ctl0{no-1}_InsertButtonPrevEmpl", ""))
                try:
                    sYear, sMonth, sDay = work["induction_time"].split("-")
                    eYear, eMonth, eDay = work["departure_time"].split("-")
                except Exception:
                    self.errJson(["", "工作开始时间或结束时间未正确填写"], '以前的工作:')
                    return 1
                ids += [
                    # 公司名
                    (f"{ferId}tbEmployerName", self.cos(work["company_name"])),
                    # 公司地址1
                    (f"{ferId}tbEmployerStreetAddress1", work["company_address"][:40]),
                    # 公司地址2
                    (f"{ferId}tbEmployerStreetAddress2", work["company_address"][40:]),
                    # 城市
                    (f"{ferId}tbEmployerCity", work["company_city"]),
                    # 电话
                    (f"{ferId}tbEmployerPhone", self.cos(work["company_phone"], 0)),
                    # 职位
                    (f"{ferId}tbJobTitle", work["position"]),
                    # 工作开始时间: 月
                    (f"{ferId}ddlEmpDateFromMonth", MONTH[sMonth]),
                    # 工作结束时间: 月
                    (f"{ferId}ddlEmpDateToMonth", MONTH[eMonth]),
                    # 工作开始时间: 年
                    (f"{ferId}tbxEmpDateFromYear", sYear),
                    # 工作结束时间: 年
                    (f"{ferId}tbxEmpDateToYear", eYear),
                    # 简述工作职责
                    (f"{ferId}tbDescribeDuties", work["responsibility"]),
                ]
                seList += [
                    # 工作开始时间: 日
                    (f"{ferId}ddlEmpDateFromDay", f"{int(sDay)}"),
                    # 工作结束时间: 日
                    (f"{ferId}ddlEmpDateToDay", f"{int(eDay)}"),
                ]
                # 州省
                if work["company_province"]:
                    ids.append((f"{ferId}tbxPREV_EMPL_ADDR_STATE", work["company_province"]))
                else:
                    ids.append((f"{ferId}cbxPREV_EMPL_ADDR_STATE_NA", ""))
                # 邮编
                if work["company_zip"]:
                    ids.append((f"{ferId}tbxPREV_EMPL_ADDR_POSTAL_CD", work["company_zip"]))
                else:
                    ids.append((f"{ferId}cbxPREV_EMPL_ADDR_POSTAL_CD_NA", ""))
                # 主管姓
                if work["director_name"]:
                    ids.append((f"{ferId}tbSupervisorSurname", work["director_name"]))
                else:
                    ids.append((f"{ferId}cbxSupervisorSurname_NA", ""))
                # 主管名
                if work["director_names"]:
                    ids.append((f"{ferId}tbSupervisorGivenName", work["director_names"]))
                else:
                    ids.append((f"{ferId}cbxSupervisorGivenName_NA", ""))

                # 国家
                seList += [(f"{ferId}DropDownList2", work["company_country"])]

        # 您是否在任何相当于中学水平或以上的教育机构里学习过？
        if self.resWork["education_background"] == "N":
            ids.append((f"{self.baseID}FormView1_rblOtherEduc_1", ""))
        elif self.resWork["education_background"] == "Y":
            ids.append((f"{self.baseID}FormView1_rblOtherEduc_0", ""))

            for no, school in enumerate(json.loads(self.resWork["education_school"])):
                ferId = f"{self.baseID}FormView1_dtlPrevEduc_ctl0{no}_"
                aYear, aMonth, aDay = school["admission_date"].split("-")
                gYear, gMonth, gDay = school["graduation_date"].split("-")
                if no and self.old_page:
                    ids.append((f"{self.baseID}FormView1_dtlPrevEduc_ctl0{no - 1}_InsertButtonPrevEduc", ""))
                ids += [
                    # 学校名称
                    (f"{ferId}tbxSchoolName", self.cos(school["name"])),
                    # 地址
                    (f"{ferId}tbxSchoolAddr1", school["address"].strip()[:40]),
                    # 地址2
                    (f"{ferId}tbxSchoolAddr2", school["address"][40:]),
                    # 城市
                    (f"{ferId}tbxSchoolCity", school["city"]),
                    # 课程
                    (f"{ferId}tbxSchoolCourseOfStudy", school["course"]),
                    # 就读日期: 年
                    (f"{ferId}tbxSchoolFromYear", aYear),
                    # 就读日期: 月
                    (f"{ferId}ddlSchoolFromMonth", MONTH[aMonth]),
                    # 毕业日期: 年
                    (f"{ferId}tbxSchoolToYear", gYear),
                    # 毕业日期: 月
                    (f"{ferId}ddlSchoolToMonth", MONTH[gMonth]),
                ]
                seList += [
                    # 就读日期: 日
                    (f"{ferId}ddlSchoolFromDay", f"{int(aDay)}"),
                    # 毕业日期: 日
                    (f"{ferId}ddlSchoolToDay", f"{int(gDay)}"),
                    # 国家
                    (f"{ferId}ddlSchoolCountry", school["country"])
                ]
                # 州省
                if school["province"]:
                    ids.append((f"{ferId}tbxEDUC_INST_ADDR_STATE", school["province"]))
                else:
                    ids.append((f"{ferId}cbxEDUC_INST_ADDR_STATE_NA", ""))
                # 邮编
                if school["zip"]:
                    ids.append((f"{ferId}tbxEDUC_INST_POSTAL_CD", school["zip"]))
                else:
                    ids.append((f"{ferId}cbxEDUC_INST_POSTAL_CD_NA", ""))

        self.waitIdSel(ids, seList)
        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '以前的工作:')
            return 1
        except Exception:
            pass

        self.progress("60% 以前的工作/培训页 完成")

        return 0

    def workEducation3(self):
        """ 补充页 """
        print("补充页")
        ids = []

        # 您是否属于一个宗族或者部落？
        if self.resWork["religious_beliefs_is"] == "N":
            self.Wait(f"{self.baseID}FormView1_rblCLAN_TRIBE_IND_1")
        elif self.resWork["religious_beliefs_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblCLAN_TRIBE_IND_0")
            self.Wait(f"{self.baseID}FormView1_tbxCLAN_TRIBE_NAME", self.resWork["religious_beliefs"])

        # 请列出您所说语言的种类
        lang = self.resWork["master_language"].split(',')[0].strip()
        self.Wait(f"{self.baseID}FormView1_dtlLANGUAGES_ctl00_tbxLANGUAGE_NAME", lang)
        for i, language in enumerate(self.resWork["master_language"].split(',')[1:]):
            language = language.strip()
            self.Wait(f"{self.baseID}FormView1_dtlLANGUAGES_ctl0{i}_InsertButtonLANGUAGE")
            self.Wait(f"{self.baseID}FormView1_dtlLANGUAGES_ctl0{i+1}_tbxLANGUAGE_NAME", language)
        # 最近五年里您是否去过其他国家？
        if self.resWork["five_been_country_is"] == "N":
            self.Wait(f"{self.baseID}FormView1_rblCOUNTRIES_VISITED_IND_1")
        elif self.resWork["five_been_country_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblCOUNTRIES_VISITED_IND_0")
            five_been_country = json.loads(self.resWork["five_been_country"])
            for index, val in enumerate(five_been_country):
                if index and self.old_page:
                    self.Wait(f"{self.baseID}FormView1_dtlCountriesVisited_ctl0{index-1}_InsertButtonCountriesVisited")
                self.choiceSelect(f"{self.baseID}FormView1_dtlCountriesVisited_ctl0{index}_ddlCOUNTRIES_VISITED", val["name"])

            for index, value in enumerate(json.loads(self.resWork["five_been_country"])):
                if index and self.old_page:
                    self.Wait(f"{self.baseID}FormView1_dtlCountriesVisited_ctl0{index - 1}_InsertButtonCountriesVisited")
                self.choiceSelect(f"{self.baseID}FormView1_dtlCountriesVisited_ctl0{index}_ddlCOUNTRIES_VISITED", value["name"])

        # 您是否从属于任何一个专业的、社会或慈善组织？并为其做过贡献、或为其工作过？
        if self.resWork["charity_is"] == "N":
            self.Wait(f"{self.baseID}FormView1_rblORGANIZATION_IND_1")
        elif self.resWork["charity_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblORGANIZATION_IND_0")
            for index, value in enumerate(json.loads(self.resWork["charity_name"])):
                if index and self.old_page:
                    self.Wait(f"{self.baseID}FormView1_dtlORGANIZATIONS_ctl0{index - 1}_InsertButtonORGANIZATION")
                self.Wait(f"{self.baseID}FormView1_dtlORGANIZATIONS_ctl0{index}_tbxORGANIZATION_NAME", value["name"])

        # 您是否具有特殊技能或接受过特殊培训，例如有关枪械、炸药、 核装置、 生物或化学方面的经验？
        if self.resWork["special_training_is"] == "N":
            self.Wait(f"{self.baseID}FormView1_rblSPECIALIZED_SKILLS_IND_1")
        elif self.resWork["special_training_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblSPECIALIZED_SKILLS_IND_0")
            self.Wait(f"{self.baseID}FormView1_tbxSPECIALIZED_SKILLS_EXPL", self.resWork["special_training_info"])

        # 您是否曾经在军队服役？
        if self.resWork["army_is"] == "N":
            self.Wait(f"{self.baseID}FormView1_rblMILITARY_SERVICE_IND_1")
        elif self.resWork["army_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblMILITARY_SERVICE_IND_0")
            for index, value in enumerate(json.loads(self.resWork["army_info"])):
                sYear, sMonth, sDay = value["start_time"].split("-")
                eYear, eMonth, eDay = value["end_time"].split("-")
                if index and self.old_page:
                    self.Wait(f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index - 1}_InsertButtonMILITARY_SERVICE", "")
                ids += [
                    # 军种
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_BRANCH", value["services"]),
                    # 级别/职位
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_RANK", value["level"]),
                    # 军事特长
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_SPECIALTY", value["military"]),
                    # 服役开始年份
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_FROMYear", sYear),
                    # 服役开始月份
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_FROMMonth", MONTH[sMonth]),
                    # 服役结束年份
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_TOYear", eYear),
                    # 服役结束月份
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_TOMonth", MONTH[eMonth]),
                ]
                seList = [
                    # 服役开始日
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_FROMDay", f"{int(sDay)}"),
                    # 服役结束日
                    (f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_TODay", f"{int(eDay)}"),
                ]
                ids = self.waitIdSel(ids, seList)
                # 服役国家
                self.choiceSelect(f"{self.baseID}FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_CNTRY",  value["country"])

        # 你是否曾经服务于或参与过准军事性单位、治安团体、造反组织、游击队或暴动组织，或曾经是其成员之一？
        if self.resWork["military_unit_is"] == "N":
            self.Wait(f"{self.baseID}FormView1_rblINSURGENT_ORG_IND_1")
        elif self.resWork["military_unit_is"] == "Y":
            self.Wait(f"{self.baseID}FormView1_rblINSURGENT_ORG_IND_0")
            self.Wait(f"{self.baseID}FormView1_tbxINSURGENT_ORG_EXPL",
                      self.resWork["military_unit_info"])

        self.urlButton()
        try:
            errInfos = self.driver.find_element_by_id(f"{self.baseID}FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '补充页:')
            return 1
        except Exception:
            pass

        self.progress("65% 补充页 完成")

        return 0

    def get_sec(self, status, ids):
        sec = json.loads(self.resWork["security"])
        if sec[status] == "N":
            return [(f"{self.baseID}FormView1_rbl{ids}_1", "")]
        elif sec[status] == "Y":
            return [
                (f"{self.baseID}FormView1_rbl{ids}_0", ""),
                (f"{self.baseID}FormView1_tbx{ids}", sec[f"info{status.strip('status')}"])
            ]

    def securityAndBackground(self):
        """ 安全与背景页 """
        print("安全与背景页")

        # btn = [(f"{self.baseID}UpdateButton3", "")]

        sec1 = self.get_sec(f"status1", "Disease")
        sec2 = self.get_sec(f"status2", "Disorder")
        sec3 = self.get_sec(f"status3", "Druguser")

        ids1 = sec1 + sec2 + sec3

        sec4 = self.get_sec(f"status4", "Arrested")
        sec5 = self.get_sec(f"status5", "ControlledSubstances")
        sec6 = self.get_sec(f"status6", "Prostitution")
        sec7 = self.get_sec(f"status7", "MoneyLaundering")
        sec8 = self.get_sec(f"status8", "HumanTrafficking")
        sec9 = self.get_sec(f"status9", "AssistedSevereTrafficking")
        sec10 = self.get_sec(f"status10", "HumanTraffickingRelated")

        ids2 = sec4 + sec5 + sec6 + sec7 + sec8 + sec9 + sec10

        sec11 = self.get_sec(f"status11", "IllegalActivity")
        sec12 = self.get_sec(f"status12", "TerroristActivity")
        sec13 = self.get_sec(f"status13", "TerroristSupport")
        sec14 = self.get_sec(f"status14", "TerroristOrg")
        sec15 = self.get_sec(f"status15", "Genocide")
        sec16 = self.get_sec(f"status16", "Torture")
        sec17 = self.get_sec(f"status17", "ExViolence")
        sec18 = self.get_sec(f"status18", "ChildSoldier")
        sec19 = self.get_sec(f"status19", "ReligiousFreedom")
        sec20 = self.get_sec(f"status20", "PopulationControls")
        sec21 = self.get_sec(f"status21", "Transplant")

        ids3 = sec11 + sec12 + sec13 + sec14 + sec15 + sec16 + sec17 + sec18 + sec19 + sec20 + sec21
        sec22 = self.get_sec(f"status22", "ImmigrationFraud")
        sec26 = self.get_sec(f"status26", "RemovalHearing")
        sec27 = self.get_sec(f"status27", "FailToAttend")
        sec28 = self.get_sec(f"status28", "VisaViolation")

        ids4 = sec22 + sec26 + sec27 + sec28

        sec23 = self.get_sec(f"status23", "ChildCustody")
        sec24 = self.get_sec(f"status24", "VotingViolation")
        sec25 = self.get_sec(f"status25", "RenounceExp")
        sec29 = self.get_sec(f"status29", "AttWoReimb")

        ids5 = sec23 + sec24 + sec25 + sec29
        # ids1 = [
        #     (f"{self.baseID}FormView1_rblDisease_1", ""),
        #     # (f"{self.baseID}FormView1_rblDisease_0", ""),
        #     # (f"{self.baseID}FormView1_tbxDisease", "")            
        #     (f"{self.baseID}FormView1_rblDisorder_1", ""),
        #     # (f"{self.baseID}FormView1_rblDisorder_0", ""),
        #     # (f"{self.baseID}FormView1_tbxDisorder", "")            
        #     (f"{self.baseID}FormView1_rblDruguser_1", ""),
        #     # (f"{self.baseID}FormView1_rblDruguser_0", ""),
        #     # (f"{self.baseID}FormView1_tbxDruguser", "")            
        #     (f"{self.baseID}UpdateButton3", ""),
        # ]

        # ids2 = [
        #     (f"{self.baseID}FormView1_rblArrested_1", ""),
        #     # (f"{self.baseID}FormView1_rblArrested_0", ""),
        #     # (f"{self.baseID}FormView1_tbxArrested", "")            
        #     (f"{self.baseID}FormView1_rblControlledSubstances_1", ""),
        #     # (f"{self.baseID}FormView1_rblControlledSubstances_0", ""),
        #     # (f"{self.baseID}FormView1_tbxControlledSubstances", "")            
        #     (f"{self.baseID}FormView1_rblProstitution_1", ""),
        #     # (f"{self.baseID}FormView1_rblProstitution_0", ""),
        #     # (f"{self.baseID}FormView1_tbxProstitution", "")            
        #     (f"{self.baseID}FormView1_rblMoneyLaundering_1", ""),
        #     # (f"{self.baseID}FormView1_rblMoneyLaundering_0", ""),
        #     # (f"{self.baseID}FormView1_tbxMoneyLaundering", "")            
        #     (f"{self.baseID}FormView1_rblHumanTrafficking_1", ""),
        #     # (f"{self.baseID}FormView1_rblHumanTrafficking_0", ""),
        #     # (f"{self.baseID}FormView1_tbxHumanTrafficking", "")            
        #     (f"{self.baseID}FormView1_rblAssistedSevereTrafficking_1", ""),
        #     # (f"{self.baseID}FormView1_rblAssistedSevereTrafficking_0", ""),
        #     # (f"{self.baseID}FormView1_tbxAssistedSevereTrafficking", "")            
        #     (f"{self.baseID}FormView1_rblHumanTraffickingRelated_1", ""),
        #     # (f"{self.baseID}FormView1_rblHumanTraffickingRelated_0", ""),
        #     # (f"{self.baseID}FormView1_tbxHumanTraffickingRelated", "")            
        #     (f"{self.baseID}UpdateButton3", ""),
        # ]

        # ids3 = [
        #     (f"{self.baseID}FormView1_rblIllegalActivity_1", ""),
        #     # (f"{self.baseID}FormView1_rblIllegalActivity_0", ""),
        #     # (f"{self.baseID}FormView1_tbxIllegalActivity", "")            
        #     (f"{self.baseID}FormView1_rblTerroristActivity_1", ""),
        #     # (f"{self.baseID}FormView1_rblTerroristActivity_0", ""),
        #     # (f"{self.baseID}FormView1_tbxTerroristActivity", "")            
        #     (f"{self.baseID}FormView1_rblTerroristSupport_1", ""),
        #     # (f"{self.baseID}FormView1_rblTerroristSupport_0", ""),
        #     # (f"{self.baseID}FormView1_tbxTerroristSupport", "")            
        #     (f"{self.baseID}FormView1_rblTerroristOrg_1", ""),
        #     # (f"{self.baseID}FormView1_rblTerroristOrg_0", ""),
        #     # (f"{self.baseID}FormView1_tbxTerroristOrg", "")            
        #     (f"{self.baseID}FormView1_rblGenocide_1", ""),
        #     # (f"{self.baseID}FormView1_rblGenocide_0", ""),
        #     # (f"{self.baseID}FormView1_tbxGenocide", "")            
        #     (f"{self.baseID}FormView1_rblTorture_1", ""),
        #     # (f"{self.baseID}FormView1_rblTorture_0", ""),
        #     # (f"{self.baseID}FormView1_tbxTorture", "")            
        #     (f"{self.baseID}FormView1_rblExViolence_1", ""),
        #     # (f"{self.baseID}FormView1_rblExViolence_0", ""),
        #     # (f"{self.baseID}FormView1_tbxExViolence", "")            
        #     (f"{self.baseID}FormView1_rblChildSoldier_1", ""),
        #     # (f"{self.baseID}FormView1_rblChildSoldier_0", ""),
        #     # (f"{self.baseID}FormView1_tbxChildSoldier", "")            
        #     (f"{self.baseID}FormView1_rblReligiousFreedom_1", ""),
        #     # (f"{self.baseID}FormView1_rblReligiousFreedom_0", ""),
        #     # (f"{self.baseID}FormView1_tbxReligiousFreedom", "")            
        #     (f"{self.baseID}FormView1_rblPopulationControls_1", ""),
        #     # (f"{self.baseID}FormView1_rblPopulationControls_0", ""),
        #     # (f"{self.baseID}FormView1_tbxPopulationControls", "")            
        #     (f"{self.baseID}FormView1_rblTransplant_1", ""),
        #     # (f"{self.baseID}FormView1_rblTransplant_0", ""),
        #     # (f"{self.baseID}FormView1_tbxTransplant", "")            
        #     (f"{self.baseID}UpdateButton3", ""),
        # ]

        # ids4 = [
        #     (f"{self.baseID}FormView1_rblImmigrationFraud_1", ""),
        #     # (f"{self.baseID}FormView1_rblImmigrationFraud_0", ""),
        #     # (f"{self.baseID}FormView1_tbxImmigrationFraud", "")            
        #     (f"{self.baseID}UpdateButton3", ""),
        # ]

        # ids5 = [
        #     (f"{self.baseID}FormView1_rblChildCustody_1", ""),
        #     # (f"{self.baseID}FormView1_rblChildCustody_0", ""),
        #     # (f"{self.baseID}FormView1_tbxChildCustody", "")            
        #     (f"{self.baseID}FormView1_rblVotingViolation_1", ""),
        #     # (f"{self.baseID}FormView1_rblVotingViolation_0", ""),
        #     # (f"{self.baseID}FormView1_tbxVotingViolation", "")            
        #     (f"{self.baseID}FormView1_rblRenounceExp_1", ""),
        #     # (f"{self.baseID}FormView1_rblRenounceExp_0", ""),
        #     # (f"{self.baseID}FormView1_tbxRenounceExp", "")            
        #     (f"{self.baseID}UpdateButton3", ""),
        # ]

        idsDic = {
            "SecurityandBackground1": ids1,
            "SecurityandBackground2": ids2,
            "SecurityandBackground3": ids3,
            "SecurityandBackground4": ids4,
            "SecurityandBackground5": ids5,
        }
        node = self.getNode
        for i in range(int(node[-1]), 6):
            try:
                self.waitIdSel(idsDic[node[:-1] + str(i)])
            except Exception:
                pass
            self.urlButton()

        self.progress("70% 安全与背景页 完成")

        return 0

    def uploadPhoto(self):
        """ 上传照片页 """
        print("上传照片页")
        print(self.resInfo["photo"])
        with open(BASEDIR + "\\photo.jpeg", 'wb') as f:
            f.write(requests.get(self.resInfo["photo"]).content)

        ids = [
            (f"{self.baseID}btnUploadPhoto", ""),
            ("ctl00_cphMain_imageFileUpload", BASEDIR + "\\photo.jpeg"),
            ("ctl00_cphButtons_btnUpload", ""),
        ]
        ids = self.waitIdSel(ids)
        if "ctl00_cphError_errorUpload" in self.driver.page_source:
            info1 = self.driver.find_element("id", "ctl00_cphError_errorUpload").text
            photo_errors = ["Unable to read image memory into DibImage.", "Image exceeds maximum file size of 240 KB"]
            if info1 in photo_errors:
                print("照片上传失败")
                self.errJson([''], '照片上传失败:')
                return 1

        info2 = self.driver.find_element("id", "ctl00_cphMain_qualityCheckOutcome").text

        if info2 == "Photo passed quality standards":
            print("照片上传成功")
        else:
            print("照片上传失败")
            self.errJson([''], '照片上传失败:')
            return 1

        ids = [
            ("ctl00_cphButtons_btnContinue", ""),
            (f"{self.baseID}UpdateButton3", "")
        ]
        self.waitIdSel(ids)

        self.progress("80% 上传照片页 完成")
        if self.resPublic["inspect"]:
            self.usPipe.upload(self.resPublic["aid"], status=4, visa_status=3)
            return 1
        return 0

    # def review(self):
        # """ 审查页面 """
        # print("审查页面")
        # self.urlButton()
        # return 0

    def signCertify(self):
        """ 最后确认页面 """
        self.progress("90% 审查页面 完成")
        print("最后确认页面")
        self.driver.execute_script("document.documentElement.scrollTop=910")
        self.Wait(f"{self.baseID}FormView3_rblPREP_IND_1")
        self.Wait(f"{self.baseID}PPTNumTbx",
                  self.resInfo["passport_number"])
        for _ in range(5):
            try:
                self.driver.execute_script("document.documentElement.scrollTop=910")
                # result = self.getCaptcha(f"c_general_esign_signtheapplication_ctl00_sitecontentplaceholder_defaultcaptcha_CaptchaImage")
                # self.Wait(f"{self.baseID}CodeTextBox", result)
                rsp = self.getCaptcha(f"c_general_esign_signtheapplication_ctl00_sitecontentplaceholder_defaultcaptcha_CaptchaImage")
                self.Wait(f"{self.baseID}CodeTextBox", rsp.pred_rsp.value)
                self.Wait(f"{self.baseID}btnSignApp")
                sleep(2)
                if "You have successfully" in self.driver.page_source and "sign your application:" not in self.driver.page_source: break
                else:
                    Captcha(4, rsp=rsp)
            except Exception: pass

        self.urlButton()
        self.progress("95% 最后确认页面 完成")
        return 0

    def done(self):
        """ 完成页面 """
        print("完成页面")
        self.printPdf()
        sleep(1)
        self.Wait(f"{self.baseID}FormView1_btnPrintApp")
        self.Wait(f"{self.baseID}ucModalNavigate_ctl01_btnWarning")
        sleep(1)
        self.printPdf()
        sleep(1)
        self.usPipe.upload(self.resPublic["aid"], visa_status='2')
        self.renamePdf()
        print("page over...")
        self.progress("100% 成功")
