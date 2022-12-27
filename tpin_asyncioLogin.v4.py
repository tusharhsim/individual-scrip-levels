#importing libraries
from aiohttp import ClientSession
import pandas as pd
import asyncio
import json
import csv


#user login input
login_data = {}
with open('loginData.csv', newline='') as uData:
    reader = csv.reader(uData)
    next(reader)
    for row in reader:
        login_data[row[0].strip()] = {'pwd' : row[1].strip(), 'pin' : row[2].strip(),
                                      'email' : row[3].strip(), 'e_pwd' : row[4].strip(),
                                      'tpin' : row[5].strip()}


#asyncio login requests
enctokens = {}
failed_logins = {}

async def login(session, uid, pwd, pin, email, e_pwd, tpin):
    try:        
        sOne= await session.post(url='https://kite.zerodha.com/api/login',
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 data='user_id=%s&password=%s' %(uid, pwd))
        rId= (await sOne.json())['data']['request_id']
        try:
            sTwo= await session.post(url='https://kite.zerodha.com/api/twofa',
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     data='user_id=%s&request_id=%s&twofa_value=%s' %(uid, rId, pin))

            enctoken = sTwo.cookies['enctoken'].value
            enctokens[enctoken] = {'email' : email, 'e_pwd' : e_pwd,
                                   'tpin' : tpin, 'uid' : uid}
        except Exception as e:
            failed_logins[uid] = f'incorrect pin - {e}'
    except Exception as e:
        failed_logins[uid] = f'incorrect pwd - {e}'

async def request():
    tasks = []
    try:
        async with ClientSession() as session:
            for uid in login_data:
                task = asyncio.create_task(login(session, uid, login_data[uid]['pwd'], login_data[uid]['pin'], login_data[uid]['email'], login_data[uid]['e_pwd'], login_data[uid]['tpin']))
                tasks.append(task)
            await asyncio.gather(*tasks)
    except Exception as e:
        print(f'exception {e}')

asyncio.run(request())

if len(enctokens) > 0:
    df = pd.DataFrame({'enctoken' : enctokens.keys(),
                       'email' : [i['email'] for i in enctokens.values()],
                       'e_pwd' : [i['e_pwd'] for i in enctokens.values()],
                       'tpin' : [i['tpin'] for i in enctokens.values()],
                       'uid' : [i['uid'] for i in enctokens.values()]})
    df = df.sort_values(by=['uid'])
    df.to_csv('data.csv', sep=',', encoding='utf-8', index= False)
    print('successful enctoken logins saved in data.csv')
    print(df)

if len(failed_logins)>0:
    print('\ncouldnt login for:')
    for i in failed_logins:
        print('\t%s --\t%s' %(i, failed_logins[i]))
