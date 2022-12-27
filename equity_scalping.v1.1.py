#importing libraries
from aiohttp import ClientSession
import asyncio

from datetime import datetime
import logging

import json
import csv

import keyboard

print('N\nscalping beast welcomes you')
print('press ESC to exit the core loop\n')


#logger's defination
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)


#functions' definition


#order management
order_ledger = {}

async def order(session, enctoken, symbol, tType, quantity):
        resp= await session.post(url='https://kite.zerodha.com/oms/orders/regular',
                                 headers={'Authorization': 'enctoken %s' %(enctoken),'Content-Type': 'application/x-www-form-urlencoded'},
                                 data='exchange=NSE&tradingsymbol=%s&transaction_type=%s&order_type=MARKET&quantity=%s&product=CNC' %(symbol, tType, quantity))
        logger.info(await resp.text())

async def limit_order(session, enctoken, symbol, tType, quantity, price):
        resp= await session.post(url='https://kite.zerodha.com/oms/orders/regular',
                                 headers={'Authorization': 'enctoken %s' %(enctoken),'Content-Type': 'application/x-www-form-urlencoded'},
                                 data='exchange=NSE&tradingsymbol=%s&transaction_type=%s&order_type=LIMIT&quantity=%s&price=%s&product=CNC' %(symbol, tType, quantity, price))
        logger.info(await resp.text())
        try:
                order_ledger[enctoken] = (await resp.json())['data']['order_id']
        except:
                order_ledger[enctoken] = None

async def limit_order_modification(session, enctoken, ids, price):
                resp= await session.put(url='https://kite.zerodha.com/oms/orders/regular/%s' %(ids),
                                headers={'Authorization': 'enctoken %s' %(enctoken),'Content-Type': 'application/x-www-form-urlencoded'},
                                data='price=%s' %(price))
                logger.info(await resp.text())

async def cancel_orders(session, enctoken, ids):
                details= await session.delete(url='https://kite.zerodha.com/oms/orders/regular/%s' %(ids), headers={'Authorization': 'enctoken %s' %(enctoken)}, ssl=False)
                logger.info(await details.text())

async def limit_order_placement(session, symbol, tType, limit_price):
                await asyncio.gather(*[limit_order(session, i, symbol, tType, j, limit_price) for i,j in token_data.items()], return_exceptions=True)
                print(f'press shift + U to update limit price, shift + X to cancel all open orders for {symbol}')
                while True:
                        if keyboard.is_pressed("shift+U"):
                                limit_price = float(''.join(i for i in input(f'new price  for {symbol}\t') if i.isdigit() or i in '.') or False)
                                if limit_price:
                                        await asyncio.gather(*[limit_order_modification(session, i, j, limit_price) for i,j in order_ledger.items()], return_exceptions=True)
                                else:
                                        pass
                                print(f'updated, shift + X to cancel open orders for {symbol}')
                        if keyboard.is_pressed("shift+X"):
                                print(f'cancelling open orders for {symbol}')
                                await asyncio.gather(*[cancel_orders(session, x, y) for(x,y) in order_ledger.items()], return_exceptions=True)
                                order_ledger.clear()
                                print(f'all open orders cancelled for {symbol}\n you can continue trading!\n')
                                break

#order placement

class Manual:
        async def BUY():
                try:
                        async with ClientSession() as session:
                                #symbol = 'HDFC'
                                symbol = ''
                                while len(symbol) == 0:
                                        symbol = input('input the scrip to buy\t\t').upper().strip()
                                print(f'buying - {symbol}')
                                limit_price = float(''.join(i for i in input('limit price\t') if i.isdigit() or i in '.') or False)
                                if limit_price:
                                        await limit_order_placement(session, symbol, 'BUY', limit_price)
                                else:
                                        await asyncio.gather(*[order(session, i, symbol, 'BUY', j) for i,j in token_data.items()], return_exceptions=True)
                                        print('bought at market price')
                except Exception as e:
                        logger.error('buying unsuccessful -- %s\n' %e)
        async def SELL():
                try:
                        async with ClientSession() as session:
                                #symbol = 'HDFC'
                                symbol = ''
                                while len(symbol) == 0:
                                        symbol = input('input the scrip to sell\t\t').upper().strip()
                                print(f'selling - {symbol}')
                                limit_price = float(''.join(i for i in input('limit price\t') if i.isdigit() or i in '.') or False)
                                if limit_price:
                                        await limit_order_placement(session, symbol, 'SELL', limit_price)
                                else:
                                        await asyncio.gather(*[order(session, i, symbol, 'SELL', j) for i,j in token_data.items()], return_exceptions=True)
                                        print('sold at market price')
                except Exception as e:
                        logger.critical('selling unsuccessful -- %s\n' %e)

#data input
token_data={}
def user_data():
        try:
                with open('holdings_data.csv', newline='') as uData:
                        reader = csv.reader(uData)
                        try:
                                token_data.clear()
                                next(reader)
                                for row in reader:
                                        token_data[row[0]]=int(row[1])
                        except Exception as e:
                                logger.error('error in fetching enctokens -- %s\n' %e)
        except Exception as e:
                logger.critical('error in reading data.csv -- %s\n' %e)
user_data()

print(' quantity\tenctoken')
for i,j in token_data.items():
                print(' %s\t\t%s' %(j, i))

input('\npress enter to trade\t')

#manualTrades
logger.info('make what you can\n')

while True:
        try:
                if keyboard.is_pressed("shift+b"):
                        print('\nbutton @ %s' %datetime.now().time())
                        asyncio.run(Manual.BUY())

                if keyboard.is_pressed("shift+s"):
                        print('\nbutton @ %s' %datetime.now().time())
                        asyncio.run(Manual.SELL())

                if keyboard.is_pressed("ins"):
                        token_data.clear()
                        user_data()
                        print('data updated\n')

                if keyboard.is_pressed("esc"):
                        break

        except Exception as e:
                logger.critical('core event loop failed -- %s\n' %e)
print('\ngood times?')
