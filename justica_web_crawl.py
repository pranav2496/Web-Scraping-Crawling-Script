#Python program to scrape website  
#and save quotes from website 
try:
    import pandas as pd
    import numpy as np
    import requests
    import xlrd
    import deathbycaptcha
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from openpyxl import Workbook


except:
    import pip
    pip.main(['install', 'pandas', 'xlrd', 'requests', 'beautifulsoup4', 'deathbycaptcha', 'selenium'])
    import requests
    import xlrd
    import deathbycaptcha
    import pandas as pd
    import numpy as np
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from openpyxl import Workbook


import re
import csv 
import json, time
from csv import writer
from pandas import ExcelWriter
from pandas import ExcelFile
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener

URL = "https://nacionalidade.justica.gov.pt/"

def solve_recaptcha(url):
    
    #DeathByCaptcha API user credntials
    username = '*********'  #username of the deathbycaptcha API package
    password = '*****************' #password
        
    Captcha_dict = {
        'proxytype': 'HTTP',
        'googlekey': '6LeDhLIZAAAAAA0Hy0VLO7wOeB5aNIibYM-aQ2_3',
        'pageurl': url,
        'action': "example/action",
        'min_score': 0.3
        }
    
    json_Captcha = json.dumps(Captcha_dict)

    client = deathbycaptcha.HttpClient(username, password)

    try:
        balance = client.get_balance()

        captcha = client.decode(type=4,token_params=json_Captcha)
        if captcha:
            return captcha["text"]

        if '': 
            client.report(captcha["captcha"])
    except deathbycaptcha.AccessDeniedException:
        print("error: Access to DBC API denied, check your credentials and/or balance")



def data_scraping(access_code, browser):
    
    browser.execute_script("document.getElementById(\"g-recaptcha-response\").innerHTML=\"{}\"".format(solve_recaptcha(URL)))

    target = browser.find_element_by_id("SenhaAcesso")
    target.clear()
        
    target.send_keys(access_code)

    target.submit()
    time.sleep(5)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    case_no = soup.find('div', {'id' : 'bloc1'}).text
    place = soup.find('div', {'style' : 'font-weight: bold;'}).text
    name = soup.find('div', {'style' : 'color:#335779; font-size:1.3em;'}).text
    stage = soup.find('section', {'class' : 'step-indicator'})

    case_no = re.search('[\d]+[\/\s]+[\d]+', case_no).group()

    stages = []
    for i in range(1,8):
        if(str(browser.page_source).__contains__('step step'+str(i)+' active3')):
            for elem in stage.find_all('div', {'class' : 'step step'+str(i)+' active3'}):
                status = re.search('[\d]+', str(elem)).group()+"-Orange"
        elif(str(browser.page_source).__contains__('step step'+str(i)+' active2')):
            for elem in stage.find_all('div', {'class' : 'step step'+str(i)+' active2'}):
                status = re.search('[\d]+', str(elem)).group()+"-LightOrange"
        else:
            for elem in stage.find_all('div', {'class' : 'step step'+str(i)+' active1'}):
                stages.append(re.search('[\d]+', str(elem)).group()+"-Green")
                status = stages[-1:][0]
    
    
    row_contents = [name, case_no, access_code, status, place]
    append_list_as_row('JusticaOutput.csv', row_contents) #Name of the output file that is stored in the same folder where the script is kept
    
    print(case_no)       
    print(place)
    print(name) 
    print(status)
    
def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

if __name__ == '__main__':
    
    options = Options()
    browser = webdriver.Chrome(options = options)
    browser.get(URL)
    
    data = pd.read_excel (r'input & output.xlsx')  # Path for the excel sheet containing the Access codes 
    df = pd.DataFrame(data, columns= ['Acess Code'])
    for code in df.values:
        if type(code[0]) is float or code[0] == 'nan':
            pass        
        else:
            print("\n"+code[0])        
            data_scraping(code[0], browser)
            
        
            
