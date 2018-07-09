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
from settings import COUNTRY, E_NAME, E_NAME_2, NAME
from yunsu import upload


class UsVisa:
    def __init__(self):
        self.req = requests.Session()
        self.req.timeout= 20
        # self.req.proxies = {
        #     'http': self.proxy
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
        self.all_url[f'index_choice_{COUNTRY}'] = res.url
        # 打印第一页 验证使用， 成功后可不用
        # with open('us_html/0-1.html', 'wb')as f:
        #     f.write(res.content)

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]

        # 数据传输之  LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha
        reg = r'<input type="hidden" name="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" id="LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha" value="(.*?)" />'
        defaultcaptcha = re.findall(reg, res.text)[0]

        data1 = {
            '__EVENTTARGET': 'ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': '1A9ADDD8',
            '__VIEWSTATEENCRYPTED': '',
            '__PREVIOUSPAGE': 'en7Fj2xF46yV7W2v9DEWvZpWYVnYcdkIIo9kXrCQIazclNhwoKQqJIH8GdNg2WAFSeIQc9YRk9sQToe1dxYxbRq1TMwjiZ8S4VZk4rJMnj9KEqHR0',
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': 'CLEARSESSION',
            'ctl00$SiteContentPlaceHolder$ucCultures$cpeLanguages_ClientState': 'true',
            'ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation': COUNTRY,
            'ctl00$SiteContentPlaceHolder$ucLocation$IdentifyCaptcha1$txtCodeTextBox': '',
            'LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': defaultcaptcha,
            'LBD_BackWorkaround_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': '1',
        }

        # 第二个请求 ==================================================================================================-
        # 选择country  ==> CHINA BEIJING
        res = self.req.post(self.us_url, data=data1)
        print(f'请求 {COUNTRY}...')

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
        # print(f'https://ceac.state.gov{img_url}')
        img_url = f'https://ceac.state.gov{img_url}'
        # 获取验证码
        img = self.req.get(img_url).content
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
            '__VIEWSTATEGENERATOR': '1A9ADDD8',
            '__VIEWSTATEENCRYPTED': '',
            '__PREVIOUSPAGE': 'en7Fj2xF46yV7W2v9DEWvZpWYVnYcdkIIo9kXrCQIazclNhwoKQqJIH8GdNg2WAFSeIQc9YRk9sQToe1dxYxbRq1TMwjiZ8S4VZk4rJMnj9KEqHR0',
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': 'CLEARSESSION',
            'ctl00$SiteContentPlaceHolder$ucCultures$cpeLanguages_ClientState': 'true',
            'ctl00$SiteContentPlaceHolder$ucLocation$ddlLocation': COUNTRY,
            'ctl00$SiteContentPlaceHolder$ucLocation$IdentifyCaptcha1$txtCodeTextBox': result,
            'LBD_VCID_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': defaultcaptcha,
            'LBD_BackWorkaround_c_default_ctl00_sitecontentplaceholder_uclocation_identifycaptcha1_defaultcaptcha': '1',
            '__ASYNCPOST': 'true'
        }

        # 第三个请求 ==================================================================================================-
        # 检测验证码，请求密保问题页
        res = self.req.post(self.us_url, data=data2)
        print(f'请求密保问题页，密保为：qwerdf ...')

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

        data3 = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': '23675DA4',
            '__PREVIOUSPAGE': 'DTNr138ui0KEFYPlFcUFR2KQG-TWOdo6Lfn_jVSlmV8NxO7pBCkoIhXv0rEoh8-rb55Vvoe0-srvBU87_8x00hwbfIx8J4sRBjOgml5Xwquz5esBrQ10REZJb1YZ6RkkrQaumQ2',
            'ctl00$ddlLanguage': 'zh-CN',
            'ctl00$HDClearSession': 'CLEARSESSION',
            'ctl00$SiteContentPlaceHolder$ddlQuestions': '1',
            'ctl00$SiteContentPlaceHolder$txtAnswer': 'qwerdf',
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

        ud = self.us_data[0]
        data1 = {
            '__PREVIOUSPAGE': 'AUEWs1jo1JKhR2ofhtDaf9E_X05cCJ7dvsNTaIE-ueElqX8mdRnFPe7LvzXgIE7mJdEx-glfqkqnNXFD-vxXFnUNGDxT7b9vl2VwmZGs4EcuGpwML4iFH8OOceZNSgu0L1CGAg2',
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
            '__VIEWSTATEGENERATOR': 'D023C631',
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '884',
        }

        # 个人信息表第一个请求 ========================================================================================-
        res = self.req.post(res.url, data=data1)
        self.pre_info_url_2 = res.url
        print(f'填写个人信息表（1）完成， {ud[2]}, 进入下一页 url: {res.url} ...')
        self.all_url[f'persional_2'] = res.url
        with open('veri.json', 'w')as f:
            json.dump([self.TXTCODETEXTBOX, ud[0][:5], ud[7], 'qwerdf'], f)
        # 打印第个人信息（1）页 验证使用， 成功后可不用
        # with open('us_html/1-2.html', 'wb') as f:
        #     f.write(res.content)

        # 数据传输之  __VIEWSTATE
        reg = r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />'
        viewstate = re.findall(reg, res.text)[0]
        data2 = {
            '__PREVIOUSPAGE': 'xGJzyAYJeKuXlDm-DmW3Kvh0uC--fYiIxO4TCGx9OJFlThJ1IaPoizB5EcauOEp1kfYeIeDbbjGVVueK9aRdzUIc7CUrUeUuXZ32QNN9gq4dQrqZ1uScoQtWhkG3XGlEyF-6XFE_ITAnUN2HhTZRAssaAzA1',
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

        uap = self.us_data[1]
        data1 = {
            '__PREVIOUSPAGE': 'bGyyWfEiRRzzGhrXuvigxR767UffiAKJfPuFfSsOmqCD0ciTmVQzArJVBdmcbT1LJPg6uvbkrd76KPBTGhpmK0RUE7yiCyt5DNbXGDaXWqlSbWB33Cj21bYi1eiE-3eBvdlinA2',
            'ctl00$ddlLanguage': 'en-US',
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
            '__VIEWSTATEGENERATOR': '911E02B7',
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

        data = {
            '__PREVIOUSPAGE': 'V9cN-b6-8fPdL6msFuStv8VS6wU0WKow-h-DPzSjJ63cHVDH9Fm8dfDqfhFD5eizB0o_U4REccjDTBizl_nQn97T8J4DGhEJfYvD7q3zxbRu3cdUajsOjcOHQllRo8igUvrOzmy-4omvd4Xh7Mmy3fLp-ew1',
            'ctl00$ddlLanguage': 'en-US',
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
            '__VIEWSTATEGENERATOR': 'D4BE0AC9',
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


if __name__ == "__main__":
    u = UsVisa()
    res = u.choice_chn
    res = u.per_info(res)
    res = u.addr_phone(res)
    res = u.passport(res)
    with open('all_url.json', 'w') as f:
        json.dump(u.all_url, f)
    for i in u.all_url:
        print(f'{i}\n  {u.all_url[i]} ...')
