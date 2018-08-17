#!/usr/bin/env python
# coding: utf-8
"""
@Author: ZhaoBin 
@Date: 2018-08-05 13:30:41 
@Last Modified by:   ZhaoBin 
@Last Modified time: 2018-08-08 17:00:41
"""
import json
import sys

import requests
from PIL import Image

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from settings import BASEDIR, MONTH, UsError, sleep
from yunsu import upload

NC = 'noClick'


class AutoUs(object):
    """ 自动化录入程序基类

        Parameter:
            resInfo:    数据库 dc_business_america_info_eng 信息
            resPublic:  数据库 dc_business_america_public_eng 信息
            resWork:    数据库 dc_business_america_work_eng 信息
    """

    def __init__(self, resPublic=None, resInfo=None, resWork=None, usPipe=None):
        try:
            assert resInfo and resPublic and resWork
        except AssertionError:
            raise UsError('数据库信息未传递')
        self.resPublic = resPublic
        self.resInfo = resInfo
        self.resWork = resWork
        self.usPipe = usPipe
        self.aid = self.resPublic['aid']
        self.allUrl = []

        self.path = sys.path[0] + '\\'
        self.usUrl = 'https://ceac.state.gov/GenNIV/Default.aspx'

        # 设置 chrome_options 属性
        self.chrome_options = webdriver.ChromeOptions()
        # 不加载图片
        # self.chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # 无界面
        # self.chrome_options.add_argument('--headless')
        # 设置代理
        # self.chrome_options.add_argument('--proxy-server=http://127.0.0.1:1080')
        # 设置浏览器窗口大小
        self.chrome_options.add_argument('window-size=800x3000')

        self.driver = webdriver.Chrome(executable_path=self.path + 'chromedriver', chrome_options=self.chrome_options)
        # 设置隐性等待时间, timeout = 20
        self.driver.implicitly_wait(10)
        # 设置显性等待时间, timeout = 10, 间隔 0.3s 检查一次
        self.wait = WebDriverWait(self.driver, 10, 0.3, "请求超时")

    # 入口函数 -- 程序执行开始
    @property
    def run(self):
        """ 根据 node 来选择具体函数 """
        # nodeList = [
        #     "Personal1", "Personal2", "AddressPhone", "PptVisa", "Travel",
        #     "TravelCompanions", "PreviousUSTravel", "USContact",  "Relatives", "Spouse",
        #     "WorkEducation1", "WorkEducation2", "WorkEducation3",  "SecurityandBackground1",
        #     "SecurityandBackground2", "SecurityandBackground3", "SecurityandBackground4",
        #     "SecurityandBackground5", "UploadPhoto", "ConfirmPhoto", "ReviewPersonal", 
        #     "ReviewTravel", "ReviewUSContact", "ReviewFamily", "ReviewWorkEducation", 
        #     "ReviewSecurity", "ReviewLocation", "SignCertify", "DeceasedSpouse", "PrevSpouse"
        # ]

        nodeDict = {
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
            "ConfirmPhoto": self.review,
            "ReviewPersonal": self.review,
            "ReviewTravel": self.review,
            "ReviewUSContact": self.review,
            "ReviewFamily": self.review,
            "ReviewWorkEducation": self.review,
            "ReviewSecurity": self.review,
            "ReviewLocation": self.review,
            "SignCertify": self.signCertify,
        }
        while self.getNode != 'Done':
            if nodeDict[self.getNode]():
                break
        return 0

    # 回到个人信息页1
    @property
    def comeBack(self):
        self.driver.get("https://ceac.state.gov/GenNIV/General/complete/complete_personal.aspx?node=Personal1")

    # 获取网页标示「网址最后一个单词」
    @property
    def getNode(self):
        return self.driver.current_url.split("node=")[1]

    # 开始一个新的签证
    @property
    def default(self):
        """ 开始一个新的签证 """
        # 请求首页
        self.driver.get(self.usUrl)
        # 选择中文简体
        # self.choiceSelect("ctl00_ddlLanguage", "zh-CN")
        # 选择领区
        self.choiceSelect(
            "ctl00_SiteContentPlaceHolder_ucLocation_ddlLocation", self.resInfo['activity'])
        # self.choiceSelect("ctl00_SiteContentPlaceHolder_ucLocation_ddlLocation", 'BEJ')
        #　识别验证码
        while self.driver.current_url == self.usUrl:
            result = self.getCaptcha(
                'c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage')
            self.Wait(
                'ctl00_SiteContentPlaceHolder_ucLocation_IdentifyCaptcha1_txtCodeTextBox', result)
            self.Wait('ctl00_SiteContentPlaceHolder_lnkNew')
            sleep(1)

        self.Wait("ctl00_SiteContentPlaceHolder_txtAnswer", "qwer")
        self.Wait("ctl00_SiteContentPlaceHolder_btnContinue")
        return "Personal1"

    # 继续一个旧的签证
    def continueGo(self, noback=1):
        """ 继续一个旧的签证信息 """
        self.driver.get(self.usUrl)
        # 选择中文简体
        # self.choiceSelect("ctl00_ddlLanguage", "zh-CN")
        # 选择领区
        self.choiceSelect("ctl00_SiteContentPlaceHolder_ucLocation_ddlLocation", self.resInfo['activity'])
        
        while self.driver.current_url == self.usUrl:
            result = self.getCaptcha(
                'c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage')
            self.Wait(
                'ctl00_SiteContentPlaceHolder_ucLocation_IdentifyCaptcha1_txtCodeTextBox', result)
            self.Wait('ctl00_SiteContentPlaceHolder_lnkRetrieve')
            sleep(1)

        self.Wait("ctl00_SiteContentPlaceHolder_ApplicationRecovery1_tbxApplicationID", self.resPublic['aacode'])

        ids = [
            ("ctl00_SiteContentPlaceHolder_ApplicationRecovery1_btnBarcodeSubmit", ""),
            ("ctl00_SiteContentPlaceHolder_ApplicationRecovery1_txbSurname",
             self.resInfo['english_name'][:5]),
            ('ctl00_SiteContentPlaceHolder_ApplicationRecovery1_txbDOBYear',
             self.resInfo['date_of_birth'].split('-')[0]),
            # ("ctl00_SiteContentPlaceHolder_ApplicationRecovery1_txbSurname", "xia"),
            # ('ctl00_SiteContentPlaceHolder_ApplicationRecovery1_txbDOBYear', "1974"),
            ('ctl00_SiteContentPlaceHolder_ApplicationRecovery1_txbAnswer', 'qwer'),
            ('ctl00_SiteContentPlaceHolder_ApplicationRecovery1_btnRetrieve', ""),
        ]
        for i in ids:
            self.Wait(i[0], i[1])
        while 1:
            try:
                node = self.getNode
                break
            except:
                pass
        if noback:
            self.Wait("ctl00_SiteContentPlaceHolder_UpdateButton3")
        else:
            self.comeBack
        # while True:
        #     try:
        #         errInfos = self.getNode
        #         if "WorkEducation2" != errInfos:
        #             break
        #         else:
        #             for index, value in enumerate(json.loads(self.resWork["five_work_info"])):
        #                 if not value["director_name"]:
        #                     self.Wait(f"ctl00_SiteContentPlaceHolder_FormView1_dtlPrevEmpl_ctl0{index}_cbxSupervisorSurname_NA")
        #                     self.Wait(f"ctl00_SiteContentPlaceHolder_FormView1_dtlPrevEmpl_ctl0{index}_cbxSupervisorGivenName_NA")
        #                 else:
        #                     break
        #             self.Wait("ctl00_SiteContentPlaceHolder_UpdateButton3")
        #     except:
        #         pass
        
        while 1:
            if self.getNode != node:
                return 0

    # 错误信息字典
    @property
    def errDict(self):
        """ 错误信息提示
            Returns:
                err (dict) 美签官网大部分错误信息的提示
        """
        err = {
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
            "Country/Region of Origin (Nationality) has not been completed.": "国家/地区（国籍）尚未选",
            "The question \"Do you hold or have you held any nationality other than...?\" has not been answered.": "其它国籍未选",
            "The question \"Are you a permanent resident of a country/region other...?\" has not been answered.": "是否永久居民未选",
            "National Identification Number has not been completed.": "身份证未填",
            "U.S. Social Security Number has not been completed.": "安全号码未填",
            "U.S. Taxpayer ID Number has not been completed.": "美国身份号码未填",
            "Country/Region of Origin (Nationality) has not been completed.": "所属国家/地区（国籍）未选",
            "The question \"Do you hold or have you held any nationality other than...?\" has not been answered.": "其它国籍未选",
            "The question \"Are you a permanent resident of a country/region other...?\" has not been answered.": "是否其它国家永久居民未选",
            "National Identification Number has not been completed.": "身份证件号码未填",
            "U.S. Social Security Number accepts only numbers (0-9) and must be exactly nine (9) digits.": "美国安全号只能为9位数字",
            "U.S. Taxpayer ID Number accepts only numbers (0-9).": "美国身份证号只能为数字",
            "Street Address (Line 1) has not been completed.": "街道地址未填",
            "City has not been completed.": "城市未填",
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
            "The question \"Have you made specific travel plans?\" has not been answered.": "访美目的未选",
            "Specify has not been completed.": "访美目的(详细)未选",
            "The question \"Have you made specific travel plans?\" has not been answered.": "旅行计划未选",
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
            "Postal Zone/ZIP Code has not been completed.": "单位邮编未填",
            "Job Title has not been completed.": "职务名称未填",
            "Employment Date From is invalid. Year is required.": "入职时间未填",
            "Employment Date To is invalid. Year is required.": "离职时间未填",
            "Briefly describe your duties: has not been completed.": "工作职责未填",
            "Name of Institution has not been completed.": "机构名称未填",
            "Postal Zone/ZIP Code has not been completed.": "邮编未填",
            "Course of Study has not been completed.": "课程未填",
            "Date of Attendance From is invalid. Month and Year are required.": "入学时间未填",
            "Date of Attendance To is invalid. Month and Year are required.": "毕业时间未填",
            "Employer Name is invalid. Only the following characters are valid for this field: A-Z, 0-9, hypen (-), apostrophe ('), ampersand (&) and single spaces in between names.": "公司名称只能为: A-Z, 0-9, -, ', & 和 空格",
            "The question \"Do you have any specialized skills or training, such as...?\" has not been answered.": "是否具有特殊技能/培训",
            "Organization Name is invalid. Only the following characters are valid for this field: A-Z, 0-9, hypen (-), apostrophe ('), ampersand (&) and single spaces in between names.": "组织名无效(与公司名要求一致)",
            "The submitted photo did not meet the image quality requirements.": "照片不合格",
            "Unable to read image memory into DibImage.": "无法读取图像",
        }
        return err

    # 将错误信息存入数据库「json 数据」
    def errJson(self, errlist=None, errInfo=None):
        """ 将错误信息封装成 json 数据进行返回 """
        ls = []
        ls.append(errInfo)
        for i in errlist[1:]:
            ls.append(self.errDict.get(i, i))
        err = json.dumps(ls).replace('\\', '\\\\')
        self.usPipe.upload(self.aid, '6', err)

    # 获取验证码
    def getCaptcha(self, id=''):
        """ 验证码识别
            根据页面验证码元素位置, 截取验证码图片
            发送验证码识别请求,返回验证码文字

            Returns: result (str)
        """
        captcha = self.driver.find_element_by_id(id)
        self.driver.save_screenshot('captcha.png')
        captcha_left = captcha.location['x']
        top = 0 if captcha.location['y'] < 1200 or '--headless' in self.chrome_options.to_capabilities()[
            'goog:chromeOptions']['args'] else 910
        captcha_top = captcha.location['y'] - top
        captcha_right = captcha.location['x'] + captcha.size['width']
        captcha_bottom = captcha.location['y'] + captcha.size['height'] - top
        # print(captcha_left, captcha_top, captcha_right, captcha_bottom)
        img = Image.open('captcha.png')
        img = img.crop((captcha_left, captcha_top, captcha_right, captcha_bottom))
        img.save('code.png')
        sleep(0.5)
        result = upload()
        return result

    # 检测元素 / 点击 / 发送字符 / 选择下拉框
    def Wait(self, idName=None, text=None, xpath=None, className=None):
        """ 设置显性等待, 每 0.3s 检查一次
            Parameter:
                idName, xpath, className: 选择器规则, 默认idName
                text: 需要发送的信息 (非 NC --> 'noClick')
        """
        try:
            assert idName or xpath or className
        except AssertionError:
            raise UsError('未传选择器')
        if idName:
            locator = ("id", idName)
        elif xpath:
            locator = ("xpath", xpath)
        elif className:
            locator = ("class name", className)

        try:
            self.wait.until(EC.presence_of_element_located(locator))
            if not text:
                self.driver.find_element(*locator).click()
            elif text != NC:
                self.driver.find_element(*locator).clear()
                sleep(0.1)
                self.driver.find_element(*locator).send_keys(text)
        except Exception as e:
            raise UsError(f"{e}\n{locator[0]}: {locator[1]}\n" + f"value : {text}\n\n" if text and text != NC else "\n")
        return 0

    def choiceSelect(self, selectid=None, value=None, t=0.2):
        """ 下拉框选择器
            根据 value 选择下拉框
        """
        try:
            assert selectid and value
        except AssertionError:
            raise UsError(
                f'下拉框选择器 ID 和 value 不能为空\nselectid: {selectid}\nvalue   : {value}')
        sleep(t)
        self.Wait(selectid, text=NC)
        try:
            element = Select(self.driver.find_element_by_id(selectid))
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

    # ================== #
    #    各个页面函数    #
    # ================== #
    def personal1(self):
        """ 填写个人信息页一 (Personal1) """
        # 拼音姓 拼音名 中文姓名
        ids = [
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_SURNAME",
             self.resInfo['english_name']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_GIVEN_NAME",
             self.resInfo['english_name_s']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_FULL_NAME_NATIVE",
             self.resInfo['username'])
        ]

        # 判断是否有曾用名
        if self.resInfo['former_name_is'] == "N":
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_rblOtherNames_1", ""))
        elif self.resInfo['former_name_is'] == "Y":
            """ ["QIQI"] """
            surNames = json.loads(self.resInfo['former_name'])
            names = json.loads(self.resInfo['former_names'])
            for index in range(len(names)):
                if index:
                    ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_DListAlias_ctl0{index}_InsertButtonAlias", ""))
                ids += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblOtherNames_0", ""),
                    (f"ctl00_SiteContentPlaceHolder_FormView1_DListAlias_ctl0{index}_tbxSURNAME",
                    surNames[index]),
                    (f"ctl00_SiteContentPlaceHolder_FormView1_DListAlias_ctl0{index}_tbxGIVEN_NAME",
                    names[index])
                ]

        # 判断是否有中文姓名电码
        if self.resInfo['code_name_is'] == "N":
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_rblTelecodeQuestion_1", ""))
        elif self.resInfo['code_name_is'] == "Y":
            lsCodeName = [
                ("ctl00_SiteContentPlaceHolder_FormView1_rblTelecodeQuestion_0", ""),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_TelecodeSURNAME",
                 self.resInfo['code_name']),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_TelecodeGIVEN_NAME",
                 self.resInfo['code_names'])
            ]
            ids.append(lsCodeName)

        year, mon, day = self.resInfo['date_of_birth'].split('-')
        # 判断性别-生日 日-月-年
        ids += [
            (f"ctl00_SiteContentPlaceHolder_FormView1_rblAPP_GENDER_{0 if self.resInfo['sex'] == 'M' else 1}", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxDOBYear", year),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_POB_CITY",
             self.resInfo['date_of_address']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_POB_ST_PROVINCE",
             self.resInfo['date_of_province'])
        ]

        # 婚姻状况-日-月-国家
        seList = [
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlAPP_MARITAL_STATUS",
             self.resInfo['marriage']),
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlDOBDay", day),
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlDOBMonth", MONTH[mon]),
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlAPP_POB_CNTRY",
             self.resInfo['date_of_country'])
        ]
        self.waitIdSel(idlist=ids, selist=seList)
        self.urlButton(__name__)

        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '个人信息一:')
            return 1
        except:
            pass

        return 0

    def personal2(self):
        """ 填写个人信息页二 (Personal2) """
        self.choiceSelect(
            "ctl00_SiteContentPlaceHolder_FormView1_ddlAPP_NATL", self.resInfo['nationality'])

        self.AACode = self.driver.find_element_by_id('ctl00_lblAppID').text
        with open("veri.json", "a") as f:
            f.write(',\n')
            veri = [self.resPublic["id"], self.AACode, self.resInfo["english_name"][:5], self.resInfo['date_of_birth'].split('-')[0], 'qwer']
            json.dump(veri, f)
        self.usPipe.upload(self.aid, aacode=self.AACode)

        ids = []

        # 判断是否拥有其它国籍
        if self.resInfo['nationality_other_is'] == 'N':
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_rblAPP_OTH_NATL_IND_1", ""))
        elif self.resInfo['nationality_other_is'] == 'Y':
            raise UsError("有其他国籍")

        # 判断是否持有其它国家的永久居住权身份
        if self.resInfo['nationality_live_is'] == 'N':
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_rblPermResOtherCntryInd_1", ""))
        elif self.resInfo['nationality_live_is'] == 'Y':
            raise UsError("持有其它国家的永久居住权身份")

        # 身份证号
        if self.resPublic['pay_personal_address']:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_NATIONAL_ID",
                        self.resPublic['pay_personal_address']))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbexAPP_NATIONAL_ID_NA", ""))

        # 美国安全号
        if self.resInfo['social_security_number']:
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_SSN1",
                 self.resInfo['social_security_number'][:3]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_SSN2",
                 self.resInfo['social_security_number'][3:5]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_SSN3",
                 self.resInfo['social_security_number'][5:9]),
            ]
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbexAPP_SSN_NA", ""))

        # 美国纳税人身份号
        if self.resInfo['taxpayer_number']:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_TAX_ID",
                        self.resInfo['taxpayer_number']))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbexAPP_TAX_ID_NA", ""))

        self.waitIdSel(idlist=ids)

        self.urlButton(__name__)

        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '个人信息二:')
            return 1
        except:
            pass

        return 0

    def addPhone(self):
        """ 地址和电话页 """
        # 街道/城市
        ids = [
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_ADDR_LN1",
             self.resInfo['live_address']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_ADDR_LN2",
             self.resInfo['famliy_address']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_ADDR_CITY",
             self.resInfo['m_city']),
        ]
        # 省份
        if self.resInfo['province']:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_ADDR_STATE", self.resInfo['province']))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbexAPP_ADDR_STATE_NA", ""))
        # 邮编
        if self.resInfo['zip_code']:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_ADDR_POSTAL_CD", self.resInfo['zip_code']))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbexAPP_ADDR_POSTAL_CD_NA", ""))

        # 国家
        self.choiceSelect(
            "ctl00_SiteContentPlaceHolder_FormView1_ddlCountry", self.resInfo['date_of_country'])

        # 邮寄地址
        if self.resInfo['mailing_address_is'] == 'Y':
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_rblMailingAddrSame_0", ""))
        elif self.resInfo['mailing_address_is'] == 'N':
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_rblMailingAddrSame_1", ""),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxMAILING_ADDR_LN1",
                 self.resInfo['mailing_address']),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxMAILING_ADDR_LN2",
                 self.resInfo['mailing_address_two']),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxMAILING_ADDR_CITY",
                 self.resInfo['mailing_address_city']),
            ]
            # 省份
            if self.resInfo['mailing_address_province']:
                ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxMAILING_ADDR_STATE",
                            self.resInfo['mailing_address_province']))
            else:
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_cbexMAILING_ADDR_STATE_NA", ""))
            # 邮编
            if self.resInfo['mailing_address_zip']:
                ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxMAILING_ADDR_POSTAL_CD",
                            self.resInfo['mailing_address_zip']))
            else:
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_cbexMAILING_ADDR_POSTAL_CD_NA", ""))

            self.choiceSelect("ctl00_SiteContentPlaceHolder_FormView1_ddlMailCountry",
                              self.resInfo['mailing_address_nationality'])

        # 主要电话
        ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_HOME_TEL",
                    self.resInfo['home_telphone']))
        # 次要电话
        if self.resInfo['tel']:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_MOBILE_TEL", self.resInfo['tel']))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbexAPP_MOBILE_TEL_NA", ""))
        # 工作电话
        if self.resInfo['company_phone']:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_BUS_TEL",
                        self.resInfo['company_phone']))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbexAPP_BUS_TEL_NA", ""))

        ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxAPP_EMAIL_ADDR",
                    self.resInfo['home_email']))

        self.waitIdSel(idlist=ids)

        self.urlButton(__name__)

        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '地址和电话:')
            return 1
        except:
            pass

        return 0

    def pptVisa(self):
        """ 护照页 """
        #　护照类型/护照号
        ids = [
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxPPT_NUM",
             self.resInfo['passport_number']),
        ]
        # 护照本编号
        if self.resInfo['passport_papers_number']:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxPPT_BOOK_NUM", self.resInfo['passport_papers_number']))
        else:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_cbexPPT_BOOK_NUM_NA", ""))

        # 护照签发城市
        ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxPPT_ISSUED_IN_CITY",
                    self.resInfo['place_of_issue']))
        # 护照签发省
        ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxPPT_ISSUED_IN_STATE",
                    self.resInfo['place_issue_province']))
        # 护照 签发日期/失效日期
        iYear, iMon, iDay = self.resInfo['lssue_date'].split('-')
        eYear, eMon, eDay = self.resInfo['expiration_date'].split('-')
        seList = [
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlPPT_TYPE",
             self.resInfo['passport_category']),
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlPPT_ISSUED_DTEDay", iDay),
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlPPT_ISSUED_DTEMonth", iMon),
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlPPT_EXPIRE_DTEDay", eDay),
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlPPT_EXPIRE_DTEMonth", eMon)
        ]
        ids += [
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxPPT_ISSUEDYear", iYear),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxPPT_EXPIREYear", eYear),
        ]

        # 护照是否遗失或被盗过
        if self.resInfo['passport_loss'] == 'N':
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_rblLOST_PPT_IND_1", ""))
        elif self.resInfo['passport_loss'] == 'Y':
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_rblLOST_PPT_IND_0", ""))
            for index, value in enumerate(json.loads(self.resInfo["passport_loss_yes"])):
                if index:
                    ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlLostPPT_ctl0{index - 1}_InsertButtonLostPPT", ""))
                # 是否记得护照号
                if value["number"]:
                    ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlLostPPT_ctl0{index}_tbxLOST_PPT_NUM", value["number"]))
                else: # 忘记了/未知的
                    ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlLostPPT_ctl0{index}_cbxLOST_PPT_NUM_UNKN_IND", ""))
                ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlLostPPT_ctl0{index}_tbxLOST_PPT_EXPL", value["infos"]))
                seList += [("ctl00_SiteContentPlaceHolder_FormView1_dtlLostPPT_ctl00_ddlLOST_PPT_NATL", value["office"])]
                ids = self.waitIdSel(ids)
                
        self.waitIdSel(selist=seList)
        self.waitIdSel(ids)
        # self.choiceSelect(sel[0], sel[1])
        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '护照:')
            return 1
        except:
            pass

        return 0

    def travel(self):
        """ 旅行页 """
        ids = []
        seList = []
        purpose = json.loads(self.resPublic['america_purpose'])
        for index, value in enumerate(purpose):
            if index:
                seList.append((f"ctl00_SiteContentPlaceHolder_FormView1_dlPrincipalAppTravel_ctl0{index - 1}_InsertButtonAlias", ""))
            seList += [
                (f"ctl00_SiteContentPlaceHolder_FormView1_dlPrincipalAppTravel_ctl0{index}_ddlPurposeOfTrip", value["one"]),
                (f"ctl00_SiteContentPlaceHolder_FormView1_dlPrincipalAppTravel_ctl0{index}_ddlOtherPurpose", value["two"]),
            ]

        seList.append(("ctl00_SiteContentPlaceHolder_FormView1_ddlWhoIsPaying", self.resPublic['travel_cost_pay']))
        seList = self.waitIdSel(selist=seList)
        if self.resPublic['travel_plans_is'] == "N":
            year, mon, day = self.resPublic['arrive_time'].split('-')
            ids = [
                ("ctl00_SiteContentPlaceHolder_FormView1_rblSpecificTravel_1", ""),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxTRAVEL_DTEYear", year),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxTRAVEL_LOS",
                 self.resPublic['stay_time']),
            ]
            ids = self.waitIdSel(ids)

            seList = [
                ("ctl00_SiteContentPlaceHolder_FormView1_ddlTRAVEL_DTEDay",
                 f"{int(day)}"),
                ("ctl00_SiteContentPlaceHolder_FormView1_ddlTRAVEL_DTEMonth",
                 f"{int(mon)}"),
                ("ctl00_SiteContentPlaceHolder_FormView1_ddlTRAVEL_LOS_CD",
                 self.resPublic['stay_times']),
            ]
            seList = self.waitIdSel(selist=seList)
        elif self.resPublic['travel_plans_is'] == "Y":
            # 到达美国日期/航班/到达城市/离美日期/航班/离美城市/请提供您在美期间计划访问的地点名称
            plans = json.loads(self.resPublic['plans_info'])
            """ {
                "arrive_time":"2018-08-30",
                "arrive_fly":"JSP",
                "arrive_city":"Los Angeles",
                "leave_time":"2018-09-04",
                "leave_fly":"PSJ",
                "leave_city":"Los Angeles"} """
            aYear, aMon, aDay = plans["arrive_time"].split('-')
            dYear, dMon, dDay = plans["leave_time"].split('-')
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_rblSpecificTravel_0", ""),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxARRIVAL_US_DTEYear", aYear),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxArriveFlight", plans["arrive_fly"]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxArriveCity", plans["arrive_city"]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxDEPARTURE_US_DTEYear", dYear),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxDepartFlight", plans["leave_fly"]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxDepartCity", plans["leave_city"]),
            ]
            seList += [
                ("ctl00_SiteContentPlaceHolder_FormView1_ddlARRIVAL_US_DTEDay", aDay),
                ("ctl00_SiteContentPlaceHolder_FormView1_ddlARRIVAL_US_DTEMonth", f"{int(aMon)}"),
                ("ctl00_SiteContentPlaceHolder_FormView1_ddlDEPARTURE_US_DTEDay", dDay),
                ("ctl00_SiteContentPlaceHolder_FormView1_ddlDEPARTURE_US_DTEMonth", f"{int(dMon)}"),
            ]
            for index, value in enumerate(json.loads(self.resPublic["plans_access"])):
                if index:
                    ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlTravelLoc_ctl0{index - 1}_InsertButtonTravelLoc", ""))
                ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlTravelLoc_ctl0{index}_tbxSPECTRAVEL_LOCATION", value["city"]))

        # 在美停留期间的住址
        ids += [
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxStreetAddress1",
             self.resPublic['stay_address']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxStreetAddress2",
             self.resPublic['stay_address_two']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxCity",
             self.resPublic['stay_city']),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbZIPCode",
             self.resPublic['stay_zip']),
        ]

        if self.resPublic['travel_cost_pay'] == 'O':
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerSurname",
                 self.resPublic['pay_personal_name']),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerGivenName",
                 self.resPublic['pay_personal_names']),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerPhone",
                 self.resPublic['pay_personal_phone']),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerPhone",
                 self.resPublic['pay_personal_phone']),
            ]
            if self.resPublic['pay_personal_email']:
                ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxPAYER_EMAIL_ADDR",
                            self.resPublic['pay_personal_email']))
            else:
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_cbxDNAPAYER_EMAIL_ADDR_NA", ""))
            # 与您的关系
            self.choiceSelect("ctl00_SiteContentPlaceHolder_FormView1_lblPayerRelationship",
                              self.resPublic['pay_personal_relation'])
            # 为您支付旅行费用的一方，其地址是否与您的家庭地址或邮寄地址相同？
            if self.resPublic['pay_personal_address_is'] == 'Y':
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblPayerAddrSameAsInd_0", ""))
            elif self.resPublic['pay_personal_address_is'] == 'N':
                ids += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblPayerAddrSameAsInd_1", ""),
                    ("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerStreetAddress1",
                     self.resPublic['pay_personal_address']),
                    ("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerStreetAddress2",
                     self.resPublic['pay_personal_address_two']),
                    ("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerCity",
                     self.resPublic['pay_personal_city']),
                ]
                if self.resPublic['pay_personal_province']:
                    ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerStateProvince",
                                self.resPublic['pay_personal_province']))
                else:
                    ids.append(
                        ("ctl00_SiteContentPlaceHolder_FormView1_cbxDNAPayerStateProvince", ""))
                if self.resPublic['pay_personal_zip']:
                    ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxPayerPostalZIPCode",
                                self.resPublic['pay_personal_zip']))
                else:
                    ids.append(
                        ("ctl00_SiteContentPlaceHolder_FormView1_cbxDNAPayerPostalZIPCode", ""))

                ids = self.waitIdSel(ids)
                self.choiceSelect(
                    "ctl00_SiteContentPlaceHolder_FormView1_ddlPayerCountry", self.resPublic['pay_personal_country'])

        ids = self.waitIdSel(ids, seList)

        # 州
        self.choiceSelect(
            "ctl00_SiteContentPlaceHolder_FormView1_ddlTravelState", self.resPublic['stay_province'])

        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '旅行:')
            return 1
        except:
            pass

        return 0

    def travelCompanions(self):
        """ 旅行同伴页 """
        #
        if self.resPublic["associate_is"] == "N":
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblOtherPersonsTravelingWithYou_1")
        elif self.resPublic["associate_is"] == "Y":
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblOtherPersonsTravelingWithYou_0")
            # 您是否作为一个团队或者组织的成员去旅行？
            if self.resPublic["associate_tuxedo_is"] == 'Y':
                self.Wait(
                    "ctl00_SiteContentPlaceHolder_FormView1_rblGroupTravel_0", "")
                self.Wait("ctl00_SiteContentPlaceHolder_FormView1_tbxGroupName",
                          self.resPublic["associate_tuxedo_name"])
            elif self.resPublic["associate_tuxedo_is"] == 'N':
                self.Wait(
                    "ctl00_SiteContentPlaceHolder_FormView1_rblGroupTravel_1")
                # 同行人姓(拼音) 、同行人名(拼音) 、 关系
                associate = json.loads(self.resPublic["associate_name_relation"])
                for index, value in enumerate(associate):
                    if index:
                        self.Wait(f"ctl00_SiteContentPlaceHolder_FormView1_dlTravelCompanions_ctl0{index - 1}_InsertButtonPrincipalPOT")
                    self.Wait(
                        f"ctl00_SiteContentPlaceHolder_FormView1_dlTravelCompanions_ctl0{index}_tbxSurname", value['name'])
                    self.Wait(
                        f"ctl00_SiteContentPlaceHolder_FormView1_dlTravelCompanions_ctl0{index}_tbxGivenName", value['name'])
                    self.choiceSelect(
                        f"ctl00_SiteContentPlaceHolder_FormView1_dlTravelCompanions_ctl0{index}_ddlTCRelationship", value['relation'])

        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '同行人:')
            return 1
        except:
            pass

        return 0

    def previousUSTravel(self):
        """ 以前美国之行 """
        # 您是否曾经在美国停留过？
        if self.resPublic["old_stay_is"] == 'Y':
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblPREV_US_TRAVEL_IND_0")
        elif self.resPublic["old_stay_is"] == 'N':
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblPREV_US_TRAVEL_IND_1")

        # 您是否曾经获得过美国签证?
        if self.resPublic["old_visa_is"] == 'Y':
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblPREV_VISA_IND_0")
        elif self.resPublic["old_visa_is"] == 'N':
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblPREV_VISA_IND_1")

        # 您被拒签过吗？ 或在入境口岸被拒入境，或被撤销入境申请？
        if self.resPublic["old_visa_refused_is"] == 'Y':
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblPREV_VISA_REFUSED_IND_0")
        elif self.resPublic["old_visa_refused_is"] == 'N':
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblPREV_VISA_REFUSED_IND_1")

        # 曾有人在公民及移民服务局为您申请过移民吗？
        if self.resPublic["old_visa_emigrate_is"] == 'Y':
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblIV_PETITION_IND_0")
        elif self.resPublic["old_visa_emigrate_is"] == 'N':
            self.Wait(
                "ctl00_SiteContentPlaceHolder_FormView1_rblIV_PETITION_IND_1")

        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '以往赴美:')
            return 1
        except:
            pass

        return 0

    def usContact(self):
        """ 美国联系人信息 """

        self.choiceSelect("ctl00_SiteContentPlaceHolder_FormView1_ddlUS_POC_REL_TO_APP",
                          self.resPublic["contact_relation"])

        if self.resPublic["contact_name"] and self.resPublic["contact_names"]:
            ids = [
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_SURNAME",
                 self.resPublic["contact_name"]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_GIVEN_NAME",
                 self.resPublic["contact_names"]),
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxUS_POC_ORG_NA_IND", ""),
            ]
        else:
            ids = [
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxUS_POC_NAME_NA", ""),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_ORGANIZATION",
                 self.resPublic["contact_group_name"])
            ]

        ids += [
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_ADDR_LN1",
             self.resPublic["contact_address"]),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_ADDR_LN2",
             self.resPublic["contact_address_two"]),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_ADDR_CITY",
             self.resPublic["contact_city"]),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_ADDR_POSTAL_CD",
             self.resPublic["contact_zip"]),
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_HOME_TEL",
             self.resPublic["contact_phone"]),
            
        ]
        if self.resPublic["contact_email"]:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxUS_POC_EMAIL_ADDR",
             self.resPublic["contact_email"]))
        else:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_cbexUS_POC_EMAIL_ADDR_NA", ""))
        self.waitIdSel(ids)
        self.choiceSelect("ctl00_SiteContentPlaceHolder_FormView1_ddlUS_POC_ADDR_STATE",
                          self.resPublic["contact_province"])
        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '美国联系人信息:')
            return 1
        except:
            pass

        return 0

    def relatives(self):
        ''' 家庭/亲属 '''
        ids = []
        seList = []
        # 父亲
        if not (self.resInfo['father_name'] or self.resInfo['father_names']):
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxFATHER_SURNAME_UNK_IND", ""),
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxFATHER_GIVEN_NAME_UNK_IND", ""),
            ]
        else:
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxFATHER_SURNAME",
                 self.resInfo["father_name"]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxFATHER_GIVEN_NAME",
                 self.resInfo["father_names"]),
            ]
            if not self.resInfo["father_birth"]:
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_cbxFATHER_DOB_UNK_IND", ""))
            else:
                year, month, day = self.resInfo["father_birth"].split("-")
                ids += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_tbxFathersDOBYear", year),
                ]
                seList += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_ddlFathersDOBMonth", MONTH[month]),
                    ("ctl00_SiteContentPlaceHolder_FormView1_ddlFathersDOBDay", day),
                ]
                
            if self.resInfo["father_america_is"] == "N":
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblFATHER_LIVE_IN_US_IND_1", ""))
            elif self.resInfo["father_america_is"] == "Y":
                ids += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblFATHER_LIVE_IN_US_IND_0", ""),
                    ("ctl00_SiteContentPlaceHolder_FormView1_ddlFATHER_US_STATUS",
                               self.resInfo["father_america_identity"])
                ]

        # 母亲
        if not (self.resInfo['mother_name'] or self.resInfo['mother_names']):
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxMOTHER_SURNAME_UNK_IND", ""),
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxMOTHER_GIVEN_NAME_UNK_IND", ""),
            ]
        else:
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxMOTHER_SURNAME",
                 self.resInfo["mother_name"]),
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxMOTHER_GIVEN_NAME",
                 self.resInfo["mother_names"]),
            ]
            if not self.resInfo["mother_birth"]:
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_cbxMOTHER_DOB_UNK_IND", ""))
            else:
                year, month, day = self.resInfo["mother_birth"].split("-")
                ids += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_tbxMothersDOBYear", year),
                ]
                seList += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_ddlMothersDOBMonth", MONTH[month]),
                    ("ctl00_SiteContentPlaceHolder_FormView1_ddlMothersDOBDay", day),
                ]
            if self.resInfo["mother_america_is"] == "N":
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblMOTHER_LIVE_IN_US_IND_1", ""))
            elif self.resInfo["mother_america_is"] == "Y":
                ids += [
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblMOTHER_LIVE_IN_US_IND_0", ""),
                    ("ctl00_SiteContentPlaceHolder_FormView1_ddlMOTHER_US_STATUS",
                               self.resInfo["mother_america_identity"])
                ]

        # 其它直系亲属
        if self.resInfo["other_america_is"] == "N":
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_rblUS_IMMED_RELATIVE_IND_1", ""))
            if self.resInfo["others_america_is"] == "Y":
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblUS_OTHER_RELATIVE_IND_0", ""))
            elif self.resInfo["others_america_is"] == "N":
                ids.append(
                    ("ctl00_SiteContentPlaceHolder_FormView1_rblUS_OTHER_RELATIVE_IND_1", ""))
        elif self.resInfo["other_america_is"] == "Y":
            ids += [
                ("ctl00_SiteContentPlaceHolder_FormView1_rblUS_IMMED_RELATIVE_IND_0", ""),
                # 姓氏
                ("ctl00_SiteContentPlaceHolder_FormView1_dlUSRelatives_ctl00_tbxUS_REL_SURNAME", ""),
                # 名字
                ("ctl00_SiteContentPlaceHolder_FormView1_dlUSRelatives_ctl00_tbxUS_REL_GIVEN_NAME", ""),
                # 与您的关系
                ("ctl00_SiteContentPlaceHolder_FormView1_dlUSRelatives_ctl00_ddlUS_REL_TYPE", ""),
                # 在美身份
                ("ctl00_SiteContentPlaceHolder_FormView1_dlUSRelatives_ctl00_ddlUS_REL_STATUS", ""),
            ]


        self.waitIdSel(ids, seList)
        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '家庭/亲属:')
            return 1
        except:
            pass

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
        return familyDict[self.resInfo["marriage"]]()

    def spouse(self):
        """ 配偶 """
        year, month, day = self.resInfo["spouse_birth"].split("-")
        ids = [
            # 配偶姓氏
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxSpouseSurname", self.resInfo["spouse_name"]),
            # 配偶名字
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxSpouseGivenName", self.resInfo["spouse_names"]),
            # 配偶生日: 年
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxDOBYear", year),
            # 配偶出生城市
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxSpousePOBCity", self.resInfo["spouse_birth_city"]),
        ]
        seList = [
            # 配偶生日: 日
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlDOBDay", day),
            # 配偶生日: 月
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlDOBMonth", MONTH[month]),
            # 配偶的所属国家/地区（国籍）(比如：中国大陆=“China”)
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlSpouseNatDropDownList", self.resInfo["spouse_nation"]),
            # 配偶的出生国家/地区
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlSpousePOBCountry", self.resInfo["spouse_birth_country"]),
            # 配偶的联系地址
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlSpouseAddressType", self.resInfo["spouse_address_select"]),
        ]
        ids = self.waitIdSel(ids, seList)
        seList = []
        # 配偶地址(选择其它时)
        if self.resInfo["spouse_address_select"] == "O":
            ids += [
                # 街道地址（第一行）
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxSPOUSE_ADDR_LN1", self.resInfo["spouse_address"]),
                # 街道地址（第二行）
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxSPOUSE_ADDR_LN2", self.resInfo["spouse_address_two"]),
                # 城市
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxSPOUSE_ADDR_CITY", self.resInfo["spouse_address_city"]),
            ]
            if self.resInfo["spouse_address_province"]:
                # 州/省
                ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxSPOUSE_ADDR_STATE", self.resInfo["spouse_address_province"]))
            else:
                ids.append(("ctl00_SiteContentPlaceHolder_FormView1_cbexSPOUSE_ADDR_STATE_NA", ""))

            if self.resInfo["spouse_address_code"]:
                # 邮编
                ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxSPOUSE_ADDR_POSTAL_CD", self.resInfo["spouse_address_code"]))
            else:
                ids.append(("ctl00_SiteContentPlaceHolder_FormView1_cbexSPOUSE_ADDR_POSTAL_CD_NA", ""))
            # 国家
            seList.append(("ctl00_SiteContentPlaceHolder_FormView1_ddlSPOUSE_ADDR_CNTRY", self.resInfo["spouse_address_country"]))

        self.waitIdSel(ids, seList)

        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '家庭/亲属:')
            return 1
        except:
            pass

        return 0

    def deceasedSpouse(self):
        """ 丧偶 """
        raise UsError("丧偶 未写")

    def prevSpouse(self):
        ''' 离异 '''
        ids = []
        seList = []
        self.Wait("ctl00_SiteContentPlaceHolder_FormView1_tbxNumberOfPrevSpouses", str(self.resInfo["spouse_former_count"]))
        for no, human in enumerate(json.loads(self.resInfo["spouse_former_info"])):
            idName = f"ctl00_SiteContentPlaceHolder_FormView1_DListSpouse_ctl0{no}_"
            if no:
                ids.append((f"{idName}InsertButtonSpouse", ""))
            year, month, day = human["former_birth_date"].split("-")
            wYear, wMonth, wDay = human["wedding_date"].split("-")
            dYear, dMonth, dDay = human["divorce_date"].split("-")
            # 离异人数
            ids += [
                (f"{idName}tbxGIVEN_NAME", human["former_names"]),
                (f"{idName}tbxDOBYear", year),
                (f"{idName}txtDomYear", wYear),
                (f"{idName}txtDomEndYear", dYear),
                (f"{idName}tbxHowMarriageEnded", human["divorce_info"]),
            ]
            if human["former_city"]:
                ids.append(
                    (f"{idName}tbxSpousePOBCity", human["former_city"]))
            else:
                ids.append((f"{idName}cbxSPOUSE_POB_CITY_NA", ""))
            seList += [
                (f"{idName}ddlDOBDay", day),
                (f"{idName}ddlDOBMonth", MONTH[month]),
                (f"{idName}ddlSpouseNatDropDownList",
                 human["former_country"]),
                (f"{idName}ddlSpousePOBCountry",
                 human["former_birth_country"]),
                (f"{idName}ddlDomDay", f"{int(wDay)}"),
                (f"{idName}ddlDomMonth", f"{int(wMonth)}"),
                (f"{idName}ddlDomEndDay", f"{int(dDay)}"),
                (f"{idName}ddlDomEndMonth", f"{int(dMonth)}"),
                (f"{idName}ddlMarriageEnded_CNTRY", human["divorce_country"]),
            ]

        self.waitIdSel(ids)

        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '离异:')
            return 1
        except:
            pass

        return 0

    def workEducation1(self):
        """ 工作教育 """
        self.choiceSelect("ctl00_SiteContentPlaceHolder_FormView1_ddlPresentOccupation",
                          self.resWork["professional_types"])
        seList = []

        year, month, day = self.resWork["induction_time"].split("-") if len(self.resWork["induction_time"]) > 3 else (0, 0, 0)

        ids = [
            # 当前工作单位或学校的名称
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxEmpSchName",
             self.resWork["company_name"]),
            # 街道地址（第一行）
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxEmpSchAddr1",
             self.resWork["company_address"]),
            # 街道地址（第二行）
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxEmpSchAddr2",
             self.resWork["company_address_two"]),
            # 城市
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxEmpSchCity",
             self.resWork["company_city"]),
            # 电话号码
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxWORK_EDUC_TEL",
             self.resWork["company_phone"]),
            # 入职年份
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxEmpDateFromYear", year),
            # 请简要描述您的工作职责：
            ("ctl00_SiteContentPlaceHolder_FormView1_tbxDescribeDuties",
             self.resWork["responsibility"]),
        ]
        seList += [
            # 所属日期
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlEmpDateFromDay", day),
            # 所属月份
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlEmpDateFromMonth", MONTH[month]),
        ]
        # 州/省份
        if self.resWork["company_province"]:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxWORK_EDUC_ADDR_STATE",
                        self.resWork["company_province"]))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxWORK_EDUC_ADDR_STATE_NA", ""))

        # 邮政区域/邮政编码
        if self.resWork["company_zip"]:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_tbxWORK_EDUC_ADDR_POSTAL_CD", self.resWork["company_zip"]))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxWORK_EDUC_ADDR_POSTAL_CD_NA", ""))

        # 月收入
        if self.resWork["month_income"]:
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_tbxCURR_MONTHLY_SALARY",
                        self.resWork["month_income"]))
        else:
            ids.append(
                ("ctl00_SiteContentPlaceHolder_FormView1_cbxCURR_MONTHLY_SALARY_NA", ""))

        seList += [
            # 所属国家
            ("ctl00_SiteContentPlaceHolder_FormView1_ddlEmpSchCountry",
             self.resWork["company_country"]),

        ]

        self.waitIdSel(ids, seList)

        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '工作教育:')
            return 1
        except:
            pass

        return 0

    def workEducation2(self):
        """ 以前的工作/培训 """
        ids = []
        seList = []

        # 您之前有工作吗？
        if self.resWork["five_work_is"] == "N":
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_rblPreviouslyEmployed_1", ""))
        elif self.resWork["five_work_is"] == "Y":
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_rblPreviouslyEmployed_0", ""))
            for no, work in enumerate(json.loads(self.resWork["five_work_info"])):
                ferId = f"ctl00_SiteContentPlaceHolder_FormView1_dtlPrevEmpl_ctl0{no}_"
                if no:
                    ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlPrevEmpl_ctl0{no-1}_InsertButtonPrevEmpl", ""))
                sYear, sMonth, sDay = work["induction_time"].split("-")
                eYear, eMonth, eDay = work["departure_time"].split("-")
                ids += [
                    # 公司名
                    (f"{ferId}tbEmployerName", work["company_name"].strip(".").replace(".,", "&")),
                    # 公司地址1
                    (f"{ferId}tbEmployerStreetAddress1", work["company_address"]),
                    # 公司地址2
                    (f"{ferId}tbEmployerStreetAddress2", work["company_address_two"]),
                    # 城市
                    (f"{ferId}tbEmployerCity", work["company_city"]),
                    # 电话
                    (f"{ferId}tbEmployerPhone", work["company_phone"]),
                    # 职位
                    (f"{ferId}tbJobTitle", work["position"]),
                    # 工作开始时间: 年
                    (f"{ferId}tbxEmpDateFromYear", sYear),
                    # 工作结束时间: 年
                    (f"{ferId}tbxEmpDateToYear", eYear),
                    # 简述工作职责
                    (f"{ferId}tbDescribeDuties", work["responsibility"]),
                ]
                seList += [
                     # 工作开始时间: 日
                    (f"{ferId}ddlEmpDateFromDay", sDay),
                    # 工作开始时间: 月
                    (f"{ferId}ddlEmpDateFromMonth", MONTH[sMonth]),
                    # 工作结束时间: 日
                    (f"{ferId}ddlEmpDateToDay", eDay),
                    # 工作结束时间: 月
                    (f"{ferId}ddlEmpDateToMonth", MONTH[eMonth]),
                ]
                # 州省
                if work["company_province"]:
                    ids.append((f"{ferId}tbxPREV_EMPL_ADDR_STATE", work["company_province"]))
                else:
                    ids.append((f"{ferId}cbxPREV_EMPL_ADDR_STATE_NA",""))
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
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_rblOtherEduc_1", ""))
        elif self.resWork["education_background"] == "Y":
            ids.append(("ctl00_SiteContentPlaceHolder_FormView1_rblOtherEduc_0", ""))

            for no, school in enumerate(json.loads(self.resWork["education_school"])):
                ferId = f"ctl00_SiteContentPlaceHolder_FormView1_dtlPrevEduc_ctl0{no}_"
                aYear, aMonth, aDay = school["admission_date"].split("-")
                gYear, gMonth, gDay = school["graduation_date"].split("-")
                if no:
                    ids.append((f"ctl00_SiteContentPlaceHolder_FormView1_dtlPrevEduc_ctl0{no - 1}_InsertButtonPrevEduc", ""))
                ids += [
                    # 学校名称
                    (f"{ferId}tbxSchoolName", school["name"]),
                    # 地址
                    (f"{ferId}tbxSchoolAddr1", school["address"]),
                    # 地址2
                    (f"{ferId}tbxSchoolAddr2", school["address_two"]),
                    # 城市
                    (f"{ferId}tbxSchoolCity", school["city"]),
                    # 课程
                    (f"{ferId}tbxSchoolCourseOfStudy", school["course"]),
                    # 就读日期: 年
                    (f"{ferId}tbxSchoolFromYear", aYear),
                    # 毕业日期: 年
                    (f"{ferId}tbxSchoolToYear", gYear),
                ]
                seList += [
                    # 就读日期: 日
                    (f"{ferId}ddlSchoolFromDay", aDay),
                    # 就读日期: 月
                    (f"{ferId}ddlSchoolFromMonth", MONTH[aMonth]),
                    # 毕业日期: 日
                    (f"{ferId}ddlSchoolToDay", gDay),
                    # 毕业日期: 月
                    (f"{ferId}ddlSchoolToMonth", MONTH[gMonth]),
                    # 国家
                    (f"{ferId}ddlSchoolCountry", school["country"])
                ]
                # 州省
                if school["province"]:
                    ids.append((f"{ferId}tbxEDUC_INST_ADDR_STATE",school["province"]))
                else:
                    ids.append((f"{ferId}cbxEDUC_INST_ADDR_STATE_NA",""))
                # 邮编
                if school["zip"]:
                    ids.append((f"{ferId}tbxEDUC_INST_POSTAL_CD",school["zip"]))
                else:
                    ids.append((f"{ferId}cbxEDUC_INST_POSTAL_CD_NA", ""))
                
                
        self.waitIdSel(ids, seList)
        sleep(2)
        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '以前的工作:')
            return 1
        except:
            pass

        return 0

    def workEducation3(self):
        """ 补充页 """
        ids = []

        # 您是否属于一个宗族或者部落？
        if self.resWork["religious_beliefs_is"] == "N":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblCLAN_TRIBE_IND_1")
        elif self.resWork["religious_beliefs_is"] == "Y":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblCLAN_TRIBE_IND_0")
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_tbxCLAN_TRIBE_NAME", self.resWork["religious_beliefs"])

        # 请列出您所说语言的种类
        lang = self.resWork["master_language"].split(',')[0].strip()
        self.Wait("ctl00_SiteContentPlaceHolder_FormView1_dtlLANGUAGES_ctl00_tbxLANGUAGE_NAME", lang)
        for language in self.resWork["master_language"].split(',')[1:]:
            language = language.strip()
            raise UsError("掌握其它语言")
        # 最近五年里您是否去过其他国家？
        if self.resWork["five_been_country_is"] == "N":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblCOUNTRIES_VISITED_IND_1")
        elif self.resWork["five_been_country_is"] == "Y":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblCOUNTRIES_VISITED_IND_0")
            
            for index, value in enumerate(json.loads(self.resWork["five_been_country"])):
                if index:
                    self.Wait(f"ctl00_SiteContentPlaceHolder_FormView1_dtlCountriesVisited_ctl0{index - 1}_InsertButtonCountriesVisited")
                self.choiceSelect(f"ctl00_SiteContentPlaceHolder_FormView1_dtlCountriesVisited_ctl0{index}_ddlCOUNTRIES_VISITED", value["name"])

        # 您是否从属于任何一个专业的、社会或慈善组织？并为其做过贡献、或为其工作过？
        if self.resWork["charity_is"] == "N":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblORGANIZATION_IND_1")
        elif self.resWork["charity_is"] == "Y":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblORGANIZATION_IND_0")
            for index, value in enumerate(json.loads(self.resWork["charity_name"])):
                if index:
                    self.Wait(f"ctl00_SiteContentPlaceHolder_FormView1_dtlORGANIZATIONS_ctl0{index - 1}_InsertButtonORGANIZATION")
                self.Wait(f"ctl00_SiteContentPlaceHolder_FormView1_dtlORGANIZATIONS_ctl0{index}_tbxORGANIZATION_NAME", value["name"])
            

        # 您是否具有特殊技能或接受过特殊培训，例如有关枪械、炸药、 核装置、 生物或化学方面的经验？
        if self.resWork["special_training_is"] == "N":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblSPECIALIZED_SKILLS_IND_1")
        elif self.resWork["special_training_is"] == "Y":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblSPECIALIZED_SKILLS_IND_0")
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_tbxSPECIALIZED_SKILLS_EXPL", self.resWork["special_training_info"])

        # 您是否曾经在军队服役？
        if self.resWork["army_is"] == "N":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblMILITARY_SERVICE_IND_1")
        elif self.resWork["army_is"] == "Y":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblMILITARY_SERVICE_IND_0")
            for index, value in enumerate(json.loads(self.resWork["army_info"])):
                sYear, sMonth, sDay = value["start_time"].split("-")
                eYear, eMonth, eDay = value["end_time"].split("-")
                if index:
                    self.Wait(f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index - 1}_InsertButtonMILITARY_SERVICE", "")
                ids += [
                    # 军种
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_BRANCH", value["services"]),
                    # 级别/职位
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_RANK", value["level"]),
                    # 军事特长
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_SPECIALTY", value["military"]),
                    # 服役开始日
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_FROMDay", sDay),
                    # 服役开始月份
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_FROMMonth", MONTH[sMonth]),
                    # 服役开始年份
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_FROMYear", sYear),
                    # 服役结束日
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_TODay", eDay),
                    # 服役结束月份
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_TOMonth", MONTH[eMonth]),
                    # 服役结束年份
                    (f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_tbxMILITARY_SVC_TOYear", eYear)
                ]
                ids = self.waitIdSel(ids)
                # 服役国家
                self.choiceSelect(f"ctl00_SiteContentPlaceHolder_FormView1_dtlMILITARY_SERVICE_ctl0{index}_ddlMILITARY_SVC_CNTRY",  value["country"])

        # 你是否曾经服务于或参与过准军事性单位、治安团体、造反组织、游击队或暴动组织，或曾经是其成员之一？
        if self.resWork["military_unit_is"] == "N":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblINSURGENT_ORG_IND_1")
        elif self.resWork["military_unit_is"] == "Y":
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_rblINSURGENT_ORG_IND_0")
            self.Wait("ctl00_SiteContentPlaceHolder_FormView1_tbxINSURGENT_ORG_EXPL", self.resWork["military_unit_info"])

        self.urlButton(__name__)
        try:
            errInfos = self.driver.find_element_by_id(
                "ctl00_SiteContentPlaceHolder_FormView1_ValidationSummary").text.split('\n')
            assert len(errInfos) > 1
            self.errJson(errInfos, '补充页:')
            return 1
        except:
            pass

        return 0

    def securityAndBackground(self):
        """ 安全与背景页 """
        ids1 = [
            ("ctl00_SiteContentPlaceHolder_FormView1_rblDisease_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblDisorder_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblDruguser_1", ""),
            ("ctl00_SiteContentPlaceHolder_UpdateButton3", ""),        
        ]

        ids2 = [
            ("ctl00_SiteContentPlaceHolder_FormView1_rblArrested_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblControlledSubstances_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblProstitution_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblMoneyLaundering_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblHumanTrafficking_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblAssistedSevereTrafficking_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblHumanTraffickingRelated_1", ""),
            ("ctl00_SiteContentPlaceHolder_UpdateButton3", ""),
        ]

        ids3 = [
            ("ctl00_SiteContentPlaceHolder_FormView1_rblIllegalActivity_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblTerroristActivity_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblTerroristSupport_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblTerroristOrg_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblGenocide_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblTorture_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblExViolence_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblChildSoldier_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblReligiousFreedom_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblPopulationControls_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblTransplant_1", ""),
            ("ctl00_SiteContentPlaceHolder_UpdateButton3", ""),
        ]

        ids4 = [
            ("ctl00_SiteContentPlaceHolder_FormView1_rblImmigrationFraud_1", ""),
            ("ctl00_SiteContentPlaceHolder_UpdateButton3", ""),
        ]

        ids5 = [
            ("ctl00_SiteContentPlaceHolder_FormView1_rblChildCustody_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblVotingViolation_1", ""),
            ("ctl00_SiteContentPlaceHolder_FormView1_rblRenounceExp_1", ""),
            ("ctl00_SiteContentPlaceHolder_UpdateButton3", ""),  
        ]
        
        idsDic = {
            "SecurityandBackground1": ids1,
            "SecurityandBackground2": ids2,
            "SecurityandBackground3": ids3,
            "SecurityandBackground4": ids4,
            "SecurityandBackground5": ids5,
        }
        node = self.getNode
        for i in range(int(node[-1]), 6):
            self.waitIdSel(idsDic[node[:-1] + str(i)])
        return 0

    def uploadPhoto(self):
        """ 上传照片页 """

        with open('usPhoto/photo.jpeg', 'wb') as f:
            f.write(requests.get(self.resInfo["photo"]).content)

        ids = [
            ("ctl00_SiteContentPlaceHolder_btnUploadPhoto", ""),
            ("ctl00_cphMain_imageFileUpload", BASEDIR + "\\usPhoto\\photo.jpeg"),
            ("ctl00_cphButtons_btnUpload", ""),
        ]
        ids = self.waitIdSel(ids)
        if "ctl00_cphError_errorUpload" in self.driver.page_source:
            info1 = self.driver.find_element("id", "ctl00_cphError_errorUpload").text
            if info1 == "Unable to read image memory into DibImage.":
                self.errJson(['', info1], '照片上传失败:')
                return 1

        info2 = self.driver.find_element("id", "ctl00_cphMain_qualityCheckOutcome").text

        if info2 == "Photo passed quality standards":
            print("照片上传成功")
        else:
            self.errJson(['', info2], '照片上传失败:')
            return 1
        
        ids = [
            ("ctl00_cphButtons_btnContinue", ""),
            ("ctl00_SiteContentPlaceHolder_UpdateButton3", "")
        ]

        self.waitIdSel(ids)
        return 0

    # def confirmPhoto(self):
        # """ 确认照片页 """
        # self.urlButton(__name__)
        # return 0

    def review(self):
        """ 审查页面 """
        self.Wait("ctl00_SiteContentPlaceHolder_UpdateButton3")
        return 0

    def signCertify(self):
        """ 最后确认页面 """
        self.Wait("ctl00_SiteContentPlaceHolder_FormView3_rblPREP_IND_1")
        self.Wait("ctl00_SiteContentPlaceHolder_PPTNumTbx", self.resInfo["passport_number"])
        while self.getNode != "Done":
            result = self.getCaptcha("c_general_esign_signtheapplication_ctl00_sitecontentplaceholder_defaultcaptcha_CaptchaImage")
            self.Wait("ctl00_SiteContentPlaceHolder_CodeTextBox", result)
            self.urlButton(__name__, 0)
            sleep(11111)
            self.Wait("ctl00_SiteContentPlaceHolder_btnSignApp")

    # 保存网址, 点击下一步(如有)
    def urlButton(self, name, button=1):
        self.allUrl.append({name: self.driver.current_url})
        if button:
            self.Wait("ctl00_SiteContentPlaceHolder_UpdateButton3")
        

    def __del__(self):
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
