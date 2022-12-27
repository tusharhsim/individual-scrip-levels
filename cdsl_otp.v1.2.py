from bs4 import BeautifulSoup
import requests
import asyncio
import imaplib
import email
import time
import csv
import re


#enctoken input
user = dict()
def userData():
        try:
                with open('data.csv', newline='') as uData:
                        reader = csv.reader(uData)
                        try:
                                next(reader)
                                for row in reader:
                                        user[row[0]] = [row[1], row[2], row[3]]
                        except Exception as e:
                                print('error in fetching enctokens -- %s' %e)
        except Exception as e:
                print('error in reading data.csv -- %s' %e)
userData()
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
boom = []
async def main(key, value):
        try:
                headers_0 = {'Authorization': f'enctoken {key}',}
                response_0 = requests.post('https://kite.zerodha.com/oms/portfolio/holdings/authorise', headers=headers_0)
                print('\n', response_0)
                boom.append(response_0.text)
                crypt_key = response_0.json()['data']['request_id']


                response_1 = requests.get('https://kite.zerodha.com/api/portfolio/authorise/holdings/kitefront/%s' %(crypt_key))
                print(response_1)
                boom.append(response_1.text)
                isin=[]
                qty=[]
                sym=[]
                for i in response_1.json()['data']['instruments']:
                        isin.append(i['isin'])
                        qty.append(str(i['quantity']))
                        sym.append(i['tradingsymbol'])


                data_2 = 'isin='+'&isin='.join(isin)+'&quantity='+'&quantity='.join(qty)+'&tradingsymbol='+'&tradingsymbol='.join(sym)
                response_2 = requests.post('https://kite.zerodha.com/api/portfolio/authorise/holdings/kitefront/%s' %(crypt_key), headers=headers, data=data_2)
                print(response_2)
                boom.append(response_2.text)
                version = response_2.json()['data']['version']
                payload = response_2.json()['data']['payload']
                dp_id = response_2.json()['data']['dp_id']
                dp_request_id = response_2.json()['data']['dp_request_id']


                response_3 = requests.post('https://edis.cdslindia.com/eDIS/VerifyDIS', headers=headers,
                                           data={'Version':version,'DPId':dp_id,'ReqId':dp_request_id,'TransDtls':payload})
                print(response_3)
                boom.append(response_3.text)
                UniqueTransactionID = BeautifulSoup(response_3.text, features="html.parser").find_all("input", type="hidden")[0].get('value')


                data_4 = f'userPin={value[2]}&UniqueTransactionID={UniqueTransactionID}'
                response_4 = requests.post('https://edis.cdslindia.com/EDIS/VerifyPin', headers=headers, data=data_4)
                print(response_4)
                boom.append(response_4.text)
                OTPTXNID = BeautifulSoup(response_4.text, features="html.parser").find_all("input", type="hidden")[0].get('value')


                gmail_host= 'imap.gmail.com'
                await asyncio.sleep(51)
                try:
                        mail = imaplib.IMAP4_SSL(gmail_host)
                        mail.login(value[0], value[1])
                        mail.select("INBOX")

                        _, selected_mails = mail.search(None, '(FROM "edis@cdslindia.co.in")')

                        email_code = selected_mails[0].split()[-1]
                        _, data = mail.fetch(email_code, 'RFC822')
                        _, bytes_data = data[0]

                        email_message = email.message_from_bytes(bytes_data)
                        if 'Transaction OTP' in email_message["subject"]:
                            for part in email_message.walk():
                                otp = re.findall(r'\d+', part.get_payload())[21]
                except Exception as e:
                        print(e)


                data_5 = f'OTP={otp}&OTPTXNID={OTPTXNID}&UniqueTransactionID={UniqueTransactionID}'
                response_5 = requests.post('https://edis.cdslindia.com/EDIS/VerifyOTP', headers=headers, data=data_5)
                print(response_5)
                boom.append(response_5.text)
                url = BeautifulSoup(response_5.text, features="html.parser").find_all("form")[0].get('action')
                ReqType = BeautifulSoup(response_5.text, features="html.parser").find_all("input")[1].get('value')
                transDtls = BeautifulSoup(response_5.text, features="html.parser").find_all("input")[2].get('value')


                response_6 = requests.post(url, headers=headers,
                                           data={'ReqId':dp_request_id,'ReqType':ReqType,'transDtls':transDtls})
                print(response_6)
                boom.append(response_6.text)
                print('otp authentication done for - ', value[0])
        except Exception as e:
                print(e)
                print('otp authentication failed for - ', value[0])

for key, value in user.items():
        asyncio.run(main(key, value))
