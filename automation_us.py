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

from pipelines import us_data
from settings import E_NAME, E_NAME_2, NAME, CITY
from yunsu import upload


class UsVisa:
    def __init__(self):
        self.req = requests.Session()
        self.req.timeout = 60
        # self.req.proxies = {
        #     'http': '127.0.0.1:8888',
        #     'https': '127.0.0.1:8888'
        # }
        # print(self.req.proxies)
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        }
        self.req.headers = self.head
        self.us_url = 'https://ceac.state.gov/genniv/'
        self.verify_url = 'https://ceac.state.gov/GenNIV/Common/ConfirmApplicationID.aspx?node=SecureQuestion'
        self.info_url = 'https://ceac.state.gov/GenNIV/General/complete/complete_personal.aspx?node=Personal1'

        self.us_data = us_data()
        self.all_url = {}

    # @property
    # def proxy(self):
    #     url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&pack=18448&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    #     res = requests.get(url)
    #     return res.text.strip()

    @property
    def choice_chn(self):
        # 第一个请求 ==================================================================================================-
        res = self.req.get(self.us_url)
        print(f'请求第一页...')
        self.all_url[f'index_choice_{CITY["北京"]}'] = res.url
        # 打印第一页 验证使用， 成功后可不用
        # with open('us_html/0-1.html', 'wb')as f:
        #     f.write(res.content)

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        # 数据传输之  LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha
        reg = r'<input type="hidden" name="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" id="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" value="(.*?)" />'
        defaultcaptcha = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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

        # 打印第2页 验证使用， 成功后可不用
        # with open('us_html/0-2.html', 'wb')as f:
        #     f.write(res.content)

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        # 数据传输之  LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha
        reg = r'<input type="hidden" name="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" id="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" value="(.*?)" />'
        defaultcaptcha = re.findall(reg, res.text)[0]

        # 验证码图片URL获取
        reg = r'<img class="LBD_CaptchaImage" id="c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha_CaptchaImage" src="(.*?)" alt="CAPTCHA" />'
        img_url = re.findall(reg, res.text)[0].replace('amp;', '')

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

        # print(f'https://ceac.state.gov{img_url}')
        img_url = f'https://ceac.state.gov{img_url}'
        # 获取验证码
        cont = self.req.get(img_url)
        # print(cont.status_code)
        img = cont.content
        self.all_url[f'code'] = img_url
        with open('code.png', 'wb') as f:
            f.write(img)

        time.sleep(5)
        print('开始识别验证码...')
        result = upload()
        print(f'验证码为：{result}...')
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

        # 打印第3-1页 验证使用， 成功后可不用
        # with open('us_html/0-3_1.html', 'wb') as f:
        #     f.write(res.content)

        # 第四个请求（设置密保） ======================================================================================-
        url = 'https://ceac.state.gov/GenNIV/Common/ConfirmApplicationID.aspx?node=SecureQuestion'
        res = self.req.get(url)
        self.all_url[f'question'] = url
        # 打印第3-2页 验证使用， 成功后可不用
        # with open('us_html/0-3_2.html', 'wb') as f:
        #     f.write(res.content)
        reg = r'<span id="ctl00_SiteContentPlaceHolder_lblBarcode" class="barcode-large">(.*?)</span>'
        self.TXTCODETEXTBOX = re.findall(reg, res.text)[0]
        print(f'标识信息： {self.TXTCODETEXTBOX} ...')

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        print(f'密保设置完成，进入信息填写页面, url: {res.url} ...')
        # 打印第4页 验证使用， 成功后可不用
        # with open('us_html/1-1.html', 'wb') as f:
        #     f.write(res.content)
        # 初始验证请求完成（开始填写信息） ============================================================================-

        return res

    def per_info(self, res):

        self.all_url['personal_1'] = res.url

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        print(f'填写个人信息表（1）完成， {ud[2]}, 进入下一页 url: {res.url} ...')
        self.all_url[f'persional_2'] = res.url
        with open('veri.json', 'a')as f:
            f.write(',\n')
            json.dump([self.TXTCODETEXTBOX, ud[0][:5], ud[7], 'qwer'], f)
        # 打印第个人信息（1）页 验证使用， 成功后可不用
        # with open('us_html/1-2.html', 'wb') as f:
        #     f.write(res.content)

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]
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
        print(f'填写个人信息表（2）完成， {ud[2]}, 进入下一页 url: {res.url} ...')
        self.all_url[f'addr_phone'] = res.url
        # 打印第个人信息（2）页 验证使用， 成功后可不用
        # with open('us_html/2.html', 'wb') as f:
        #     f.write(res.content)

        return res

    def addr_phone(self, res):
        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        print(f'填写 地址-电话页 完成, 进入下一页 url: {res.url} ...')
        self.all_url[f'passport'] = res.url
        # 打印第个人信息（2）页 验证使用， 成功后可不用
        # with open('us_html/4 .html', 'wb') as f:
        #     f.write(res.content)
        return res

    def passport(self, res):
        up = self.us_data[2]
        # print(f'{up} ...')
        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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

        print(f'填写 护照页 完成, 进入下一页 url: {res.url} ...')
        self.all_url[f'Travel'] = res.url
        # 打印第个人信息（2）页 验证使用， 成功后可不用
        # with open('us_html/3.html', 'wb') as f:
        #     f.write(res.content)
        return res

    def travel(self, res):
        no = -5
        while no < 0:
            up = self.us_data[3]
            # print(f'{up} ...')

            # 数据传输之  __VIEWSTATE
            reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
            viewstate = re.findall(reg, res.text)[0]

            reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
            previouspage = re.findall(reg, res.text)[0]

            reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
            viewstategenerator = re.findall(reg, res.text)[0]
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
        print(f'填写 旅行计划页 完成, 进入下一页 url: {res.url} ...')
        # self.all_url[f'Travel Companions'] = res.url
        # 打印第个人信息（2）页 验证使用， 成功后可不用
        # with open('us_html/4.html', 'wb') as f:
        #     f.write(res.content)

        self.all_url[f'Travel Companions'] = res.url

        return res

    def travel_companions(self, res):
        # up = self.us_data[4]
        # print(f'{up} ...')

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        # with open('us_html/6.html', 'wb') as f:
        #     f.write(res.content)
        print(f'填写 同行人员页 完成, 进入下一页 url: {res.url} ...')
        self.all_url['PreviousUSTravel'] = res.url

        return res

    def previous_US_travel(self, res):
        # up = self.us_data[4]
        # print(f'{up} ...')

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        # with open('us_html/7.html', 'wb') as f:
        #     f.write(res.content)
        print(f'填写 以前美国之行页 完成, 进入下一页 url: {res.url} ...')
        self.all_url['USContact'] = res.url

        return res

    def us_contact(self, res):
        up = self.us_data[4]
        # print(f'{up} ...')

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        # with open('us_html/8.html', 'wb') as f:
        #     f.write(res.content)
        print(f'填写 美国友人(组织)页 完成, 进入下一页 url: {res.url} ...')
        self.all_url['Relatives'] = res.url

        return res

    def relatives(self, res):
        no = -5
        while no < 0:
            # 数据传输之  __VIEWSTATE
            reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
            viewstate = re.findall(reg, res.text)[0]

            reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
            previouspage = re.findall(reg, res.text)[0]

            reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
            viewstategenerator = re.findall(reg, res.text)[0]

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
            # with open('us_html/8.html', 'wb') as f:
            #     f.write(res.content)
            if res.url == 'https://ceac.state.gov/GenNIV/General/complete/complete_family2.aspx?node=Spouse':
                break
        print(f'填写 美国亲属页1 完成, 进入下一页 url: {res.url} ...')
        self.all_url['Spouse'] = res.url

        return res

    def spouse(self, res):
        up = self.us_data[5]
        # print(f'{up} ...')

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        # with open('us_html/8.html', 'wb') as f:
        #     f.write(res.content)
        print(f'填写 配偶信息页 完成, 进入下一页 url: {res.url} ...')
        self.all_url['WorkEducation1'] = res.url

        return res

    def work_education_1(self, res):
        up = self.us_data[6]
        # print(f'{up} ...')

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        # with open('us_html/8.html', 'wb') as f:
        #     f.write(res.content)
        print(f'填写 现在的工作页 完成, 进入下一页 url: {res.url} ...')
        self.all_url['WorkEducation2'] = res.url

        return res

    def work_education_2(self, res):
        up = self.us_data[7]
        # print(f'{up} ...')

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__PREVIOUSPAGE" id="__PREVIOUSPAGE" value="(.*?)" />'
        previouspage = re.findall(reg, res.text)[0]

        reg = r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />'
        viewstategenerator = re.findall(reg, res.text)[0]

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
        # with open('us_html/8.html', 'wb') as f:
        #     f.write(res.content)
        print(f'填写 以前的工作页 完成, 进入下一页 url: {res.url} ...')
        self.all_url['WorkEducation3'] = res.url

        return res

    def judge_res(self, func, res):
        if not res:
            print('页面获取错误, 返回出错函数名')
            return (func.__name__, )    # 出错函数之后的函数名
        elif res is tuple:
            return res
        return func(res)

    @property
    def run(self):
        res = self.choice_chn
        func_list = [
            self.per_info,
            self.addr_phone,
            self.passport,
            self.travel,
            self.travel_companions,
            self.previous_US_travel,
            self.us_contact,
            self.relatives,
            self.spouse,
            self.work_education_1,
            self.work_education_2
        ]
        for func in func_list:
            res = self.judge_res(func, res)


if __name__ == "__main__":
    u = UsVisa()
    u.run

    with open('all_url.json', 'w') as f:
        json.dump(u.all_url, f)
    print()
    for i in u.all_url:
        print(f'{i}\n  {u.all_url[i]} ...')
    # res = requests.get('https://ceac.state.gov/GenNIV/Help/Help.aspx', headers={
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
    #     'Cookie': 'ASP.NET_SessionId=csvhdq2p13ldtploll0rsuy5; _ga=GA1.3.622592070.1531215428; _gid=GA1.3.1940485068.1531215428; __utma=27961390.622592070.1531215428.1531215428.1531215428.1; __utmc=27961390; __utmz=27961390.1531215428.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; isDirty=1; __utmb=27961390.6.10.1531215428; _gat_GSA_ENOR0=1; ExpiredSession=True; PageRefresh=False'
    #     })
    # with open('fy.html', 'wb') as f:
    #     f.write(res.content)
