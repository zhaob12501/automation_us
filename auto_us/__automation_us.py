# -*- coding: utf-8 -*-
"""
@author: ZhaoBin
@file: us_vs.py 
Created on 2018/5/7 17:24
"""
import json
import re
import time

import requests

from .pipelines import us_data
from .settings import CITY
from .yunsu import upload


class AutomationUS:
    '''美国签证自动化录入系统（模拟请求）

    '''
    def __init__(self):
        self.req = requests.Session()
        self.req.timeout = 600
        self.req.proxies = {
            # 'http': '127.0.0.1:8888',
            # 'https': '127.0.0.1:8888',
            'http': '127.0.0.1:1080',
            'https': '127.0.0.1:1080',
        }
        # self.req.verify = False
        print(self.req.proxies)
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        }
        self.req.headers = self.head
        self.us_url = 'https://ceac.state.gov/GenNIV/Default.aspx'
        self.verify_url = 'https://ceac.state.gov/GenNIV/Common/ConfirmApplicationID.aspx?node=SecureQuestion'
        self.info_url = 'https://ceac.state.gov/GenNIV/General/complete/complete_personal.aspx?node=Personal1'

        self.us_data = us_data()
        self.all_url = {}

    # @property
    # def proxy(self):
        # url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&pack=18448&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        # res = requests.get(url)
        # return res.text.strip()

    def getParameter(self, res):
        '''相同参数获取: 
        Returns:
            (viewstate, previouspage, viewstategenerator)
        '''
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

        return (viewstate, previouspage, viewstategenerator)

    def getCode(self, res):
        '''验证码图片识别
        Returns:
            result (str)  4 <= len(result) <= 6
        '''
        reg = r'<img class="LBD_CaptchaImage" id="c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage" src="(.*?)" alt="CAPTCHA" />'
        img_url = re.findall(reg, res.text)[0].replace('amp;', '')

        # print(f'https://ceac.state.gov{img_url}')
        img_url = f'https://ceac.state.gov{img_url}'
        # 获取验证码
        cont = self.req.get(img_url)

        img = cont.content
        self.all_url[f'code'] = img_url
        with open('code.png', 'wb') as f:
            f.write(img)

        time.sleep(5)
        print('开始识别验证码...')
        result = upload()
        print(f'验证码为：{result}...')
        return result

    @property
    def default(self):
        # 第一个请求 请求中文==========================================================================================-
        res = self.req.get(self.us_url)
        print(f'请求首页, 选择中文 ...')

        viewstate, previouspage, viewstategenerator = self.getParameter(res)
        reg = r'<input type="hidden" name="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" id="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" value="(.*?)" />'
        defaultcaptcha = re.findall(reg, res.text)[0]
        data = {
            "__EVENTTARGET": "ctl00$ddlLanguage",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__VIEWSTATEENCRYPTED": "",
            "__PREVIOUSPAGE": previouspage,
            "ctl00$ddlLanguage": "zh-CN",
            "ctl00$HDClearSession": "CLEARSESSION",
            "ctl00$SiteContentPlaceHolder$ucCultures$cpeLanguages_ClientState": "true",
            "ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation": "",
            "ctl00$SiteContentPlaceHolder$ucLocation$IdentifyCaptcha1$txtCodeTextBox": "",
            "LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha": defaultcaptcha,
            "LBD_BackWorkaround_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha": "1",
        }

        res = self.req.post(self.us_url, data=data)
        print('选择 中文页 ...')

        return res

    def choiceChn(self, res):
        '''选择国家, 设置用户信息及验证信息
        Returns:
            用户基本信息页的 response 属性: res
        '''

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        # 数据传输之  LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha
        reg = r'<input type="hidden" name="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" id="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" value="(.*?)" />'
        defaultcaptcha = re.findall(reg, res.text)[0]

        data1 = {
            '__EVENTTA RGET': 'ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': 'CLEARSESSION',
            'ctl00$SiteContentPlaceHolder$ucCultures$cpeLanguages_ClientState': 'true',
            'ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation': CITY["北京"],
            'ctl00$SiteContentPlaceHolder$ucLocation$IdentifyCaptcha1$txtCodeTextBox': '',
            'LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': defaultcaptcha,
            'LBD_BackWorkaround_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': '1',
        }

        # 第二个请求 ==================================================================================================-
        # 选择country  ==> CHINA BEIJING
        res = self.req.post(self.us_url, data=data1)
        print(f'请求 {CITY["北京"]}...')

        self.all_url[f'index_choice_{CITY["北京"]}'] = res.url
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        # 数据传输之  LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha
        reg = r'<input type="hidden" name="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" id="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" value="(.*?)" />'
        defaultcaptcha = re.findall(reg, res.text)[0]

        result = self.getCode(res)

        data2 = {
            'ctl00$ScriptManager1': 'ctl00$SiteContentPlaceHolder$UpdatePanel1|ctl00$SiteContentPlaceHolder$lnkNew',
            '__EVENTTARGET': 'ctl00$SiteContentPlaceHolder$lnkNew',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': 'CLEARSESSION',
            'ctl00$SiteContentPlaceHolder$ucCultures$cpeLanguages_ClientState': 'true',
            'ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation': CITY["北京"],
            'ctl00$SiteContentPlaceHolder$ucLocation$IdentifyCaptcha1$txtCodeTextBox': result,
            'LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': defaultcaptcha,
            'LBD_BackWorkaround_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': '1',
            '__ASYNCPOST': 'true'
        }

        # 第三个请求 ==================================================================================================-
        # 检测验证码，请求密保问题页
        res = self.req.post(self.us_url, data=data2)
        print(f'请求密保问题页，密保为：qwer ...')

        # 第四个请求（设置密保） ======================================================================================-
        url = 'https://ceac.state.gov/GenNIV/Common/ConfirmApplicationID.aspx?node=SecureQuestion'
        res = self.req.get(url)
        self.all_url[f'question'] = url

        reg = r'<span id="ctl00_SiteContentPlaceHolder_lblBarcode" class="barcode-large">(.*?)</span>'
        self.TXTCODETEXTBOX = re.findall(reg, res.text)[0]
        print(f'标识信息： {self.TXTCODETEXTBOX} ...')

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data3 = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': 'CLEARSESSION',
            'ctl00$SiteContentPlaceHolder$ddlQuestions': '1',
            'ctl00$SiteContentPlaceHolder$txtAnswer': 'qwer',
            'ctl00$SiteContentPlaceHolder$btnContinue': 'Continue',
        }

        # 第五个请求 （密保设置完成，进入信息填写页面）================================================================-
        res = self.req.post(self.verify_url, data=data3)
        print(f'密保设置完成')

        # 初始验证请求完成（开始填写信息） ============================================================================-

        return res

    def perInfo(self, res):
        '''添加 用户基本信息 data 并发送请求
        Returns:
            地址-电话页的 response 属性: res
        '''
        self.all_url['personal_1'] = res.url

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        ud = self.us_data[0]
        data1 = {
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_SURNAME': f'{ud[0]}',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_GIVEN_NAME': f'{ud[1]}',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_FULL_NAME_NATIVE': f'{ud[2]}',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_FULL_NAME_NATIVE_NA': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblOtherNames': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblTelecodeQuestion': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblAPP_GENDER': f'{ud[3]}',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlAPP_MARITAL_STATUS': f'{ud[4]}',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlDOBDay': f'{ud[5]}',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlDOBMonth': f'{ud[6]}',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxDOBYear': f'{ud[7]}',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_POB_CITY': f'{ud[8]}',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_POB_ST_PROVINCE_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexAPP_POB_ST_PROVINCE_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlAPP_POB_CNTRY': 'CHIN',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Personal 2',
            'ctl00$HiddenSideBarItemClicked': '',
            '__LASTFOCUS': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '884',
        }

        # 个人信息表第一个请求 ========================================================================================-
        res = self.req.post(res.url, data=data1)
        self.pre_info_url_2 = res.url
        print(f'填写 个人信息表（1）完成， {ud[2]}')
        self.all_url[f'persional_2'] = res.url
        self.veri = [self.TXTCODETEXTBOX, ud[0][:5], ud[7], 'qwer', '']


        viewstate, previouspage, _ = self.getParameter(res)

        data2 = {
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': 'False',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlAPP_NATL': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$rblAPP_OTH_NATL_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblPermResOtherCntryInd': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_NATIONAL_ID': ud[9],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_NATIONAL_ID_NA': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_SSN_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexAPP_SSN_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_TAX_ID_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexAPP_TAX_ID_NA': 'on',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Address and Phone',
            'ctl00$HiddenSideBarItemClicked': '',
            '__LASTFOCUS': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
        }

        # 个人信息表第二个请求 ========================================================================================-
        res = self.req.post(self.pre_info_url_2, data=data2)
        print(f'填写 个人信息表（2）完成， {ud[2]}')
        self.all_url[f'addr_phone'] = res.url

        return res

    def addrPhone(self, res):
        '''添加 地址-电话页 data 并发送请求
        Returns:
            护照页的 response 属性: res
        '''
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        uap = self.us_data[1]
        data1 = {
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_ADDR_LN1': uap[0],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_ADDR_LN2': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_ADDR_CITY': uap[1],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_ADDR_STATE_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexAPP_ADDR_STATE_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_ADDR_POSTAL_CD_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexAPP_ADDR_POSTAL_CD_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlCountry': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$rblMailingAddrSame': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_HOME_TEL': uap[2],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_MOBILE_TEL_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexAPP_MOBILE_TEL_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_BUS_TEL_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexAPP_BUS_TEL_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAPP_EMAIL_ADDR': uap[3],
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Passport',
            'ctl00$HiddenSideBarItemClicked': '',
            '__LASTFOCUS': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '307',
        }

        res = self.req.post(res.url, data=data1)
        print(f'填写 地址-电话页 完成')
        self.all_url[f'Paassport'] = res.url

        return res

    def passport(self, res):
        '''添加 护照页 data 并发送请求
        Returns:
            旅行计划页的 response 属性: res
        '''
        up = self.us_data[2]

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPPT_TYPE': 'R',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPPT_NUM': up[0],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPPT_BOOK_NUM_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexPPT_BOOK_NUM_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPPT_ISSUED_CNTRY': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$hfNationality': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPPT_ISSUED_IN_CITY': up[1],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPPT_ISSUED_IN_STATE': '',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPPT_ISSUED_IN_CNTRY': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPPT_ISSUED_DTEDay': up[2],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPPT_ISSUED_DTEMonth':  up[3],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPPT_ISSUEDYear':  up[4],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPPT_EXPIRE_DTEDay':  up[5],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPPT_EXPIRE_DTEMonth':  up[6],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPPT_EXPIREYear':  up[7],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPPT_EXPIRE_NA': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblLOST_PPT_IND': up[8],
            # 'ctl00$SiteContentPlaceHolder$FormView1$rblLOST_PPT_IND': 'Y',
            # 'ctl00$SiteContentPlaceHolder$FormView1$dtlLostPPT$ctl00$tbxLOST_PPT_NUM': 'G59897649',
            # 'ctl00$SiteContentPlaceHolder$FormView1$dtlLostPPT$ctl00$ddlLOST_PPT_NATL': 'CHIN',
            # 'ctl00$SiteContentPlaceHolder$FormView1$dtlLostPPT$ctl00$tbxLOST_PPT_EXPL': '111',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Travel',
            'ctl00$SiteContentPlaceHolder$ddlPPT_ISSUED_CNTRY': '',
            'ctl00$SiteContentPlaceHolder$ddlNationality': '',
            'ctl00$HiddenSideBarItemClicked': '',
            '__LASTFOCUS': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '198',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 护照页 完成')
        self.all_url[f'Travel'] = res.url

        return res

    def travel(self, res):
        '''添加 旅行计划页 data 并发送请求
        Returns:
            同行人员页的 response 属性: res
        '''
        no = -5
        while no < 0:
            up = self.us_data[3]

            viewstate, previouspage, viewstategenerator = self.getParameter(
                res)

            data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstategenerator,
                '__PREVIOUSPAGE': previouspage,
                'ctl00$ddlLanguage': 'zh-CN',
                'ctl00$HDClearSession': '',
                'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
                'ctl00$SiteContentPlaceHolder$FormView1$hfSite': CITY['北京'],
                'ctl00$SiteContentPlaceHolder$FormView1$hfVisaClass': '',
                'ctl00$SiteContentPlaceHolder$FormView1$dlPrincipalAppTravel$ctl00$ddlPurposeOfTrip': up[0],
                'ctl00$SiteContentPlaceHolder$FormView1$dlPrincipalAppTravel$ctl00$ddlOtherPurpose': up[1],
                'ctl00$SiteContentPlaceHolder$FormView1$rblSpecificTravel': 'N',
                'ctl00$SiteContentPlaceHolder$FormView1$ddlTRAVEL_DTEDay': up[2],
                'ctl00$SiteContentPlaceHolder$FormView1$ddlTRAVEL_DTEMonth': up[3],
                'ctl00$SiteContentPlaceHolder$FormView1$tbxTRAVEL_DTEYear': up[4],
                'ctl00$SiteContentPlaceHolder$FormView1$tbxTRAVEL_LOS': up[5],
                'ctl00$SiteContentPlaceHolder$FormView1$ddlTRAVEL_LOS_CD': up[6],
                'ctl00$SiteContentPlaceHolder$FormView1$tbxStreetAddress1': up[7],
                'ctl00$SiteContentPlaceHolder$FormView1$tbxStreetAddress2': '',
                'ctl00$SiteContentPlaceHolder$FormView1$tbxCity': up[8],
                'ctl00$SiteContentPlaceHolder$FormView1$ddlTravelState': up[9],
                'ctl00$SiteContentPlaceHolder$FormView1$tbZIPCode': up[10],
                'ctl00$SiteContentPlaceHolder$FormView1$ddlWhoIsPaying': up[11],
                'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Travel Companions',
                'ctl00$HiddenSideBarItemClicked': '',
            }

            res = self.req.post(res.url, data=data)
            if res.url == 'https://ceac.state.gov/GenNIV/General/complete/complete_travelcompanions.aspx?node=TravelCompanions':
                break
            no += 1
        if no == 0:
            return 0
        print(f'填写 旅行计划页 完成')

        self.all_url[f'Travel Companions'] = res.url

        return res

    def travelCompanions(self, res):
        '''添加 同行人员页 data 并发送请求
        Returns:
            以前美国之行页的 response 属性: res
        '''

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblOtherPersonsTravelingWithYou': 'N',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Previous U.S. Travel',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 同行人员页 完成')
        self.all_url['PreviousUSTravel'] = res.url

        return res

    def previousUSTravel(self, res):
        '''添加 以前美国之行页 data 并发送请求
        Returns:
            美国友人(组织)页的 response 属性: res
        '''

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblPREV_US_TRAVEL_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblPREV_VISA_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblPREV_VISA_REFUSED_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblIV_PETITION_IND': 'N',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: U.S. Contact',
            'ctl00$HiddenSideBarItemClicked': '',
            '__LASTFOCUS': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 以前美国之行页 完成')
        self.all_url['USContact'] = res.url

        return res

    def usContact(self, res):
        '''添加 美国友人(组织)页 data 并发送请求
        Returns:
            美国亲属页的 response 属性: res
        '''
        up = self.us_data[4]

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_SURNAME': up[0],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_GIVEN_NAME': up[1],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_NAME_NA': up[2],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_ORG_NA_IND': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbxUS_POC_ORG_NA_IND': up[3],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlUS_POC_REL_TO_APP': up[4],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_ADDR_LN1': up[5],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_ADDR_LN2': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_ADDR_CITY': up[6],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlUS_POC_ADDR_STATE': up[7],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_ADDR_POSTAL_CD': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_HOME_TEL': up[8],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxUS_POC_EMAIL_ADDR_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexUS_POC_EMAIL_ADDR_NA': 'on',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Family',
            'ctl00$HiddenSideBarItemClicked': '',
            '__LASTFOCUS': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '300',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 美国友人(组织)页 完成')
        self.all_url['Relatives'] = res.url

        return res

    def relatives(self, res):
        '''添加 美国亲属页 data 并发送请求
        Returns:
            配偶信息页的 response 属性: res
        '''
        no = -5
        while no < 0:
            viewstate, previouspage, viewstategenerator = self.getParameter(
                res)

            data = {
                '__PREVIOUSPAGE': previouspage,
                'ctl00$ddlLanguage': 'zh-CN',
                'ctl00$HDClearSession': '',
                'ctl00$SiteContentPlaceHolder$HiddenPageValid': 'False',
                'ctl00$SiteContentPlaceHolder$FormView1$tbxFATHER_SURNAME_UNK_IND': 'Y',
                'ctl00$SiteContentPlaceHolder$FormView1$cbxFATHER_SURNAME_UNK_IND': 'on',
                'ctl00$SiteContentPlaceHolder$FormView1$tbxFATHER_GIVEN_NAME_UNK_IND': 'Y',
                'ctl00$SiteContentPlaceHolder$FormView1$cbxFATHER_GIVEN_NAME_UNK_IND': 'on',
                'ctl00$SiteContentPlaceHolder$FormView1$tbxFATHER_DOB_UNK_IND': 'Y',
                'ctl00$SiteContentPlaceHolder$FormView1$tbxMOTHER_SURNAME_UNK_IND': 'Y',
                'ctl00$SiteContentPlaceHolder$FormView1$cbxMOTHER_SURNAME_UNK_IND': 'on',
                'ctl00$SiteContentPlaceHolder$FormView1$tbxMOTHER_GIVEN_NAME_UNK_IND': 'Y',
                'ctl00$SiteContentPlaceHolder$FormView1$cbxMOTHER_GIVEN_NAME_UNK_IND': 'on',
                'ctl00$SiteContentPlaceHolder$FormView1$tbxMOTHER_DOB_UNK_IND': 'N',
                'ctl00$SiteContentPlaceHolder$FormView1$rblUS_IMMED_RELATIVE_IND': 'N',
                'ctl00$SiteContentPlaceHolder$FormView1$rblUS_OTHER_RELATIVE_IND': 'N',
                'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Spouse',
                'ctl00$HiddenSideBarItemClicked': '',
                '__LASTFOCUS': '',
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstategenerator,
                '__SCROLLPOSITIONX': '0',
                '__SCROLLPOSITIONY': '0',
            }

            res = self.req.post(res.url, data=data)

            if res.url == 'https://ceac.state.gov/GenNIV/General/complete/complete_family2.aspx?node=Spouse':
                break
        print(f'填写 美国亲属页 完成')
        self.all_url['Spouse'] = res.url

        return res

    def spouse(self, res):
        '''添加 配偶信息页 data 并发送请求
        Returns:
            现在的工作页的 response 属性: res
        '''
        up = self.us_data[5]

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '107',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxSpouseSurname': up[0],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxSpouseGivenName': up[1],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlDOBDay': up[2],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlDOBMonth': up[3],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxDOBYear': up[4],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlSpouseNatDropDownList': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxSpousePOBCity_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbexSPOUSE_POB_CITY_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlSpousePOBCountry': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlSpouseAddressType': up[5],
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Work/Education/Training',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 配偶信息页 完成')
        self.all_url['Present'] = res.url

        return res

    def present(self, res):
        '''添加 现在的工作页 data 并发送请求
        Returns:
            以前的工作页的 response 属性: res
        '''
        up = self.us_data[6]

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': 'False',
            'ctl00$SiteContentPlaceHolder$FormView1$HiddenPageChanged': '',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlPresentOccupation': up[0],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxEmpSchName': up[1],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxEmpSchAddr1': up[2],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxEmpSchAddr2': '',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxEmpSchCity': up[3],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxWORK_EDUC_ADDR_STATE_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbxWORK_EDUC_ADDR_STATE_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxWORK_EDUC_ADDR_POSTAL_CD_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbxWORK_EDUC_ADDR_POSTAL_CD_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxWORK_EDUC_TEL': up[4],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlEmpSchCountry': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$ddlEmpDateFromDay': up[5],
            'ctl00$SiteContentPlaceHolder$FormView1$ddlEmpDateFromMonth': up[6],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxEmpDateFromYear': up[7],
            'ctl00$SiteContentPlaceHolder$FormView1$tbxCURR_MONTHLY_SALARY_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$cbxCURR_MONTHLY_SALARY_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxDescribeDuties': up[8],
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Work/Education: Previous',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 现在的工作页 完成')
        self.all_url['Previous'] = res.url

        return res

    def previous(self, res):
        '''添加 以前的工作页 data 并发送请求
        Returns:
            补充页的 response 属性: res
        '''
        up = self.us_data[7]

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblPreviouslyEmployed': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbEmployerName': up[0],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbEmployerStreetAddress1': up[1],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbEmployerStreetAddress2': '',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbEmployerCity': up[2],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$cbxPREV_EMPL_ADDR_STATE_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$cbxPREV_EMPL_ADDR_POSTAL_CD_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$DropDownList2': 'CHIN',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbEmployerPhone': up[3],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbJobTitle': up[4],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbSupervisorSurname_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$cbxSupervisorSurname_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbSupervisorGivenName_NA': 'Y',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$cbxSupervisorGivenName_NA': 'on',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$ddlEmpDateFromDay': up[5],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$ddlEmpDateFromMonth': up[6],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbxEmpDateFromYear': up[7],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$ddlEmpDateToDay': up[8],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$ddlEmpDateToMonth': up[9],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbxEmpDateToYear': up[10],
            'ctl00$SiteContentPlaceHolder$FormView1$dtlPrevEmpl$ctl00$tbDescribeDuties': up[11],
            'ctl00$SiteContentPlaceHolder$FormView1$rblOtherEduc': 'N',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Work/Education: Additional',
            'ctl00$HiddenSideBarItemClicked': '',
            '__LASTFOCUS': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '846',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 以前的工作页 完成')
        self.all_url['Additional'] = res.url

        return res

    def additional(self, res):
        '''添加 补充页 data 并发送请求
        Returns:
            安全与背景页的 response 属性: res
        '''

        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '270',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblCLAN_TRIBE_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$dtlLANGUAGES$ctl00$tbxLANGUAGE_NAME': 'chinese',
            'ctl00$SiteContentPlaceHolder$FormView1$rblCOUNTRIES_VISITED_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblORGANIZATION_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblSPECIALIZED_SKILLS_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxSPECIALIZED_SKILLS_EXPL': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblMILITARY_SERVICE_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$rblINSURGENT_ORG_IND': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxINSURGENT_ORG_EXPL': '',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Security and Background',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 补充页 完成')
        self.all_url['SecurityAndBackground1'] = res.url

        return res

    def securityAndBackground(self, res):
        '''添加 安全与背景页(5页) data 并发送请求
        Returns:
            照片页的 response 属性: res
        '''

        # 安全与背景页-1
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblDisease': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxDisease': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblDisorder': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxDisorder': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblDruguser': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxDruguser': '',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Security/Background Part 2',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 安全与背景页1 完成')
        self.all_url['SecurityAndBackground2'] = res.url

        # 安全与背景页-2
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '428',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblArrested': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxArrested': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblControlledSubstances': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxControlledSubstances': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblProstitution': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxProstitution': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblMoneyLaundering': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxMoneyLaundering': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblHumanTrafficking': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxHumanTrafficking': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblAssistedSevereTrafficking': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxAssistedSevereTrafficking': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblHumanTraffickingRelated': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxHumanTraffickingRelated': '',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Security/Background Part 3',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 安全与背景页2 完成')
        self.all_url['SecurityAndBackground3'] = res.url

        # 安全与背景页-3
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '786',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblIllegalActivity': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxIllegalActivity': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblTerroristActivity': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxTerroristActivity': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblTerroristSupport': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxTerroristSupport': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblTerroristOrg': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxTerroristOrg': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblGenocide': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxGenocide': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblTorture': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxTorture': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblExViolence': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxExViolence': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblChildSoldier': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxChildSoldier': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblReligiousFreedom': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxReligiousFreedom': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblPopulationControls': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxPopulationControls': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblTransplant': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxTransplant': '',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Security/Background Part 4',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 安全与背景页3 完成')
        self.all_url['SecurityAndBackground4'] = res.url

        # 安全与背景页-4
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblImmigrationFraud': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxImmigrationFraud': '',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: Security/Background Part 5',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 安全与背景页4 完成')
        self.all_url['SecurityAndBackground5'] = res.url

        # 安全与背景页-5
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
            '__PREVIOUSPAGE': previouspage,
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': '',
            'ctl00$SiteContentPlaceHolder$HiddenPageValid': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblChildCustody': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxChildCustody': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblVotingViolation': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxVotingViolation': '',
            'ctl00$SiteContentPlaceHolder$FormView1$rblRenounceExp': 'N',
            'ctl00$SiteContentPlaceHolder$FormView1$tbxRenounceExp': '',
            'ctl00$SiteContentPlaceHolder$UpdateButton3': 'Next: PHOTO',
            'ctl00$HiddenSideBarItemClicked': '',
        }

        res = self.req.post(res.url, data=data)

        print(f'填写 安全与背景页5 完成')
        self.all_url['UploadPhoto'] = res.url

        return res




    def continueTo(self):
        res = self.default
        up = self.us_data[0]
        result = self.getCode(res)
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

        # 数据传输之  LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha
        reg = r'<input type="hidden" name="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" id="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" value="(.*?)" />'
        defaultcaptcha = re.findall(reg, res.text)[0]

        data1 = {
            "ctl00$ScriptManager1": "ctl00$SiteContentPlaceHolder$UpdatePanel1|ctl00$SiteContentPlaceHolder$lnkRetrieve",
            "__EVENTTARGET": "ctl00$SiteContentPlaceHolder$lnkRetrieve",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__VIEWSTATEENCRYPTED": "",
            "__PREVIOUSPAGE": previouspage,
            "ctl00$ddlLanguage": "zh-CN",
            "ctl00$HDClearSession": "CLEARSESSION",
            "ctl00$SiteContentPlaceHolder$ucCultures$cpeLanguages_ClientState": "true",
            "ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation": "",
            "ctl00$SiteContentPlaceHolder$ucLocation$IdentifyCaptcha1$txtCodeTextBox": result,
            "LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha": defaultcaptcha,
            "LBD_BackWorkaround_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha": "1",
            "__ASYNCPOST": "true",
        }

        print('进入 填写验证信息页 ...')
        self.req.post(self.us_url, data=data1)
        recoveryUrl = 'https://ceac.state.gov/GenNIV/common/Recovery.aspx'
        res = self.req.get(recoveryUrl)

        viewstate, previouspage, viewstategenerator = self.getParameter(res)
        data2 = {
            "ctl00$ScriptManager1": "ctl00$SiteContentPlaceHolder$updPanelApplication|ctl00$SiteContentPlaceHolder$ApplicationRecovery1$btnBarcodeSubmit",
            "__LASTFOCUS": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__PREVIOUSPAGE": previouspage,
            "ctl00$ddlLanguage": "zh-CN",
            "ctl00$HDClearSession": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$tbxApplicationID": up[10],
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$ddlLocation": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbSname": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbYear": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$ddlQuestions": "1",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbAnswer1": "",
            "ctl00$HiddenSideBarItemClicked": "",
            "__ASYNCPOST": "true",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$btnBarcodeSubmit": "Retrieve Application",
        }
        print('验证 AA码 ...')
        res = self.req.post(recoveryUrl, data=data2)

        viewstate, previouspage, viewstategenerator = self.getParameter(res)
        data3 = {
            "ctl00$ScriptManager1": "ctl00$SiteContentPlaceHolder$updPanelApplication|ctl00$SiteContentPlaceHolder$ApplicationRecovery1$btnRetrieve",
            "__PREVIOUSPAGE": previouspage,
            "ctl00$ddlLanguage": "zh-CN",
            "ctl00$HDClearSession": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$tbxApplicationID": up[10],
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbSurname": up[0],
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbDOBYear": up[7],
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbAnswer": "qwer",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$ddlLocation": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbSname": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbYear": "",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$ddlQuestions": "1",
            "ctl00$SiteContentPlaceHolder$ApplicationRecovery1$txbAnswer1": "",
            "ctl00$HiddenSideBarItemClicked": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__ASYNCPOST": "true",
        }
        print('验证 姓(前五位) 出生年份 自定义信息 ...')
        res = self.req.post(recoveryUrl, data=data3)
        viewstate, previouspage, viewstategenerator = self.getParameter(res)

    @property
    def runProcess(self):
        res = self.default
        func_list = [
            self.choiceChn,
            self.perInfo,
            self.addrPhone,
            self.passport,
            self.travel,
            self.travelCompanions,
            self.previousUSTravel,
            self.usContact,
            self.relatives,
            self.spouse,
            self.present,
            self.previous,
            self.additional,
            self.securityAndBackground,
            # self.uploadPhoto,
            # self.upload,
            # self.Result,
            # self.confirmPhoto,
            # self.reviewPersonal,
            # self.reviewTravel,
        ]
        for func in func_list:
            res = func(res)
            if not res:
                print('页面获取错误, 返回出错函数名')
                self.veri[4] = func.__name__
                return (func.__name__, )    # 出错函数之后的函数名
            elif type(res) is tuple:
                return res


if __name__ == "__main__":
    u = AutomationUS()
    u.runProcess

    with open('veri.json', 'a')as f:
        f.write(',\n')
        json.dump(u.veri, f)

    with open('all_url.json', 'w') as f:
        json.dump(u.all_url, f)

    print()

    for i in u.all_url:
        print(f'{i}\n  {u.all_url[i]} ...')















    # def uploadPhoto(self, res):
    #     '''添加 照片页 data 并发送请求
    #     Returns:
    #         上传照片页的 response 属性: res
    #     '''
    #     viewstate, previouspage, viewstategenerator = self.getParameter(res)
    #     data = {
    #         '__EVENTTARGET': '',
    #         '__EVENTARGUMENT': '',
    #         '__LASTFOCUS': '',
    #         '__VIEWSTATE': viewstate,
    #         '__VIEWSTATEGENERATOR': viewstategenerator,
    #         '__PREVIOUSPAGE': previouspage,
    #         'ctl00$ddlLanguage': 'zh-CN',
    #         'ctl00$HDClearSession': '',
    #         'ctl00$SiteContentPlaceHolder$btnUploadPhoto': '',
    #         'ctl00$HiddenSideBarItemClicked': '',
    #     }

    #     res = self.req.post(res.url, data=data)
    #     with open('uploadPhoto.html', 'wb') as f:
    #         f.write(res.content) 
    #     print(f'点击 上传照片')
    #     self.all_url['Upload'] = res.url

    #     return res

    # def upload(self, res):
    #     '''进行照片上传
    #     Returns:
    #         上传完成页面的 response 属性: res
    #     '''
    #     reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
    #     viewstate = re.findall(reg, res.text)[0]

    #     reg = r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />'
    #     eventvalidation = re.findall(reg, res.text)[0]

    #     reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
    #     viewstategenerator = re.findall(reg, res.text)[0]

    #     file = {
    #         "__VIEWSTATE": (None, viewstate),
    #         "__VIEWSTATEGENERATOR": (None, viewstategenerator),
    #         "__EVENTVALIDATION": (None, eventvalidation),
    #         "ctl00$cphMain$imageFileUpload": ('photo.jpeg', open("photo.jpeg", 'rb'), 'image/jpeg'),
    #         "ctl00$cphButtons$btnUpload.x": (None, '130'),
    #         "ctl00$cphButtons$btnUpload.y": (None, '11'),
    #     }

    #     res = self.req.post(res.url, files=file)

    #     with open('upload.html', 'wb') as f:
    #         f.write(res.content)

    #     print(f'上传照片')
    #     self.all_url['Result'] = res.url

    #     if 'Photo passed quality standards' in res.text:
    #         print('上传成功!')
    #         return res

    #     elif 'There was a missing or invalid parameter in the request' in res.text:
    #         print('请求中存在缺少或无效的参数')

    #     return (self.upload.__name__, )

    # def Result(self, res):
    #     '''照片上传完成, 点击下一步
    #     Returns:
    #         保存页的 response 属性: res
    #     '''
    #     reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
    #     viewstate = re.findall(reg, res.text)[0]

    #     reg = r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />'
    #     eventvalidation = re.findall(reg, res.text)[0]

    #     reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
    #     viewstategenerator = re.findall(reg, res.text)[0]

    #     data = {
    #         '__VIEWSTATE': viewstate,
    #         '__VIEWSTATEGENERATOR': viewstategenerator,
    #         '__EVENTVALIDATION': eventvalidation,
    #         'ctl00$cphButtons$btnContinue.x': '133',
    #         'ctl00$cphButtons$btnContinue.y': '13',
    #     }

    #     res = self.req.post(res.url, data=data)
    #     self.all_url['confirmPhoto'] = res.url
    #     print('进入 保存照片页...')
    #     with open('confirmPhoto.html', 'wb') as f:
    #         f.write(res.content)
    #     return res

    # def confirmPhoto(self, res):
    #     '''照片保存完成, 点击下一步
    #     Returns:
    #         检查页的 response 属性: res
    #     '''
    #     while 1:
    #         viewstate, previouspage, viewstategenerator = self.getParameter(res)

    #         data = {
    #             "__EVENTTARGET": "ctl00$SiteContentPlaceHolder$UpdateButton3",
    #             "__EVENTARGUMENT": "",
    #             "__LASTFOCUS": "",
    #             "__VIEWSTATE": viewstate,
    #             "__VIEWSTATEGENERATOR": viewstategenerator,
    #             "__PREVIOUSPAGE": previouspage,
    #             "ctl00$ddlLanguage": "zh-CN",
    #             "ctl00$HDClearSession": "",
    #             "ctl00$HiddenSideBarItemClicked": "",
    #         }

    #         res = self.req.post(res.url, data=data)
    #         self.all_url['reviewPersonal'] = res.url
    #         print('进入 检查页...')

    #         reg = r'<img id="ctl00_SiteContentPlaceHolder_Image1" src="\.\./\.\.(.*?)" style="border-width:0px;">'
    #         photoUrl = 'https://ceac.state.gov/GenNIV' + re.findall(reg, res.text)[0].replace('amp;', '')
    #         with open('_photo.jpeg', 'wb') as f:
    #             f.write(self.req.get(photoUrl).content)

    #         with open('save.html', 'wb') as f:
    #             f.write(res.content)
    #         if res != 'https://ceac.state.gov/GenNIV/General/photo/photo_confirmphoto.aspx?node=ConfirmPhoto&save':
    #             break
    #     return res

    # def reviewPersonal(self, res):
    #     '''检查完成, 点击下一步
    #     Returns:
    #         _页的 response 属性: res
    #     '''
    #     viewstate, previouspage, viewstategenerator = self.getParameter(res)

    #     data = {
    #         "__EVENTTARGET": "",
    #         "__EVENTARGUMENT": "",
    #         "__LASTFOCUS": "",
    #         "__VIEWSTATE": viewstate,
    #         "__VIEWSTATEGENERATOR": viewstategenerator,
    #         "__PREVIOUSPAGE": previouspage,
    #         "ctl00$ddlLanguage": "zh-CN",
    #         "ctl00$HDClearSession": "",
    #         "ctl00$SiteContentPlaceHolder$UpdateButton3": "Next: Travel",
    #         "ctl00$HiddenSideBarItemClicked": "",            
    #     }

    #     res = self.req.post(res.url, data=data)
    #     self.all_url['ReviewTravel'] = res.url
    #     print('进入 _页...')

    #     return res

    # def reviewTravel(self, res):
    #     '''_完成, 点击下一步
    #     Returns:
    #         _页的 response 属性: res
    #     '''
    #     viewstate, previouspage, viewstategenerator = self.getParameter(res)

    #     data = {

    #     }

    #     res = self.req.post(res.url, data=data)
    #     self.all_url['_'] = res.url
    #     print('进入 _页...')

    #     return res

    # def _(self, res):
    #     '''_完成, 点击下一步
    #     Returns:
    #         _页的 response 属性: res
    #     '''
    #     viewstate, previouspage, viewstategenerator = self.getParameter(res)

    #     data = {

    #     }

    #     res = self.req.post(res.url, data=data)
    #     self.all_url['_'] = res.url
    #     print('进入 _页...')

    #     return res

    # def _(self, res):
    #     '''_完成, 点击下一步
    #     Returns:
    #         _页的 response 属性: res
    #     '''
    #     viewstate, previouspage, viewstategenerator = self.getParameter(res)

    #     data = {

    #     }

    #     res = self.req.post(res.url, data=data)
    #     self.all_url['_'] = res.url
    #     print('进入 _页...')

    #     return res

    # def _(self, res):
    #     '''_完成, 点击下一步
    #     Returns:
    #         _页的 response 属性: res
    #     '''
    #     viewstate, previouspage, viewstategenerator = self.getParameter(res)

    #     data = {

    #     }

    #     res = self.req.post(res.url, data=data)
    #     self.all_url['_'] = res.url
    #     print('进入 _页...')

    #     return res

    # def _(self, res):
    #     '''_完成, 点击下一步
    #     Returns:
    #         _页的 response 属性: res
    #     '''
    #     viewstate, previouspage, viewstategenerator = self.getParameter(res)

    #     data = {

    #     }

    #     res = self.req.post(res.url, data=data)
    #     self.all_url['_'] = res.url
    #     print('进入 _页...')

    #     return res
