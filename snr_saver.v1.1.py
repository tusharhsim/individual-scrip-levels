from datetime import date, timedelta
import requests
import json
import csv

enctoken = 'X2FZawn9uLerqRFJjDQBwOUw8vJrwWZqwnZE5RB2UFBwdyvuC4GVv7+iN1vFq41EpRHw7qAGocdFwnoG8kUjKFa40hSjVEfTlclRjrjRNYATynG6G9YaXg=='
s_date = date(2021, 4, 15)
e_date = date(2022, 5, 25)

equities = {'RELIANCE' : [738561, 10], 'HDFCBANK' : [341249, 10], 'INFY' : [408065, 10], 'ICICIBANK' : [1270529, 10],
            'HDFC' : [340481, 10], 'TCS' : [2953217, 10], 'KOTAKBANK' : [492033, 10], 'ITC' : [424961, 10], 'LT' : [2939649, 10], 'HINDUNILVR' : [356865, 10]}

def level_extractor(enctoken, first_date, last_date, c_id, pa):
        def support_finder(low, high, pa):
                temp_support = [0]*len(low)
                d_pa = pa*1.4
                u_pa = pa*2.1
                floor, ceil = 0,0
                down_move, up_move = 0,0
                for i in range(len(low)):
                        try:
                                if (low[i] > low[i+1]) and not up_move:
                                        if not ceil:
                                                ceil = high[i]
                                        down_move = ceil - low[i+1]
                                elif (low[i] < low[i+1]) and down_move:
                                        if not floor:
                                                floor = low[i]
                                                touch = i
                                        up_move = high[i+1] - floor

                                if up_move and (low[i] > low[i+1]):
                                        if (up_move >= u_pa and down_move >= d_pa) or (up_move > u_pa*1.6):
                                                sup = int(floor)
                                                while sup in temp_support:
                                                    sup -= 1
                                                temp_support[touch] = sup
                                        down_move, up_move = 0,0
                                        floor, ceil = 0,0
                        except:
                                if (i == len(low)-1) and floor:
                                        if (up_move >= u_pa and down_move >= d_pa) or (up_move > u_pa*1.6):
                                                sup = int(floor)
                                                while sup in temp_support:
                                                    sup -= 1
                                                temp_support[touch] = sup
                return temp_support

        def resistance_finder(low, high, pa):
                temp_resistance = [0]*len(high)
                d_pa = pa*2.1
                u_pa = pa*1.4
                floor, ceil = 0,0
                down_move, up_move = 0,0
                for i in range(len(high)):
                        try:
                                if (high[i] < high[i+1]) and not down_move:
                                        if not floor:
                                                floor = low[i]
                                        up_move = high[i+1] - floor
                                elif (high[i] > high[i+1]) and up_move:
                                        if not ceil:
                                                ceil = high[i]
                                                touch = i
                                        down_move = ceil - low[i+1]

                                if down_move and (high[i] < high[i+1]):
                                        if (up_move >= u_pa and down_move >= d_pa) or (down_move > d_pa*1.6):
                                                res = int(ceil)
                                                while res in temp_resistance:
                                                    res += 1
                                                temp_resistance[touch] = res
                                        down_move, up_move = 0,0
                                        floor, ceil = 0,0
                        except:
                                if (i == len(high)-1) and ceil:
                                        if (up_move >= u_pa and down_move >= d_pa) or (down_move > d_pa*1.6):
                                                res = int(ceil)
                                                while res in temp_resistance:
                                                    res += 1
                                                temp_resistance[touch] = res
                return temp_resistance

        ohlc = []
        headers = {'Authorization': 'enctoken '+str(enctoken),
                   'Content-Type': 'application/x-www-form-urlencoded'}

        while first_date <= last_date:
                if last_date - first_date >= timedelta(days=60):
                        params = (('from', first_date),('to', first_date+timedelta(days=60)))
                        first_date += timedelta(days=60)
                else:
                        params = (('from', first_date),('to', last_date))
                        first_date = last_date + timedelta(days=1)
                response = requests.get('https://kite.zerodha.com/oms/instruments/historical/%s/5minute' %(c_id), headers = headers, params = params)
                ohlc += response.json()['data']['candles']

        high = []
        low = []
        for i in ohlc[::][:]:
                high.append(i[2])
                low.append(i[3])

        resistance = resistance_finder(low, high, pa)
        support = support_finder(low, high, pa)

        ltp = requests.get('https://kite.zerodha.com/oms/instruments/historical/%s/day' %(c_id),
                   headers={'Authorization': 'enctoken %s' %(enctoken),
                            'Content-Type': 'application/x-www-form-urlencoded'},
                   params=(('from', e_date + timedelta(days=1)),('to', e_date + timedelta(days=1)))).json()['data']['candles'][-1][4]
        baseline = int(ltp)
        lower_limit = baseline - (pa*21)
        upper_limit = baseline + (pa*21)

        ranged_level_s = [i for i in support if i >= lower_limit and i <= upper_limit]
        ranged_level_r = [i for i in resistance if i >= lower_limit and i <= upper_limit]

        return list(set(ranged_level_s)), list(set(ranged_level_r))
        #return list(set(support)), list(set(resistance))

for key, value in equities.items():
        supports, resistances = level_extractor(enctoken, s_date, e_date, value[0], value[1])
        with open('%s.csv' %(key), 'w',  newline="") as level_file:
                csvwriter = csv.writer(level_file)
                csvwriter.writerow(['support:'])
                csvwriter.writerow(supports)
                csvwriter.writerow(['resistance:'])
                csvwriter.writerow(resistances)
        print('levels saved for %s' %(key))
