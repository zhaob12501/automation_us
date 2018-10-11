from auto_us import AllPage

a = AllPage()

a.renamePdf()



# import json 
# from selenium import webdriver 
# from time import sleep
# download_dir = r"C:\Users\Administrator\Desktop\automation\automation_us\usFile"
# appState = { 
#     "recentDestinations": [ 
#      { 
#       "id": "Save as PDF", 
#       "origin": "local" 
#      } 
#     ], 
#     "selectedDestinationId": "Save as PDF", 
#     "version": 2 
# } 
# profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState),'savefile.default_directory': download_dir}
# chrome_options = webdriver.ChromeOptions() 
# chrome_options.add_experimental_option('prefs', profile) 
# chrome_options.add_argument('--kiosk-printing') 


# driver = webdriver.Chrome(chrome_options=chrome_options) 
# driver.get('http://www.mobtop.com.cn') 
# driver.get('http://www.mobtop.com.cn/Uploads/Business/pdf/repatriation/2018-09-13/P88GR1G-1.pdf') 
# driver.execute_script('window.print();') 
# sleep(3)
# driver.quit()


