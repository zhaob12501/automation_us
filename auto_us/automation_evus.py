from .autoUS import AutoUs

MONTH = {
    "01": "一月",
    "02": "二月",
    "03": "三月",
    "04": "四月",
    "05": "五月",
    "06": "六月",
    "07": "七月",
    "08": "八月",
    "09": "九月",
    "10": "十月",
    "11": "十一月",
    "12": "十二月",
}


class AutomationEvus(AutoUs):
    def __init__(self, noWin=False, noImg=False):
        super().__init__(noWin=noWin, noImg=noImg)
        self.indexUrl = "https://www.evusvisa.com/cn/application"
        
    def putInfo(self):
        ids = [
            ("last_name", "姓"),
            ("first_name", "名"),
            ("birth_date_day", f"{int('')}"),
            ("birth_date_month", MONTH[""]),
            ("birth_date_year", "年"),
            ("city_birth", "出生城市"),
            ("country_birth", "出生国家「中国」"),
            ("radio-gender-male" if "男" else "radio-gender-female", ""),
            ("national_identification_number", "身份证号"),
            ("btnNext0", ""),
            ("passport_number", "护照号码"),
            ("passport_expedition_date_day", f"{int('')}"),
            ("passport_expedition_date_month", MONTH[""]),
            ("passport_expedition_date_year", "签发时间「年」"),
            ("passport_expiration_date_day", f"{int('')}"),
            ("passport_expiration_date_month", MONTH[""]),
            ("passport_expiration_date_year", "到期时间「年」"),
            ("visa_foil_number", "美国B1/B2签证号码"),
            ("radio-q_years-1" if "您持有十年效期的美国访客签证吗（B1、B2 或 B1/B2 类）？" else "radio-q_years-0", ""),
            ("radio-passport_contains_us_visa-1" if "您的美国签证是否在您现在使用的护照上？" else "radio-passport_contains_us_visa-0", "")
        ]
        
