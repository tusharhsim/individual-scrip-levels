from selenium.webdriver.common.by import By
from selenium import webdriver
import winsound
import keyboard
import csv


equities = ['RELIANCE', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HDFC', 'TCS', 'KOTAKBANK', 'ITC', 'LT', 'HINDUNILVR']
symbols = {}
support = []
resistance = []

for i in equities:
        with open('%s.csv' %(i), newline='') as uData:
                reader = list(csv.reader(uData))
                symbols[i] = [[int(j) for j in reader[1]], [int(j) for j in reader[3]]]
                support += [int(j) for j in reader[1]]
                resistance += [int(j) for j in reader[3]]

driver = webdriver.Chrome()
driver.implicitly_wait(7)
driver.get('https://kite.zerodha.com/')
driver.find_element(By.ID, "userid").send_keys('CVX340')
driver.find_element(By.ID, "password").send_keys('Vishal@123')
driver.find_element(By.TAG_NAME, 'button').click()
driver.maximize_window()
driver.find_element(By.ID, 'pin').send_keys(581899)
driver.find_element(By.TAG_NAME, 'button').click()

while True:
        if keyboard.is_pressed("esc"):
                break                        

        for child in range(1, len(equities)+1):
                try:
                        ltp = int(float(driver.find_element(By.CSS_SELECTOR, 'div.vddl-draggable:nth-child(%s) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > span:nth-child(3)' %(child)).text))
                        print(ltp)
                        if ltp in support:
                                for scrip in symbols:
                                        if ltp in symbols[scrip][0] and scrip == driver.find_element(By.CSS_SELECTOR, 'div.vddl-draggable:nth-child(%s) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)' %(child)).text:
                                                print('support collision detected in -- %s @ %s' %(scrip, ltp))
                                                winsound.Beep(1024, 888)
                        if ltp in resistance:
                                for scrip in symbols:
                                        if ltp in symbols[scrip][1] and scrip == driver.find_element(By.CSS_SELECTOR, 'div.vddl-draggable:nth-child(%s) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > span:nth-child(1)' %(child)).text:
                                                print('resistance collision detected in -- %s @ %s' %(scrip, ltp))
                                                winsound.Beep(2048, 888)

                        if keyboard.is_pressed("esc"):
                                break                        

                except Exception as e:
                        print(f'failed due to -- {e}')
