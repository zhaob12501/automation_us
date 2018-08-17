# 美国签证系统的数据属性(value)

## 可不选选项的项目

名称 | value
:--: | :--:
美国社会安全号 (9位纯数字) | social_security_number
美国纳税人身份号码 (纯数字) | taxpayer_number
邮政区域/邮政编码 | 所有
备用电话号码 | tel
工作电话号码 | company_phone
护照本编号 | passport_papers_number
护照/旅行证件号码(是否遗失或被盗中) |  
美国签证号码 | old_visa_number 
在美国的联系人或组织 (二者选其一) | (associate_is, associate_tuxedo_is) 
电子邮件地址(同行页, 旅行页付款选择 other 时) | (我们库里还没有)
父亲的全名与出生日期 |  
母亲的全名与出生日期 |  
月收入（如有工作，当地货币） | month_income 
主管姓名(姓, 名 分开, 两个字段) | (我们库里还没有) 
机构名称 (以前的工作页: 中学以上机构学习) | (我们库里还没有)  

## 可添加多个的项目

1. 您是否曾经用过其它名字? (例如：婚前用名、宗教用名、职业用名、别名等)
1. 除了您上面填写的国籍外,您还拥有或曾拥有其它国籍吗?
1. 按上面所示的您的原籍国/地区（国籍），您现在是其它一个国家/地区的永久居民吗？
1. 赴美访问目的
1. 是否有人与您同行？(同行人员可填多个, 组织/团队没有多选)
1. 您是否曾经在美国停留过？(多选 日期/停留时间)
1. 您是否持有或者曾经持有美国驾照？(驾照号码/所属州)
1. 除父母以外，您在美国是否还有其他直系亲属?
1. 您之前有工作吗？
1. 您是否在任何相当于中学水平或以上的教育机构里学习过？
1. 请列出您所说语言的种类
1. 最近五年里您是否去过其他国家？
1. 您是否从属于任何一个专业的、社会或慈善组织？并为其做过贡献、或为其工作过？
1. 您是否曾经在军队服役？

```go
格式:
问题/选项/下拉框提示    (英文)
问题/选项/下拉框提示    (中文)
______________________________
| 提示(中) | 提示(英) | value值|
| 提示(中) | 提示(英) | value值|
|_________|__________|________|
value 大小写区分
除统计之外的单选都为 : Y/N
```
---

### 
提示(中) | 提示(英) | value
:---: | :---: | :---:
中国北京 | CHINA, BEIJING | BEJ
中国上海 | CHINA, SHENYANG | SNY


### Personal (个人的)

**1**   `单选`
Sex
性别

提示(中) | 提示(英) | value
:---: | :---: | :---:
男 | Male | M
女| Female | F

**2**   `下拉框`
Marital Status
婚姻状况

提示(中) | 提示(英) | value
:---: | :---: | :---:
请选择 | -Select One- |
已婚 | MARRIED | M
普通法律婚姻 | COMMON LAW MARRIAGE | C
民事婚姻/国内同居 | CIVIL UNION/DOMESTIC PARTNERSHIP | P
单身 | SINGLE | S
丧偶 | WIDOWED | W
离异 | DIVORCED | D
合法分居 | LEGALLY SEPARATED | L
其他 | OTHER | O

### Travel Information (旅行信息)

**1**   `下拉框`
Purpose of Trip to the U.S.
赴美访问目的

提示(中) | 提示(英) | value
:---: | :---: | :---:
请选择签证种类 | PLEASE SELECT A VISA CLASS | -
外国政府官员(A) | FOREIGN GOVERNMENT OFFICIAL (A) | A
临时商务及旅游（B） | TEMP. BUSINESS PLEASURE VISIT (B) | B
过境的外国公民（C） | ALIEN IN TRANSIT (C) | C
北马里亚纳工作者或投资者（CW/E2C） | CNMI WORKER OR INVESTOR (CW/E2C) | CNMI
机船组人员（D） | CREWMEMBER (D) | D
贸易协议国贸易人员或投资者（E） | TREATY TRADER OR INVESTOR (E) | E
学术或语言学生（F） | ACADEMIC OR LANGUAGE STUDENT (F) | F
国际组织代表/雇员（G） | INTERNATIONAL ORGANIZATION REP./EMP. (G) | G
临时工作（H） | TEMPORARY WORKER (H) | H
外国媒体代表（I） | FOREIGN MEDIA REPRESENTATIVE (I) | I
交流访问者（J） | EXCHANGE VISITOR (J) | J
美国公民的未婚夫(妻)或配偶(K) | FIANCÉ(E) OR SPOUSE OF A U.S. CITIZEN (K) | K
公司内部调派人员(L) | INTRACOMPANY TRANSFEREE (L) | L
职业/非学术学校的学生(M) | VOCATIONAL/NONACADEMIC STUDENT (M) | M
其它(N) | OTHER (N) | N
北大西洋公约组织雇员(NATO) | NATO STAFF (NATO) | NATO
具有特殊才能的人员(O) | ALIEN WITH EXTRAORDINARY ABILITY (O) | O
国际承认的外国人士(P) | INTERNATIONALLY RECOGNIZED ALIEN (P) | P
文化交流访问者(Q) | CULTURAL EXCHANGE VISITOR (Q) | Q
宗教人士(R) | RELIGIOUS WORKER (R) | R
提供信息者或证人(S) | INFORMANT OR WITNESS (S) | S
人口贩运受害者(T) | VICTIM OF TRAFFICKING (T) | T
北美自由贸易协议专业人员(TD/TN) | NAFTA PROFESSIONAL (TD/TN) | TD/TN
犯罪活动的受害者（U） | VICTIM OF CRIMINAL ACTIVITY (U) | U
\- | PAROLE BENEICIARY (PARCIS) | PAROLE-BEN

**2** `下拉框`
Specify
具体说明 (与 1 联动)
> 提示(中) 

所属 | 提示(中) | 提示(英) | value
:---: | :---: | :---: | :---:
| A |  | AMBASSADOR OR PUBLIC MINISTER (A1) | A1-AM
|  |  | CHILD OF AN A1 (A1) | A1-CH
|  |  | CAREER DIPLOMAT/CONSULAR OFFICER (A1) | A1-DP
|  |  | SPOUSE OF AN A1 (A1) | A1-SP
|  |  | CHILD OA AN A2 (A2) | A2-CH
|  |  | FOREIGN OFFICIAL/EMPLOYEE (A2) | A2-EM
|  |  | SPOUSE OF AN A2 (A2) | A2-SP
|  |  | CHILD OF AN A3 (A3) | A3-CH
|  |  | PERSONAL EMP. OF AN A1 OR A2 (A3) | A3-EM
|  |  | SPOUSE OF AN A3 (A3) | A3-SP
----------|----------|----------|----------|----------
| B |  | BUSINESS & TOURISM (TEMPORARY VISITOR) (B1/B2) | B1-B2
|  |  | BUSINESS/CONFERENCE (B1) | B1-CF
|  |  | TOURISM/MEDICAL TREATMENT (B2) | B2-TM
----------|----------|----------|----------|----------
| C |  | CREWMEMBER IN TRANSIT (C1/D) | C1-D
|  |  | TRANSIT (C1) | C1-TR
|  |  | TRANSIT TO U.N. HEADQUARTERS (C2) | C2-UN
|  |  | CHILD OF A C3 (C3) | C3-CH
|  |  | PERSONAL EMP. OF A C3 (C3) | C3-EM
|  |  | FOREIGN OFFICIAL IN TRANSIT (C3) | C3-FR
|  |  | SPOUSE OF A C3 (C3) | C3-SP
|----------|----------|----------|----------
|  |  | CNMI TEMPORARY WORKER (CW1) | CW1-CW1
|  |  | CHILD OF CW1 (CW2) | CW2-CH
|  |  | SPOUSE OF CW1 (CW2) | CW2-SP
|  |  | CNMI LONG TERM INVESTOR (E2C) | E2C-E2C
|----------|----------|----------|----------
| D |  | CREWMEMBER (D) | D-D
|----------|----------|----------|----------
| E |  | CHILD OF AN E1 (E1) | E1-CH
|  |  | EXECUTIVE/MGR/ESSENTIAL EMP (E1) | E1-EX
|  |  | SPOUSE OF AN E1 (E1) | E1-SP
|  |  | TREATY TRADER (E1) | E1-TR
|  |  | CHILD OF AN E2 (E2) | E2-CH
|  |  | EXECUTIVE/MGR/ESSENTIAL EMP (E2) | E2-EX
|  |  | SPOUSE OF AN E2 (E2) | E2-SP
|  |  | TREATY INVESTOR (E2) | E2-TR
|  |  | CHILD OF AN E3 (E3D) | E3D-CH
|  |  | SPOUSE OF AN E3 (E3D) | E3D-SP
|----------|----------|----------|----------
| F |  | STUDENT (F1) | F1-F1
|  |  | CHILD OF AN F1 (F2) | F2-CH
|  |  | SPOUSE OF AN F1 (F2) | F2-SP
|----------|----------|----------|----------
| G |  | CHILD OF A G1 (G1) | G1-CH
|  |  | PRINCIPAL REPRESENTATIVE (G1) | G1-G1
|  |  | SPOUSE OF A G1 (G1) | G1-SP
|  |  | STAFF OF PRINCIPAL REPRESENTATIVE (G1) | G1-ST
|  |  | CHILD OF A G2 (G2) | G2-CH
|  |  | REPRESENTATIVE (G2) | G2-RP
|  |  | SPOUSE OF A G2 (G2) | G2-SP
|  |  | CHILD OF A G3 (G3) | G3-CH
|  |  | NON-RECOGNIZED/-MEMBER COUNTRY REP(G3) | G3-RP
|  |  | SPOUSE OF A G3 (G3) | G3-SP
|  |  | CHILD OF AN G4 (G4) | G4-CH
|  |  | INTERNATIONAL ORG. EMPLOYEE (G4) | G4-G4
|  |  | SPOUSE OF A G4 (G4) | G4-SP
|  |  | CHILD OF A G5 (G5) | G5-CH
|  |  | PERSONAL EMP. OF A G1, 2, 3, OR 4 (G5) | G5-EM
|  |  | SPOUSE OF A G5 (G5) | G5-SP
|----------|----------|----------|----------|-
| H |  | H1B-H1B SPECIALTY OCCUPATION (H1B)
|  |  | CHILEAN SPEC. OCCUPATION (H1B1) | H1B1-CHL
|  |  | SINGAPOREAN SPEC. OCCUPATION (H1B1) | H1B1-SGP
|  |  | NURSE IN SHORTAGE AREA (H1C) | H1C-NR
|  |  | AGRICULTURAL WORKER (H2A) H2A-AG
|  |  | NONAGRICULTURAL WORKER (H2B) | H2B-NA
|  |  | TRAINEE (H3) | H3-TR
|  |  | CHILD OF AN H (H4) | H4-CH
|  |  | SPOUSE OF AN H (H4) | H4-SP
|----------|----------|----------|----------
| I |  | CHILD OF AN I (I) | I-CH
|  |  | FOREIGN MEDIA REPRESENTATIVE (I) | I-FR
|  |  | SPOUSE OF AN I (I) | I-SP
|----------|----------|----------|----------
| J |  | EXCHANGE VISITOR (J1) | J1-J1
|  |  | CHILD OF A J1 (J2) | J2-CH
|  |  | SPOUSE OF A J1 (J2) | J2-SP
|----------|----------|----------|----------
| K |  | FIANCÉ(E) OF A U.S. CITIZEN (K1) | K1-K1
|  |  | CHILD OF A K1 (K2) | K2-K2
|  |  | SPOUSE OF A U.S. CITIZEN (K3) | K3-K3
|  |  | CHILD OF A K3 (K4) | K4-K4
|----------|----------|----------|----------
| L |  | INTRACOMPANY TRANSFEREE (L1) | L1-L1
|  |  | CHILD OF A L1 (L2) | L2-CH
|  |  | SPOUSE OF A L1 (L2) | L2-SP
|----------|----------|----------|----------
| M |  | STUDENT (M1) | M1-M1
|  |  | CHILD OF M1 (M2) | M2-CH
|  |  | SPOUSE OF M1 (M2) | M2-SP
|  |  | COMMUTER STUDENT (M3) | M3-M3
|----------|----------|----------|----------
| N |  | CHILD OF A N8 (N9) | N8-CH
|  |  | PARENT OF CERTAIN SPECIAL IMMIGRANT (N8) | N8-N8
|----------|----------|----------|----------
| NATO |  | CHILD OF NATO 1 (NATO1) | NATO1-CH
|  |  | PRINCIPAL REPRESENTATIVE (NATO1) | NATO1-PR
|  |  | SPOUSE OF NATO1 (NATO1) | NATO1-SP
|  |  | CHILD OF NATO2 (NATO2) | NATO2-CH
|  |  | REPRESENTATIVE (NATO2) | NATO2-RP
|  |  | SPOUSE OF NATO2 (NATO2) | NATO2-SP
|  |  | CHILD OF NATO3 (NATO3) | NATO3-CH
|  |  | SPOUSE OF NATO3 (NATO3) | NATO3-SP
|  |  | CLERICAL STAFF (NATO3) | NATO3-ST
|  |  | CHILD OF NATO4 (NATO4) | NATO4-CH
|  |  | OFFICIAL (NATO4) | NATO4-OF
|  |  | SPOUSE OF NATO4 (NATO4) | NATO4-SP
|  |  | CHILD OF NATO5 (NATO5) | NATO5-CH
|  |  | EXPERT (NATO5) | NATO5-EX
|  |  | SPOUSE OF NATO5 (NATO5) | NATO5-SP
|  |  | CHILD OF NATO6 (NATO6) | NATO6-CH
|  |  | SPOUSE OF NATO6 (NATO6) | NATO6-SP
|  |  | CIVILIAN STAFF (NATO6) | NATO6-ST
|  |  | CHILD OF NATO7 (NATO7) | NATO7-CH
|  |  | PERSONAL EMP. OF NATO1-NATO6 (NATO7) | NATO7-EM
|  |  | SPOUSE OF NATO7 (NATO7) | NATO7-SP
|----------|----------|----------|----------
| O |  | EXTRAORDINARY ABILITY (O1) | O1-EX
|  |  | ALIEN ACCOMPANYING/ASSISTING (O2) | O2-AL
|  |  | CHILD OF O1 OR O2 (O3) | O3-CH
|  |  | SPOUSE OF O1 OR O2 (O3) | O3-SP
|----------|----------|----------|----------
| P |  | INTERNATIONALLY RECOGNIZED ALIEN (P1) | P1-P1
|  |  | ARTIST/ENTERTAINER EXCHANGE PROG. (P2) | P2-P2
|  |  | ARTIST/ENTERTAINER IN CULTURAL PROG. (P3) | P3-P3
|  |  | CHILD OF P1, P2 OR P3 (P4) | P4-CH
|  |  | SPOUSE OF P1, P2 OR P3 (P4) | P4-SP
|----------|----------|----------|----------
| Q |  | CULTURAL EXCHANGE VISITOR (Q1) | Q1-Q1
|----------|----------|----------|----------
| R |  | RELIGIOUS WORKER (R1) | R1-R1
|  |  | CHILD OF R1 (R2) | R2-CH
|  |  | SPOUSE OF R1 (R2) | R2-SP
|----------|----------|----------|----------
| S |  | FAMILY MEMBER OF AN INFORMANT (S7) | S7-S7
|----------|----------|----------|----------
| T |  | VICTIM OF TRAFFICKING (T1) | T1-T1
|  |  | SPOUSE OF T1 (T2) | T2-SP
|  |  | CHILD OF T1 (T3) | T3-CH
|  |  | PARENT OF T1 (T4) | T4-PR
|  |  | SIBLING OF T1 (T5) | T5-SB
|  |  | ADULT/MINOR CHILD OF A DERIV BEN OF A T1 (T6) | T6-CB
|----------|----------|----------|----------
| TD/TN |  | CHILD OF TN (TD) | TD-CH
|  |  | SPOUSE OF TN (TD) | TD-SP
|----------|----------|----------|----------
| U |  | VICTIM OF CRIME (U1) | U1-U1
|  |  | SPOUSE OF U1 (U2) | U2-SP
|  |  | CHILD OF U1 (U3) | U3-CH
|  |  | PARENT OF U1 (U4) | U4-PR
|  |  | SIBLING OF U1 (U5) | U5-SB
|----------|----------|----------|----------
| PAROLE-BEN |  | PARCIS (USCIS APPROVED PAROLE) | PRL-PARCIS

**3** `下拉框`
state
州

提示(中) | 提示(英) | value
:---: | :---: | :---:
\- 选择一个 - | - Select one - | 
阿拉巴马州 | ALABAMA | AL
阿拉斯加州 | ALASKA | AK
美国萨摩亚 | AMERICAN SAMOA | AS
亚利桑那 | ARIZONA | AZ
阿肯色州 | ARKANSAS | AR
CALIFORNIA | CALIFORNIA | CA
COLORADO | COLORADO | CO
康涅狄格 | CONNECTICUT | CT
特拉华州 | DELAWARE | DE
哥伦比亚特区 | DISTRICT OF COLUMBIA | DC
佛罗里达 | FLORIDA | FL
GEORGIA | GEORGIA | GA
关岛 | GUAM | GU
夏威夷 | HAWAII | HI
爱达荷州 | IDAHO | ID
ILLINOIS | ILLINOIS | IL
印第安纳 | INDIANA | IN
IOWA | IOWA | IA
堪萨斯州 | KANSAS | KS
肯塔基州 | KENTUCKY | KY
路易斯安那州 | LOUISIANA | LA
缅因州 | MAINE | ME
马里兰 | MARYLAND | MD
马萨诸塞州 | MASSACHUSETTS | MA
MICHIGAN | MICHIGAN | MI
明尼苏达 | MINNESOTA | MN
密西西比州 | MISSISSIPPI | MS
密苏里州 | MISSOURI | MO
蒙大拿 | MONTANA | MT
内布拉斯加州 | NEBRASKA | NE
NEVADA | NEVADA | NV
新罕布什尔 | NEW HAMPSHIRE | NH
新泽西州 | NEW JERSEY | NJ
新墨西哥 | NEW MEXICO | NM
纽约 | NEW YORK | NY
北卡罗来纳 | NORTH CAROLINA | NC
北达科他州 | NORTH DAKOTA | ND
北马里亚纳群岛 | NORTHERN MARIANA ISLANDS | MP
OHIO | OHIO | OH
俄克拉何马州 | OKLAHOMA | OK
OREGON | OREGON | OR
宾夕法尼亚州 | PENNSYLVANIA | PA
PUERTO RICO | PUERTO RICO | PR
罗德岛 | RHODE ISLAND | RI
南卡罗来纳 | SOUTH CAROLINA | SC
南达科他州 | SOUTH DAKOTA | SD
田纳西州 | TENNESSEE | TN
TEXAS | TEXAS | TX
犹他州 | UTAH | UT
佛蒙特 | VERMONT | VT
维尔京群岛 | VIRGIN ISLANDS | VI
VIRGINIA | VIRGINIA | VA
本报讯 | WASHINGTON | WA
西弗吉尼亚 | WEST VIRGINIA | WV
威斯康星州 | WISCONSIN | WI
怀俄明州 | WYOMING | WY

### Passport 护照签发国家

提示(中) | 提示(英) | value
:--: | :--: | :--:
请选择 | - Select One - |  
阿富汗 | AFGHANISTAN | AFGH
阿尔巴尼亚 | ALBANIA | ALB
阿尔及利亚 | ALGERIA | ALGR
美国萨摩亚 | AMERICAN SAMOA | ASMO
安道尔 | ANDORRA | ANDO
安哥拉 | ANGOLA | ANGL
安圭拉 | ANGUILLA | ANGU
安提瓜和巴布达 | ANTIGUA AND BARBUDA | ANTI
阿根廷 | ARGENTINA | ARG
亚美尼亚 | ARMENIA | ARM
澳大利亚 | AUSTRALIA | ASTL
奥地利 | AUSTRIA | AUST
阿塞拜疆 | AZERBAIJAN | AZR
巴哈马 | BAHAMAS | BAMA
巴林 | BAHRAIN | BAHR
孟加拉国 | BANGLADESH | BANG
巴巴多斯 | BARBADOS | BRDO
白俄罗斯 | BELARUS | BYS
比利时 | BELGIUM | BELG
伯利兹 | BELIZE | BLZ
贝宁 | BENIN | BENN
百慕大 | BERMUDA | BERM
不丹 | BHUTAN | BHU
玻利维亚 | BOLIVIA | BOL
波黑 | BOSNIA-HERZEGOVINA | BIH
博茨瓦纳 | BOTSWANA | BOT
巴西 | BRAZIL | BRZL
英属印度洋领地 | BRITISH INDIAN OCEAN TERRITORY | IOT
文莱 | BRUNEI | BRNI
保加利亚 | BULGARIA | BULG
BURKINA FASO | BURKINA FASO | BURK
缅甸 | BURMA | BURM
布隆迪 | BURUNDI | BRND
柬埔寨 | CAMBODIA | CBDA
喀麦隆 | CAMEROON | CMRN
加拿大 | CANADA | CAN
CABO VERDE | CABO VERDE | CAVI
开曼群岛 | CAYMAN ISLANDS | CAYI
中非共和国 | CENTRAL AFRICAN REPUBLIC | CAFR
CHAD | CHAD | CHAD
智利 | CHILE | CHIL
中国 | CHINA | CHIN
哥伦比亚 | COLOMBIA | COL
科摩罗 | COMOROS | COMO
刚果民主共和国，刚果民主共和国 | CONGO, DEMOCRATIC REPUBLIC OF THE | COD
刚果共和国，刚果共和国 | CONGO, REPUBLIC OF THE | CONB
哥斯达黎加 | COSTA RICA | CSTR
COTE D`IVOIRE | COTE D`IVOIRE | IVCO
克罗地亚 | CROATIA | HRV
CUBA | CUBA | CUBA
塞浦路斯 | CYPRUS | CYPR
捷克共和国 | CZECH REPUBLIC | CZEC
丹麦 | DENMARK | DEN
吉布提 | DJIBOUTI | DJI
DOMINICA | DOMINICA | DOMN
多明尼加共和国 | DOMINICAN REPUBLIC | DOMR
厄瓜多尔 | ECUADOR | ECUA
埃及 | EGYPT | EGYP
萨尔瓦多 | EL SALVADOR | ELSL
赤道几内亚 | EQUATORIAL GUINEA | EGN
厄立特里亚 | ERITREA | ERI
爱沙尼亚 | ESTONIA | EST
ESWATINI | ESWATINI | SZLD
埃塞俄比亚 | ETHIOPIA | ETH
欧洲联盟 | EUROPEAN UNION | XEU
FIJI | FIJI | FIJI
芬兰 | FINLAND | FIN
法国 | FRANCE | FRAN
加蓬 | GABON | GABN
GAMBIA，THE | GAMBIA, THE | GAM
GEORGIA | GEORGIA | GEO
德国 | GERMANY | GER
加纳 | GHANA | GHAN
直布罗陀 | GIBRALTAR | GIB
希腊 | GREECE | GRC
格林纳达 | GRENADA | GREN
危地马拉 | GUATEMALA | GUAT
几内亚 | GUINEA | GNEA
几内亚 - 比绍 | GUINEA - BISSAU | GUIB
圭亚那 | GUYANA | GUY
海地 | HAITI | HAT
听到和麦克唐纳群岛 | HEARD AND MCDONALD ISLANDS | HMD
HOLY SEE（梵蒂冈城） | HOLY SEE (VATICAN CITY) | VAT
洪都拉斯 | HONDURAS | HOND
香港特别行政区 | HONG KONG SAR | HNK
香港，英国总领事馆 | HONG KONG, BRITISH CONSULATE GENERAL | HOKO
匈牙利 | HUNGARY | HUNG
冰岛 | ICELAND | ICLD
印度 | INDIA | IND
印度尼西亚 | INDONESIA | IDSA
伊朗 | IRAN | IRAN
伊拉克 | IRAQ | IRAQ
爱尔兰 | IRELAND | IRE
以色列 | ISRAEL | ISRL
意大利 | ITALY | ITLY
牙买加 | JAMAICA | JAM
日本 | JAPAN | JPN
约旦 | JORDAN | JORD
哈萨克斯坦 | KAZAKHSTAN | KAZ
肯尼亚 | KENYA | KENY
基里巴斯 | KIRIBATI | KIRI
朝鲜民主主义人民共和国（北部） | KOREA, DEMOCRATIC REPUBLIC OF (NORTH) | PRK
韩国，（南部）共和国 | KOREA, REPUBLIC OF (SOUTH) | KOR
科索沃 | KOSOVO | KSV
科威特 | KUWAIT | KUWT
吉尔吉斯斯坦 | KYRGYZSTAN | KGZ
老挝 | LAOS | LAOS
拉脱维亚 | LATVIA | LATV
黎巴嫩 | LEBANON | LEBN
莱索托 | LESOTHO | LES
利比里亚 | LIBERIA | LIBR
利比亚 | LIBYA | LBYA
列支敦士登 | LIECHTENSTEIN | LCHT
立陶宛 | LITHUANIA | LITH
卢森堡 | LUXEMBOURG | LXM
澳门 | MACAU | MAC
马其顿 | MACEDONIA | MKD
马达加斯加 | MADAGASCAR | MADG
马拉维 | MALAWI | MALW
马来西亚 | MALAYSIA | MLAS
马尔代夫 | MALDIVES | MLDV
马里 | MALI | MALI
马耳他 | MALTA | MLTA
马绍尔群岛 | MARSHALL ISLANDS | RMI
马提尼克岛 | MARTINIQUE | MART
毛里塔尼亚 | MAURITANIA | MAUR
毛里求斯 | MAURITIUS | MRTS
墨西哥 | MEXICO | MEX
密克罗尼西亚 | MICRONESIA | FSM
摩尔多瓦 | MOLDOVA | MLD
MONACO | MONACO | MON
蒙古 | MONGOLIA | MONG
黑山 | MONTENEGRO | MTG
MONTSERRAT | MONTSERRAT | MONT
摩洛哥 | MOROCCO | MORO
莫桑比克 | MOZAMBIQUE | MOZ
纳米比亚 | NAMIBIA | NAMB
瑙鲁 | NAURU | NAU
尼泊尔 | NEPAL | NEP
荷兰 | NETHERLANDS | NETH
新西兰 | NEW ZEALAND | NZLD
尼加拉瓜 | NICARAGUA | NIC
尼日尔 | NIGER | NIR
尼日利亚 | NIGERIA | NRA
挪威 | NORWAY | NORW
阿曼 | OMAN | OMAN
巴基斯坦 | PAKISTAN | PKST
帛琉 | PALAU | PALA
巴勒斯坦权力机构 | PALESTINIAN AUTHORITY | PAL
巴拿马 | PANAMA | PAN
巴布亚新几内亚 | PAPUA NEW GUINEA | PNG
巴拉圭 | PARAGUAY | PARA
秘鲁 | PERU | PERU
菲律宾 | PHILIPPINES | PHIL
PITCAIRN ISLANDS | PITCAIRN ISLANDS | PITC
波兰 | POLAND | POL
葡萄牙 | PORTUGAL | PORT
卡塔尔 | QATAR | QTAR
罗马尼亚 | ROMANIA | ROM
俄国 | RUSSIA | RUS
卢旺达 | RWANDA | RWND
SAMOA | SAMOA | WSAM
圣马力诺 | SAN MARINO | SMAR
圣多美和普林西比 | SAO TOME AND PRINCIPE | STPR
沙特阿拉伯 | SAUDI ARABIA | SARB
塞内加尔 | SENEGAL | SENG
塞尔维亚 | SERBIA | SBA
塞舌尔 | SEYCHELLES | SEYC
塞拉利昂 | SIERRA LEONE | SLEO
新加坡 | SINGAPORE | SING
斯洛伐克 | SLOVAKIA | SVK
斯洛文尼亚 | SLOVENIA | SVN
索罗蒙群岛 | SOLOMON ISLANDS | SLMN
索马里 | SOMALIA | SOMA
南非 | SOUTH AFRICA | SAFR
南苏丹 | SOUTH SUDAN | SSDN
西班牙 | SPAIN | SPN
斯里兰卡 | SRI LANKA | SRL
ST。 HELENA | ST. HELENA | SHEL
ST。 KITTS和NEVIS | ST. KITTS AND NEVIS | STCN
ST。 LUCIA | ST. LUCIA | SLCA
ST。 VINCENT和GRENADINES | ST. VINCENT AND THE GRENADINES | STVN
状态中性旅行文件 | STATUS NEUTRAL TRAVEL DOCUMENT | SNTD
苏丹 | SUDAN | SUDA
苏里南 | SURINAME | SURM
瑞典 | SWEDEN | SWDN
瑞士 | SWITZERLAND | SWTZ
叙利亚 | SYRIA | SYR
台湾 | TAIWAN | TWAN
塔吉克斯坦 | TAJIKISTAN | TJK
坦桑尼亚 | TANZANIA | TAZN
泰国 | THAILAND | THAI
东帝汶 | TIMOR-LESTE | TMOR
TOGO | TOGO | TOGO
汤加 | TONGA | TONG
特立尼达和多巴哥 | TRINIDAD AND TOBAGO | TRIN
突尼斯 | TUNISIA | TNSA
火鸡 | TURKEY | TRKY
土库曼斯坦 | TURKMENISTAN | TKM
特克斯和凯科斯群岛 | TURKS AND CAICOS ISLANDS | TCIS
TUVALU | TUVALU | TUV
乌干达 | UGANDA | UGAN
乌克兰 | UKRAINE | UKR
阿拉伯联合酋长国 | UNITED ARAB EMIRATES | UAE
英国 | UNITED KINGDOM | GRBR
联合国 | UNITED NATIONS | UNLP
美国 | UNITED STATES OF AMERICA | USA
乌拉圭 | URUGUAY | URU
乌兹别克斯坦 | UZBEKISTAN | UZB
瓦努阿图 | VANUATU | VANU
委内瑞拉 | VENEZUELA | VENZ
越南 | VIETNAM | VTNM
VIRGIN ISLANDS，BRITISH | VIRGIN ISLANDS, BRITISH | BRVI
瓦利斯和富图纳群岛 | WALLIS AND FUTUNA ISLANDS | WAFT
也门 | YEMEN | YEM
赞比亚 | ZAMBIA | ZAMB
津巴布韦 | ZIMBABWE | ZIMB
