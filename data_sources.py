"""
import passwords dict


"""
import helper_functions
import os
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import sys
import pickle
import requests
import ast

if "passwords" not in locals():
    passwords = helper_functions.get_pwds()

## TOS Keys #####################################################
def check_subscriptions():

    def check_proxy_bot():
        """
        PROXYBOT DISCONTINUED
        https://proxybot.io/
        checks how many remaining requests i have on the free plan
        if requests get below 1000 say something
        """
        """check proxybot.io"""
        key = passwords['proxy_bot_key']
        url = 'https://proxybot.io/api/v1/'+key+'/usage'

        response = requests.get(url=url)
        data = response.json()
        if data["remainingRequests"] < 1000:
            message = 'PROXY BOT - remaining requests:'+str(data["remainingRequests"])+'of'+str(data["requestsLimit"])
            return message

    def check_TOS_keys():

        def check_token_status(token):

            now = datetime.now()

            if token == 'tos_access_token':
                next_update = datetime.strptime(passwords['tos_access_token_last_update'],'%Y-%m-%d %H:%M:%S.%f')
                if (now - next_update).total_seconds() >= -15: # give a 15 second buffer
                    print('ACCESS TOKEN NEEDS UPDATE')
                    return True

            elif token == 'tos_refresh_token':
                next_update = datetime.strptime(passwords['tos_refresh_token_next_update'], '%Y-%m-%d %H:%M:%S.%f')
                time_to_next_update = (now - next_update).days
                if time_to_next_update >= -7:
                    print(str(abs(time_to_next_update)),'days until refresh token expires')

                if time_to_next_update >= -1:  # give a 1 day buffer
                    print('REFRESH TOKEN NEEDS UPDATE')
                    return True

        def get_new_refresh_token(code):

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'authorization_code',
                'refresh_token': passwords['tos_refresh_token'],
                'access_type': 'offline',
                'code': code,
                'client_id': passwords['tos_key'] + '@AMER.OAUTHAP',
                'redirect_uri': 'http://localhost'}

            response = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
            data = response.json()

            # get the new tokens and expiration date and update it in pwd info
            pwd_changes = {}
            pwd_changes['tos_refresh_token'] = data['refresh_token']
            pwd_changes['tos_refresh_token_next_update'] = datetime.now() + timedelta(seconds=data['refresh_token_expires_in'])
            pwd_changes['tos_access_token'] = data['access_token']
            pwd_changes['tos_access_token_last_update'] = datetime.now() + timedelta(seconds=data['expires_in'])
            helper_functions.change_pwds(pwd_changes)

        def get_new_auth_code(): #passwords

            import urllib.parse

            method = 'GET'
            base_url = 'https://auth.tdameritrade.com/auth?'
            client_id = passwords['tos_key'] + '@AMER.OAUTHAP'
            params = {'response_type': 'code', 'redirect_uri': 'http://localhost', 'client_id': client_id}
            login_url = requests.Request(method=method, url=base_url, params=params).prepare()
            login_url = login_url.url

            print('------------------------------------------------------------------------------------------------------------')
            print('NEED TO GET A NEW REFRESH TOKEN')
            print(login_url)
            input_code = input('input code:')
            print('------------------------------------------------------------------------------------------------------------')

            input_code = input_code.split('?code=')[1]
            input_code = urllib.parse.unquote(input_code)

            # payload = {'su_username': '',
            #            'su_password': ''}
            #
            # headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
            # headers = {'Content-Type':'application/json;charset=UTF-8'}
            #
            # login_url = 'https://auth.tdameritrade.com/oauth?client_id=N2RXH0P5GO0WYC8IG1H74I1FQSP0Y0TM%40AMER.OAUTHAP&response_type=code&redirect_uri=http%3A%2F%2Flocalhost'
            # after_login_url =  'https://auth.tdameritrade.com/oauth?client_id=N2RXH0P5GO0WYC8IG1H74I1FQSP0Y0TM@AMER.OAUTHAP&response_type=code&redirect_uri=http://localhost&lang=en-us'
            # after_accept_url = 'https://auth.tdameritrade.com/oauth?client_id=N2RXH0P5GO0WYC8IG1H74I1FQSP0Y0TM%40AMER.OAUTHAP&response_type=code&redirect_uri=http%3A%2F%2Flocalhost&lang=en-us'
            #
            # with requests.session() as session:
            #     resp = session.get(login_url)
            #     resp_1 = session.post(after_login_url,data=payload)
            #     resp_2 = session.post(after_accept_url,headers=headers,allow_redirects=False)
            #     resp_3 = session.post(after_accept_url)

            return input_code

        def get_new_access_token():

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': passwords['tos_refresh_token'],
                'access_type': '',
                'code':'',
                'client_id': passwords['tos_key'] + '@AMER.OAUTHAP',
                'redirect_uri': 'http://localhost'}

            response = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
            data = response.json()

            pwd_changes = {}
            pwd_changes['tos_access_token'] = data['access_token']
            pwd_changes['tos_access_token_last_update'] = datetime.now() + timedelta(seconds=data['expires_in'])
            helper_functions.change_pwds(change_dict=pwd_changes)

        ######################################

        if check_token_status(token='tos_refresh_token'):
            auth_code = get_new_auth_code()
            get_new_refresh_token(code=auth_code)

        elif check_token_status(token='tos_access_token'):
            get_new_access_token()

    #######################################################

    check_TOS_keys()

## Data Sources #################################################

#!!! may need to have a class object input
def get_intraday_EOD_data(custom_date=False,use_proxy=False):
    """
    get the list of tickers for that day
    get the intraday data for all of them
    save that data as a variable in each of the tickers files

    USING THE ALPACA API
    CONVERT DATA TO DATAFRAME WITH COLUMNS
        Date        Open      High       Low      Close     Volume
    0   2019-05-31  124.2300  124.6150  123.3250  123.9400  11987596
    1   2019-05-30  125.2600  125.7600  124.7800  125.7300  16785285
    2   2019-05-29  125.3800  125.3900  124.0400  124.9400  22763140
    3   2019-05-28  126.9800  128.0000  126.0500  126.1600  23128359

    custom_day = 2020-05-31 (year-month-day)

    """
    # gets really incomplete data
    def alpaca_data(custom_date=''):
        import alpaca_trade_api as tradeapi

        if custom_date:
            custom_date = custom_date.split('-')
            year = int(custom_date[0])
            month = int(custom_date[1])
            day = int(custom_date[2])
        else:
            now = datetime.now()
            year = now.year
            month = now.month
            day = now.day


        api = tradeapi.REST(key_id=passwords['alpaca_key_id'], secret_key=passwords['alpaca_secret_key'])

        start = pd.Timestamp(year=year, month=month, day=day, hour=6, minute=30, tz='America/Chicago').isoformat()
        end = pd.Timestamp(year=year, month=month, day=day, hour=15, tz='America/Chicago').isoformat()

        # Get daily price data for AAPL over the last 5 trading days.
        barset = api.get_barset('ABIO', '1Min', end=end, start=start, limit=400)
        df_list = []

        # Bar({'c': 319.67, 'h': 319.67, 'l': 319.67, 'o': 319.67, 't': 1590756000, 'v': 500})

        for i in barset['ABIO']:
            row = [i.t,i.o,i.h,i.l,i.c,i.v]
            # df_list[i.t]={'Open':i.o,
            #                'High':i.h,
            #                'Low':i.l,
            #                'Close':i.c,
            #                'Volume':i.v}
            df_list.append(row)

        df = pd.DataFrame(df_list,columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

        df = df.loc[:'2020-05-29 09:31:00']

        return df

    # gets more complete data but doesnt do ext hours
    def alphavantage_data(ticker):

        keys = [passwords['alphavantage_key1'],passwords['alphavantage_key2'],passwords['alphavantage_key3']]

        for key in keys:
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+ticker+'&interval=1min&outputsize=full&apikey='+key
            #resp = requests.get(url, timeout=5)
            resp = helper_functions.run_request(url=url,use_proxy=use_proxy)
            if not resp:
                continue

        #!!! NEEDS ERROR HANDLING IN CASE RESP == NONE
        data = resp.json()

        df = pd.DataFrame.from_dict(data["Time Series (1min)"], orient='index')
        df = df.reset_index()
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(int)

        mask = (df['Date'] >'2020-05-29 09:30:00')

        df = df.loc[mask]

        return df

    # gets more complete data w/ extended hours
    def TOS_data(ticker, use_date):
        """
        use_date = 2020-5-29 (year-month-day)

        """

        use_date = use_date.split('-')
        year = int(use_date[0])
        month = int(use_date[1])
        day = int(use_date[2])

        # TOS url build
        extended_hours_data = 'true'
        period = '2'  # The number of periods to show.
        frequency_type = 'minute'  # The type of frequency with which a new candle is formed.
        frequency = '1'  # The number of the frequencyType to be included in each candle.

        key = passwords['tos_key']

        # get all data, both pre and post market (time in milliseconds)
        start = str(int(datetime(year=year, month=month, day=day, hour=3).timestamp() * 1000))
        end = str(int(datetime(year=year, month=month, day=day, hour=22).timestamp() * 1000))

        # url (start to end date) gets minute intraday for specific day
        url = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/pricehistory?apikey=" + key + \
              "&frequencyType=" + frequency_type + \
              "&endDate=" + end + \
              "&startDate=" + start + \
              "&needExtendedHoursData=" + extended_hours_data

        # response = requests.get(url=url)
        response = helper_functions.run_request(url=url,use_proxy=False)
        #!!! NEED TO DO ERROR HANDLING IN CASE RESPONSE == NONE

        data = response.json()

        data = data['candles']
        df = pd.DataFrame(data)
        df = df.rename(columns={'datetime': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low',
                                'close': 'Close', 'volume': 'Volume'})

        df['Date'] = pd.to_datetime(df['Date'], unit='ms') - timedelta(hours=5)

        return df

    #######################################################

    if custom_date:
        custom_date = custom_date.split('-')
        year = int(custom_date[0])
        month = int(custom_date[1])
        day = int(custom_date[2])
    else:
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day

    # directory build
    date_str = str(year) + '-' + str(month) + '-' + str(day)
    directory = 'Stock_Notes/Pickle_Dates/' + date_str

    print('getting EOD data for file:',date_str)

    # loop through date folders
    for filename in os.listdir(directory):
        if filename.endswith(".pickle"):
            ticker = filename.split('.')[0]
            print('     ', ticker, end='', flush=True)

            # open file and read report
            file_path = directory + "/" + ticker + ".pickle"

            with open(file_path, "rb") as data:
                report = pickle.load(data)

            #if theres a key for EOD data in the report and the value is a dataframe then skip that ticker
            if 'EOD data' in report.keys():
                if isinstance(report['EOD data'], pd.DataFrame):
                    print('[c]')
                    continue

            df = TOS_data(ticker=ticker, use_date=date_str)
            report['EOD data'] = df

            # open file and write in EOD data
            with open(file_path, 'wb') as data:
                pickle.dump(report, data)
            print('') #leave here

def polygon_ticker_details(ticker,use_proxies=False):
    """
    "polygon ticker details (https://api.polygon.io/v1/meta/symbols/"+ticker+"/company")
        - CIK
        - comp name
        - exchange
        - industry
        - sector
    """
    key = passwords['polygon_key']
    url = "https://api.polygon.io/v1/meta/symbols/" + ticker + "/company?apiKey="+key
    #funct_name = 'polygon ticker details'
    funct_name = sys._getframe().f_code.co_name
    print('     ',funct_name)

    ret_vals = {funct_name: {'CIK': None, 'Industry': None, 'Sector': None,
                             'Market Cap': None, 'Exchange': None, 'Comp Name': None, 'ERRORS': []}}

    try:
        response = helper_functions.run_request(url=url, use_proxy=False)
        data = response.json()

        ret_vals = {funct_name: {'CIK': data['cik'], 'Industry': data['industry'], 'Sector': data['sector'],
                                 'Market Cap': data['marketcap'], 'Exchange': data['exchange'],
                                 'Comp Name': data['name'], 'ERRORS': []}}

    except:
        ret_vals[funct_name]['ERRORS'].append('Request Failure')

    return ret_vals

def polygon_news(ticker,use_proxies=False):
    """
    polygon news ('https://api.polygon.io/v1/meta/symbols/' + ticker + '/news?perpage=' + perpage + '&page=' + pages + '&apiKey=AKZFIX7BDQ2YJUKQKHCE')
        - news headlines
    ALSO NOT RELIABLE
    # NEED TO ADJUST FOR IEX GETTING BLOCKED WHEN USING A VPN
    """

    #funct_name = 'polygon news'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    pages = '1'
    num_results = '5'

    key = passwords['polygon_key']

    url = 'https://api.polygon.io/v2/reference/news?ticker='+ticker+'&order=asc&limit='+num_results+'&sort=published_utc&apiKey='+key

    response = helper_functions.run_request(url=url, use_proxy=False)

    if response:
        data = response.json()
        news_list = []
        for i in data['results']:
            news_list.append([i['title'], i['article_url']])

        ret_vals = {funct_name: {'News Headlines': news_list}}

    else:
        ret_vals = {funct_name: {'News Headlines': None}}

    return ret_vals

def iex_news(ticker,use_proxies=False):
    """
    IEX news ("https://cloud.iexapis.com/stable/stock/"+ticker+"/news/last/"+last+"/?token="+p_key)
        - news headlines
    NOT RELIABLE, DOESNT GET CURRENT DAY NEWS
    """
    #funct_name = 'iex news'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    last = '5'
    days = 3

    p_key = passwords['iex_key']
    url = 'https://cloud.iexapis.com/stable/stock/'+ticker+'/news/last/'+last+'?token='+p_key

    response = helper_functions.run_request(url=url, use_proxy=use_proxies)
    if response:
        data = response.json()

        now = datetime.now()
        news_list = []

        for i in data:
            date_time = i['datetime']
            date = datetime.fromtimestamp(date_time / 1000.0)
            headline = i['headline']
            url = i['url']

            if date >= (now - timedelta(days=days, hours=12)):
                date = datetime.strftime(date, "%b-%d-%y %I:%M%p")
                row = [date, headline, url]
                news_list.append(row)

        ret_vals = {funct_name: {'News Headlines': news_list}}

    else:
        ret_vals = {funct_name: {'News Headlines': None}}

    return ret_vals

# broken web scraper
def benzinga_news(ticker, use_proxies=False):
    #funct_name = 'benzinga news'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    #try:
    url = 'https://www.benzinga.com/stock/' + ticker + '/'
    url = 'https://www.benzinga.com/quote/AAPL'
    response = helper_functions.run_request(url=url, use_proxy=use_proxies)

    data = response.content

    soup = BeautifulSoup(data, 'lxml')
    table = soup.body.find('div', {'class': 'NewsMenu__ContentWrapper-gwbipf-0 glJeVy content-wrapper tab-content lg:h-23/25 overflow-y-scroll quote-news p-2 mt-2'})
    news_list = []
    for li in table.findAll("div", {'class': 'py-2 content-headline'}):
        link = li.find('a', href=True).get('href')
        title = li.find('a').text
        #date = li.find('span', {'class': 'date'}).text

        # # remove the '-0400'
        # date = date.split(' -')
        # del date[-1]
        # date = date[0]
        # # remove the day
        # date = date.split(', ')
        # del date[0]
        # date = date[0]
        # # convert to datetime
        # date = datetime.strptime(date, '%d %b %Y %H:%M:%S')
        #
        # news_list.append([date, title, link])

    ret_vals = {funct_name: {'News Headlines': news_list, 'ERRORS': []}}

    # except:
    #     ret_vals = {funct_name: {'News Headlines': None, 'ERRORS': ['Request Failure']}}

    return ret_vals

def iex_stock_stats(ticker,use_proxies=False):
    """
    IEX stock stats ("https://cloud.iexapis.com/stable/stock/" + ticker + "/stats/?token=" + p_key)
        - comp name
        - market cap
        - shares outstanding
        - float
    """

    #funct_name = 'iex stock stats'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    p_key = passwords['iex_key']
    url = "https://cloud.iexapis.com/stable/stock/" + ticker + "/stats/?token=" + p_key

    response = helper_functions.run_request(url=url, use_proxy=False)

    if response:
        data = response.json()
        ret_vals = {
            funct_name: {'Market Cap': data['marketcap'],
                         'Float': data['float'],
                         'Comp Name': data['companyName'],
                         'Shares Outstanding': data['sharesOutstanding'],
                         'ERRORS': []}}

    else:
        ret_vals = {funct_name: {'Market Cap': None,
                                 'Float': None,
                                 'Comp Name': None,
                                 'Shares Outstanding': None,
                                 'ERRORS': ['Request Failure']}}

    return ret_vals

def iex_stock_company_info(ticker,use_proxies=False):
    """
    IEX stock company info ("https://cloud.iexapis.com/v1/stock/" + ticker + "/company/?token=" + s_key)
        - comp name
        - exchange
        - industry
        - sector
    """

    #funct_name = 'iex stock company info'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    p_key = passwords['iex_key']
    url = "https://cloud.iexapis.com/v1/stock/" + ticker + "/company/?token=" + p_key

    response = helper_functions.run_request(url=url, use_proxy=False)

    if response:
        data = response.json()

        ret_vals = {funct_name: {'Comp Name': data['companyName'],
                                 'Exchange': data['exchange'],
                                 'Industry': data['industry'],
                                 'Sector': data['sector'],
                                 'ERRORS': []}}

    else:
        ret_vals = {funct_name: {'Comp Name': None,
                                 'Exchange': None,
                                 'Industry': None,
                                 'Sector': None,
                                 'ERRORS': ['Request Failure']}}

    return ret_vals

def iex_splits(ticker,use_proxies=False):
    """
    IEX splits ("https://cloud.iexapis.com/v1/stock/"+ticker+"/splits/3m/?token="+s_key)
        - reverse split date
        - reverse split ratio
    """

    #funct_name = 'iex splits'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    p_key = passwords['iex_key']
    url = "https://cloud.iexapis.com/v1/stock/" + ticker + "/splits/3m/?token=" + p_key

    ret_vals = {funct_name: {'Split Date': None, 'Split Description': None}}

    response = helper_functions.run_request(url=url, use_proxy=False)

    if response:
        data = response.json()
        try:
            ret_vals = {funct_name: {'Split Date': data['exDate'], 'Split Description': data['description']}}
        except:
            pass

    return ret_vals

def marketwatch_overview(ticker,use_proxies=False):
    """
    market watch overview ("https://www.marketwatch.com/investing/stock/" + ticker)
        - market cap
        - float
        - short float percent
        - short interest
    """

    #funct_name = 'marketwatch overview'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    url = "https://www.marketwatch.com/investing/stock/" + ticker

    ret_vals = {funct_name: {'Market Cap': None,  # provided
                             'Float': None,  # provided
                             'Short Interest': None,  # provided
                             'Assigned Short Float': None,  # provided
                             'Calculated Short Float': None,  # calculated
                             'ERRORS': []
                             }}

    response = helper_functions.run_request(url=url, use_proxy=use_proxies)
    if response:
        data = response.content

        try:
            soup = BeautifulSoup(data, 'lxml')
            table = soup.body.find('div', {'class': 'element element--list'})
        except:
            ret_vals[funct_name]['ERRORS'].append('Request Failure')
            return ret_vals

        try:  # FLOAT
            ret_vals[funct_name]['Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(table.find_all('li')[5].span.text, convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Float')

        try:  # SHORT INTEREST
            ret_vals[funct_name]['Short Interest'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(table.find_all('li')[13].span.text, convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Short Interest')

        try:  # ASSIGNED SHORT FLOAT
            ret_vals[funct_name]['Assigned Short Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(table.find_all('li')[14].span.text, convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Assigned Short Float')

        try:  # CALCULATED SHORT FLOAT
            ret_vals[funct_name]['Calculated Short Float'] = helper_functions.check_for_zeroes(
                ret_vals[funct_name]['Short Interest'] / ret_vals[funct_name]['Float'])
        except:
            ret_vals[funct_name]['ERRORS'].append('Calculated Short Float')

        try:  # MARKET CAP
            ret_vals[funct_name]['Market Cap'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(table.find_all('li')[3].span.text, convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Market Cap')

    return ret_vals

# broken web scraper
def marketwatch_financials(ticker,use_proxies=False):
    """
    market watch financials ("https://www.marketwatch.com/investing/stock/"+ticker+"/financials/balance-sheet/quarter")
        - cash and short term assets
        - cash
        - short term debt
        - long term debt
    """

    #funct_name = 'marketwatch financials'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    ret_vals = {funct_name: {'CASTI': None,
                             'Cash': None,
                             'ST debt': None,
                             'LT debt': None,  # all provided
                             'ERRORS': []}}

    url = "https://www.marketwatch.com/investing/stock/" + ticker + "/financials/balance-sheet/quarter"
    response = helper_functions.run_request(url=url, use_proxy=use_proxies)

    if response:
        data = response.content
        try:
            df = pd.read_html(data)
        except:
            ret_vals[funct_name]['ERRORS'].append('Pandas HTML Parse Error')
            return ret_vals

        asset_df = df[0]

        col_names = []
        for col in asset_df.columns:
            col_names.append(col)
        date_name = col_names[-2]
        asset_df = asset_df[date_name]
        try:
            liab_df = df[1]
            liab_df = liab_df[date_name]
        except:
            ret_vals

        try:
            ret_vals[funct_name]['CASTI'] = helper_functions.string_num_converter(asset_df[0], convert_to='num')
        except:
            ret_vals[funct_name]['ERRORS'].append('CASTI')

        try:
            ret_vals[funct_name]['Cash'] = helper_functions.string_num_converter(asset_df[1], convert_to='num')
        except:
            ret_vals[funct_name]['ERRORS'].append('Cash')

        try:
            ret_vals[funct_name]['ST debt'] = helper_functions.string_num_converter(liab_df[1], convert_to='num')
        except:
            ret_vals[funct_name]['ERRORS'].append('ST debt')

        try:
            ret_vals[funct_name]['LT debt'] = helper_functions.string_num_converter(liab_df[11], convert_to='num')
        except:
            ret_vals[funct_name]['ERRORS'].append('LT debt')

    else:
        ret_vals[funct_name]['ERRORS'].append('Request Failure')

    return ret_vals

# broken web scraper
def finviz(ticker,use_proxies=False):
    """
    finviz ("https://finviz.com/quote.ashx?t=" + ticker)
        - market cap
        - shares outstanding
        - float
        - short float percent
        - short interest
        - news headlines
        - current day volume
        - analyst upgrades/downgrades X
        - book value/share X
        - current day volume
        """

    #funct_name = 'finviz'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    url = "https://finviz.com/quote.ashx?t=" + ticker

    ret_vals = {funct_name: {'Market Cap': None,  # provided
                             'Shares Outstanding': None,  # provided
                             'Float': None,  # provided
                             'Short Interest': None,  # calculated
                             'Assigned Short Float': None,  # provided
                             'Curr Day Volume': None,  # provided
                             'News Headlines': [],  # provided
                             'ERRORS': []}}

    response = helper_functions.run_request(url=url, use_proxy=use_proxies)

    if response:
        data = response.content

        ############################################
        # GET THE NEWS HEADLINES
        ############################################
        soup = BeautifulSoup(data, 'lxml')

        # get the table data from the news section
        try:
            #   gets [Date, Title, URL]
            table = soup.find("table", {"id": "news-table"})
            rows = []
            for tr in table.findAll("tr"):
                row = []
                date = ''
                for td in tr:
                    text = td.text
                    row.append(text)
                    try:
                        link = td.find('a', href=True).get('href')
                        row.append(link)
                    except:
                        pass

                rows.append(row)
            # clean up the data
            for row in rows:
                date_text = row[0]

                # remove '\xa0' in string
                if '\xa0' in date_text:
                    date_text = date_text.replace(u'\xa0', u'')

                # make sure theres a date in front of every time
                date_text = date_text.split(' ')
                if len(date_text) == 2:
                    date = date_text[0]
                    row[0] = date_text[0] + ' ' + date_text[1]
                else:
                    row[0] = date + ' ' + date_text[0]
                # convert to datetime
                row[0] = datetime.strptime(row[0], '%b-%d-%y %I:%M%p')

                ret_vals[funct_name]['News Headlines'].append(row)
        except:
            ret_vals[funct_name]['ERRORS'].append('News Headlines')

        ############################################
        # GET SHARE STATS
        ############################################
        try:
            finviz_df = pd.read_html(data)

        except:
            ret_vals[funct_name]['ERRORS'].append('All Share Stats')
            return ret_vals

        # otherwise works as normal, variables will be assigned None instead of an error
        try:  # MARKETCAP
            ret_vals[funct_name]['Market Cap'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(finviz_df[6][1][1], convert_to='num'))

        except:
            ret_vals[funct_name]['ERRORS'].append('Market Cap')

        try:  # SHARES OUTSTANDING
            ret_vals[funct_name]['Shares Outstanding'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(finviz_df[6][9][0], convert_to='num'))

        except:
            ret_vals[funct_name]['ERRORS'].append('Shares Outstanding')

        try:  # STOCK FLOAT
            ret_vals[funct_name]['Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(finviz_df[6][9][1], convert_to='num'))

        except:
            ret_vals[funct_name]['ERRORS'].append('Float')

        try:  # SHORT PERCENT FLOAT
            ret_vals[funct_name]['Assigned Short Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(finviz_df[6][9][2], convert_to='num'))

        except:
            ret_vals[funct_name]['ERRORS'].append('Assigned Short Float')

        try:  # SHORT INTEREST
            ret_vals[funct_name]['Short Interest'] = helper_functions.check_for_zeroes(
                int(ret_vals[funct_name]['Assigned Short Float'] * ret_vals[funct_name]['Float']))

        except:
            ret_vals[funct_name]['ERRORS'].append('Short Interest')

        try:  # CURR DAY VOLUME
            ret_vals[funct_name]['Curr Day Volume'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(finviz_df[6][9][11], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Curr Day Volume')

    else:
        ret_vals[funct_name]['ERRORS'].append('Request Failure')

    return ret_vals

def yahoo_key_stats(ticker,use_proxies=False):
    """
    yahoo key stats ("https://finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker)
        - market cap
        - shares outstanding
        - float
        - short float percent
        - short interest
        - prev month short interest
        - report date
        - prev month report date
    """

    #funct_name = 'yahoo key stats'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    url = "https://finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker

    ret_vals = {funct_name: {'Market Cap': None,  # provided
                             'Shares Outstanding': None,  # provided
                             'Float': None,  # provided
                             'Assigned Short Float': None,  # provided
                             'Calculated Short Float': None,  # calculated
                             'Short Interest': None,  # provided
                             'Prev Month Short Interest': None,  # provided
                             'Report Date': None,  # provided
                             'Prev Month Report Date': None,  # provided
                             'ERRORS': []}}

    response = helper_functions.run_request(url=url, use_proxy=use_proxies)

    if response:
        data = response.content

        # pandas method
        try:
            yahoo_df = pd.read_html(data)

        except:
            ret_vals[funct_name]['ERRORS'].append('All Share Stats')
            return ret_vals

        try:  # MARKET CAP
            columns = []
            for i in range(0, len(yahoo_df[0].columns)):
                columns.append(i)

            yahoo_df[0].columns = columns

            ret_vals[funct_name]['Market Cap'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(yahoo_df[0][1][0], convert_to='num'))

        except:
            ret_vals[funct_name]['ERRORS'].append('Market Cap')

        try:  # SHARES OUTSTANDING
            ret_vals[funct_name]['Shares Outstanding'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(yahoo_df[2][1][2], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Shares Outstanding')

        try:  # STOCK FLOAT
            ret_vals[funct_name]['Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(yahoo_df[2][1][3], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Float')

        try:  # SHORT INTEREST
            ret_vals[funct_name]['Short Interest'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(yahoo_df[2][1][6], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Short Interest')

        try:  # CALCUALTED SHORT PERCENTAGE OF FLOAT
            ret_vals[funct_name]['Calculated Short Float'] = helper_functions.check_for_zeroes(
                round((ret_vals[funct_name]['Short Interest'] / ret_vals[funct_name]['Float']), 2))
        except:
            ret_vals[funct_name]['ERRORS'].append('Calculated Short Float')

        try:  # ASSIGNED SHORT PERCENTAGE OF FLOAT
            ret_vals[funct_name]['Assigned Short Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(yahoo_df[2][1][8], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Assigned Short Float')

        try:  # REPORT DATE
            ret_vals[funct_name]['Report Date'] = yahoo_df[2][0][6]
        except:
            ret_vals[funct_name]['ERRORS'].append('Report Date')

        try:  # PREVIOUS MONTH SHORT INTEREST
            ret_vals[funct_name]['Prev Month Short Interest'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(yahoo_df[2][1][10], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Prev Month Short Interest')

        try:  # PREVIOUS MONTH REPORT DATE
            ret_vals[funct_name]['Prev Month Report Date'] = yahoo_df[2][0][10]
        except:
            ret_vals[funct_name]['ERRORS'].append('Prev Month Report Date')

    else:
        ret_vals[funct_name]['ERRORS'].append('Request Failure')

    return ret_vals

# wrapper not returning short report dates, or industry and sector
def yahoo_API(ticker,use_proxies=False):

    #funct_name = 'yahoo API'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    ret_vals = {funct_name: {'Market Cap': None,
                             'Curr Day Volume': None,
                             'Shares Outstanding': None,
                             'Float': None,
                             'Assigned Short Float': None,
                             'Short Interest': None,
                             'Prev Month Short Interest': None,
                             'Report Date': None,
                             'Prev Month Report Date': None,
                             'Industry': None,
                             'Sector': None,
                             'ERRORS': []}}

    try:
        response = yf.Ticker(ticker)
        data = response.info
    except:
        ret_vals[funct_name]['ERRORS'].append('Request Failure')
        return ret_vals

    ret_vals[funct_name]['Market Cap'] = data['marketCap']
    ret_vals[funct_name]['Curr Day Volume'] = data['volume']
    ret_vals[funct_name]['Shares Outstanding'] = data['sharesOutstanding']
    ret_vals[funct_name]['Float'] = data['floatShares']
    ret_vals[funct_name]['Assigned Short Float'] = data['shortPercentOfFloat']
    ret_vals[funct_name]['Short Interest'] = data['sharesShort']
    ret_vals[funct_name]['Prev Month Short Interest'] = data['sharesShortPriorMonth']

    try:
        ret_vals[funct_name]['Report Date'] = pd.to_datetime(data['dateShortInterest'] * 1000, unit='ms')
    except:
        ret_vals[funct_name]['Report Date'] = None
    try:
        ret_vals[funct_name]['Prev Month Report Date'] = pd.to_datetime(data['sharesShortPreviousMonthDate'] * 1000,unit='ms')
    except:
        ret_vals[funct_name]['Prev Month Report Date'] = None

    ret_vals[funct_name]['Industry'] = data['industry']
    ret_vals[funct_name]['Sector'] = data['sector']

    return ret_vals

# broken web scraper
def shortsqueeze(ticker,use_proxies=False):
    """
    shortsqueeze ("http://shortsqueeze.com/?symbol=" + ticker + "&submit=Short+Quote")
        - market cap
        - float
        - short float percent
        - short interest
        - prev month short interest
        - report date
    """
    #funct_name = 'shortsqueeze'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    url = "http://shortsqueeze.com/?symbol=" + ticker + "&submit=Short+Quote"

    ret_vals = {funct_name: {'Short Interest': None,  # provided
                             'Prev Month Short Interest': None,  # provided
                             'Float': None,  # provided
                             'Assigned Short Float': None,  # provided
                             'Calculated Short Float': None,  # calculated
                             'Market Cap': None,  # provided
                             'Exchange': None,  # provided
                             'Report Date': None,  # provided
                             'ERRORS': []}}

    response = helper_functions.run_request(url=url, use_proxy=use_proxies)

    if response:
        try:
            data = response.content
            SS_df = pd.read_html(data)

        except:
            ret_vals[funct_name]['ERRORS'].append('HTML Parse Fail')
            return ret_vals

        try:  # SHORT INTEREST
            ret_vals[funct_name]['Short Interest'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(SS_df[31][1][4], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Short Interest')

        try:  # PREVIOUS MONTH SHORT INTEREST
            ret_vals[funct_name]['Prev Month Short Interest'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(SS_df[31][1][5], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Prev Month Short Interest')

        try:  # STOCK FLOAT
            ret_vals[funct_name]['Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(SS_df[33][1][3], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Float')

        try:  # ASSIGNED SHORT PERCENTAGE OF FLOAT
            ret_vals[funct_name]['Assigned Short Float'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(SS_df[31][1][2], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Assigned Short Float')

        try:  # CALCULATED SHORT PERCENTAGE OF FLOAT
            ret_vals[funct_name]['Calculated Short Float'] = helper_functions.check_for_zeroes(
                round((ret_vals[funct_name]['Short Interest'] / ret_vals[funct_name]['Float']), 2))
        except:
            ret_vals[funct_name]['ERRORS'].append('Calculated Short Float')

        try:  # MARKET CAP
            ret_vals[funct_name]['Market Cap'] = helper_functions.check_for_zeroes(
                helper_functions.string_num_converter(SS_df[33][1][4], convert_to='num'))
        except:
            ret_vals[funct_name]['ERRORS'].append('Market Cap')

        try:  # EXCHANGE
            ret_vals[funct_name]['Exchange'] = SS_df[34][1][0]
        except:
            ret_vals[funct_name]['ERRORS'].append('Exchange')

        try:  # REPORT DATE
            ret_vals[funct_name]['Report Date'] = SS_df[34][1][1]
        except:
            ret_vals[funct_name]['ERRORS'].append('Report Date')

    else:
        ret_vals[funct_name]['ERRORS'].append('Request Failure')

    return ret_vals

def TOS_fundamentals(ticker,use_proxies=False):
    key = passwords['tos_key']
    url = "https://api.tdameritrade.com/v1/instruments?apikey=" + key + "&symbol=" + ticker + "&projection=fundamental"

    #funct_name = 'TOS fundamentals'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    ret_vals = {funct_name: {'Market Cap': None,
                             'Float': None,
                             'Shares Outstanding': None,
                             'ERRORS': []}}

    response = helper_functions.run_request(url=url, use_proxy=False)

    if response:
        data = response.json()

        ret_vals[funct_name]['Market Cap'] = int(data[ticker]['fundamental']['marketCap'] * 1000000)
        ret_vals[funct_name]['Float'] = int(data[ticker]['fundamental']['marketCapFloat'] * 1000000)
        ret_vals[funct_name]['Exchange'] = data[ticker]['exchange']
        ret_vals[funct_name]['Shares Outstanding'] = int(data[ticker]['fundamental']['sharesOutstanding'] * 1000000)

    else:
        ret_vals[funct_name]['ERRORS'].append('Request Failure')

    return ret_vals

def get_curr_day_volume(ticker,use_proxies=False):

    def TOS_curr_day_volume(ticker):

        #funct_name = 'TOS quotes'
        key = passwords['tos_key']
        #headers = {'Authorization': ('Bearer ' + passwords['tos_access_token'])}

        url = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/quotes?apikey=" + key

        try:
            response = requests.get(url=url)
            data = response.json()[ticker]
            return data['totalVolume']
        except:
            return None

    def yahoo_curr_day_volume(ticker, use_proxies=False):
        """
        yahoo quotes (“https://finance.yahoo.com/quote/”+ticker+”?p=”+ticker)
            - current day volume
        """
        #funct_name = 'yahoo quotes'
        url = "https://finance.yahoo.com/quote/" + ticker + "?p=" + ticker
        response = helper_functions.run_request(url=url, use_proxy=use_proxies)

        if response:
            data = response.content

            # pandas method
            try:
                yahoo_df = pd.read_html(data)
            except:
                return None

            try:  # CURR DAY VOLUME
                 return helper_functions.check_for_zeroes(helper_functions.string_num_converter(yahoo_df[0][1][6], convert_to='num'))

            except:
                return None
        else:
            return  None

    ####################################################

    #funct_name = 'get curr day volume'
    funct_name = sys._getframe().f_code.co_name
    print('     ', funct_name)

    # try TOS quotes
    curr_day_volume = TOS_curr_day_volume(ticker=ticker)

    if curr_day_volume:
        return {funct_name: {'Curr Day Volume': curr_day_volume, 'ERRORS': []}}
    else:
        # if TOS fails try yahoo quotes without proxy
        curr_day_volume = yahoo_curr_day_volume(ticker=ticker, use_proxies=False)

        if curr_day_volume:
            return {funct_name: {'Curr Day Volume': curr_day_volume, 'ERRORS': ['Cant get TOS curr day volume']}}
        else:
            # if yahoo with proxy fails try with a proxy (proxybot doesnt work anymore, so just try again
            curr_day_volume = yahoo_curr_day_volume(ticker=ticker, use_proxies=False)
            # curr_day_volume = yahoo_curr_day_volume(ticker=ticker, use_proxies=True)

            if curr_day_volume:
                return {funct_name: {'Curr Day Volume': curr_day_volume, 'ERRORS': ['Cant get TOS curr day volume','Yahoo quotes no proxy request failed']}}
            else:
                return {funct_name: {'Curr Day Volume': None, 'ERRORS': ['Cant get TOS or yahoo curr day volume','Yahoo quotes no proxy & proxy request failed']}}

def get_historical_data(ticker,use_proxies):

    def TOS_daily_data(ticker):
        # get daily data going back 3 years

        #funct_name = 'TOS Daily Data'
        funct_name = sys._getframe().f_code.co_name

        key = passwords['tos_key']
        url = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/pricehistory?apikey=" + key + \
              "&periodType=year&period=3&frequencyType=daily&frequency=1&needExtendedHoursData=false"

        response = helper_functions.run_request(url=url, use_proxy=False)

        if response:
            try:
                data = response.json()['candles']

                df = pd.DataFrame(data)
                df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close',
                                        'volume': 'Volume', 'datetime': 'Date'})
                df['Date'] = pd.to_datetime(df['Date'], unit='ms') - timedelta(hours=5)
                df = df.sort_values(by='Date', ascending=False)
                df = df.reset_index(drop=True)
            except:
                return None

            # # if the time is after 3:00 PM and before midnight
            # now_time = datetime.now().time()
            # # if its after 3 and before midnight and not the weekend then add the current day stats into the df
            # if now_time > dt.time(15) and now_time < dt.time(23, 59) and not is_weekend():
            #     now = datetime.now()
            #     # make sure the last recorded df date != the current day date
            #     if df['Date'].iloc[0] != pd.Timestamp(year=now.year, month=now.month, day=now.day).isoformat():
            #         # add in the current day data
            #         df = insert_last_day_data(ticker=ticker,input_df=df)

            now = datetime.now()
            # make sure the last recorded df date != the current day date
            if df['Date'].iloc[0] == pd.Timestamp(year=now.year, month=now.month, day=now.day).isoformat():
                df = df.iloc[1:]

        else:
            df = None
        return df

    def alphavantage(ticker, output_size='full'):  # start='', end='', num_days=''
        # can either input start and end dates or number of days to get datafor  dates are  %Y-%m-%d format
        """"
        Alphavantage API: *can handle OTCs
        can input start (p0) and end (p1) dates or number of days to get data, dates are  %Y-%m-%d format

        DOES NOT GIVE CURRENT DAY DATA

        """
        #funct_name = 'Alphavantage'
        funct_name = sys._getframe().f_code.co_name

        key_list = [passwords['alphavantage_key3'], passwords['alphavantage_key2'], passwords['alphavantage_key1']]

        for key in key_list:
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + ticker + "&outputsize=" + output_size + "&apikey=" + key + "&datatype=json"

            response = helper_functions.run_request(url=url, use_proxy=False)
            if response:
                break

        if response:
            try:
                # set up the dataframe
                data = response.json()
                df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index')
                df = df.reset_index()
                df = df.rename(
                    columns={'index': 'Date', '1. open': 'Open', '2. high': 'High', '3. low': 'Low',
                             '4. close': 'Close',
                             '5. adjusted close': 'Adj Close',
                             '6. volume': 'Volume', "8. split coefficient": "Split Coeff"})
                df['Date'] = pd.to_datetime(df['Date'])
                cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', 'Split Coeff']
                df[cols] = df[cols].astype(float)

                df = df.sort_values(by='Date', ascending=False)
                df = df.reset_index(drop=True)

            except:  # if this part fucks up then scrap it
                return None

            # get rid of the current date if it exists in the df
            now = datetime.now()
            if df['Date'].iloc[0] == pd.Timestamp(year=now.year, month=now.month, day=now.day, hour=0, minute=0,
                                                  second=0):
                df = df.iloc[1:]

            # tests for splits
            s = df['Split Coeff']
            if (s != 1).any():
                split_coeff = 1

                for i in df.index:
                    # print("itter: ",i)
                    # print("split coeff is:", split_coeff)
                    df.at[i, 'Open'] *= 1 / split_coeff
                    df.at[i, 'High'] *= 1 / split_coeff
                    df.at[i, 'Low'] *= 1 / split_coeff
                    df.at[i, 'Close'] *= 1 / split_coeff
                    cur_split_coeff = df.at[i, 'Split Coeff']
                    # print("current split coeff is: ",cur_split_coeff)

                    if cur_split_coeff != 1:
                        split_coeff = cur_split_coeff * split_coeff

                    # print("new value is: ", split_coeff)

                    df.at[i, 'Split Coeff'] = split_coeff
        else:
            df = None

        return df

    ##################################################
    # TOS = TOS_daily_data(ticker=ticker)
    # AV = alphavantage(ticker=ticker)

    # print('')

    funct_name = 'Hist Data'

    print('     ', funct_name)

    data = TOS_daily_data(ticker=ticker)

    if isinstance(data, pd.DataFrame):
        # print('using TOS')
        return {funct_name: {funct_name: data, 'ERRORS': []}}

    else:  # if alphavantage failed, try TOS
        # print('TOS fucked up, using AV')
        data = alphavantage(ticker=ticker)
        if isinstance(data, pd.DataFrame):
            return {funct_name: {funct_name: data, 'ERRORS': []}}

        else:  # if TOS failed, return None
            return {'Hist Data': {'Hist Data': None, 'ERRORS': ['Hist Data Not Working']}}

## CALCULATE DEPENDANT METRICS #################################################

def get_price_history_stats(stats_dict, close_perc='', HOD_trigger=''):
    """High History
    inputs:
    - ticker
    - date (YYYY-mm-dd)
    - number of days to calculate for
    - HOD trigger
    - close within x% of high
    - also has the option to input a dataframe

    outputs:
    - ratio of days over HOD trig to days that closed within x% of high

    **** NOTES *****
    intraday high time data feeds:
        IEX
    """

    daily_data = stats_dict['Hist Data']

    # if cant get the hist data then return everything as None
    if not isinstance(daily_data, pd.DataFrame):
        stats_dict['Held High Perc'] = None
        stats_dict['Avg Continuation'] = None
        stats_dict['Total Run Count'] = None
        stats_dict['VWavg Run'] = None

        return stats_dict

    now_date = datetime.today()
    now_date_str = now_date.strftime('%Y-%m-%d')
    now_date = datetime.strptime(now_date_str, '%Y-%m-%d')

    num_days = 500  # roughly 2 years

    if HOD_trigger == "":
        HOD_trigger = .2  # default is atleast 20% run to be counted

    if close_perc == "":
        close_perc = .4  # default is 40% close from high

    data = daily_data[0:num_days].copy()

    # if the current day is returned as part of the dataframe then delete it
    if data['Date'].iloc[0] == now_date:
        data = data.iloc[1:]

    # creates day 0 open to high % change column
    data['D0O_D0H_Chg'] = (data['High'] - data['Open']) / data['Open']

    # creates adj close column and offsets it for the D1C - D0H comparison
    data['Adj_close'] = data['Close'].shift(-1)

    # get day 1 close to day 0 high pct change
    data['D1C_D0H_Chg'] = (data['High'] - data['Adj_close']) / data['Adj_close']

    # gets highest % change between the two
    data["Max Run"] = data[["D1C_D0H_Chg", "D0O_D0H_Chg"]].max(axis=1)

    # total range on the day
    data['Range'] = data['High'] - data['Low']

    data['RangeSplit'] = data['Range'] * close_perc
    data['CloseFromeHigh'] = data['High'] - data['Close']

    # find total number of plays over HOD Triger
    D0O_D0H_runners = data.loc[(data['D0O_D0H_Chg'] >= HOD_trigger)]  # same day runners
    D1C_D0H_runners = data.loc[(data['D1C_D0H_Chg'] >= HOD_trigger)]  # runners including gap ups
    runners = D0O_D0H_runners.append(D1C_D0H_runners)
    runners = runners.drop_duplicates()
    runners = runners.reset_index()
    runners["index"] = runners["index"].astype(float)
    runners["Days From Now"] = (
            datetime.now() - pd.to_datetime(runners["Date"])).dt.days  # how many days ago the run day was

    # sums up total volume of all runners and puts it in the runners df
    vol_sum = runners["Volume"].sum()
    runners["Vol Sum"] = vol_sum

    # weights each run day by volume / total volume
    runners["Vol Weight"] = (runners["Volume"] / vol_sum) + 1

    # creates a recency metric by taking the square root of how many days ago the run occured
    runners["Days Sqrt"] = runners["Days From Now"] ** (1 / 2)
    runners["Recency Weight"] = runners["Days Sqrt"] / runners["Days From Now"]

    # a measure of how much volume and recency contributes to runners
    vwavg_run = (runners["Vol Weight"] * runners["Max Run"] * runners["Recency Weight"]).sum()

    # counts the total runners
    total_run_count = len(runners)

    # find runners that closed within 40% of highs (> RangeSplit)
    closed_up = len(runners.loc[runners['CloseFromeHigh'] < runners['RangeSplit']])

    try:
        held_high_perc = round((closed_up / total_run_count), 3)
    except ZeroDivisionError:
        held_high_perc = 0

    # looks at history of multi day runners
    runners = runners.sort_values('Date', ascending=False)
    day_one_moves = []  # stores index values of days that are considered day1 runners (no runners within a previous x day period)

    # retrieves a list of day one movers (big green candles that are atleast 6 days separated from other moves)
    x = 0
    while x < (total_run_count - 1):
        d1 = runners.index[x]
        d2 = runners.index[x + 1]
        if (d2 - d1) > 6:  # 6 days separated
            day_one_moves.append(d1)  # saves the index
        x += 1

    # gets the highest high after 7 days of the day 1 move
    day_one_move_changes = []
    for idx_val in day_one_moves:
        x = 1
        # D1H = runners.loc[idx_val][2]  # gets D1 high for comparison
        D1H = runners.loc[idx_val]['High']  # gets D1 high for comparison
        high_list = []

        while x <= 7:  # 7 is number of days to look forward to determine high after day 1
            high = data.loc[idx_val + x]['High']
            high_list.append(high)
            x += 1

        highest = max(high_list)

        change = (highest - D1H) / D1H
        day_one_move_changes.append(change)

    try:
        avg_continuation = round(sum(day_one_move_changes) / len(day_one_move_changes), 3)
    except ZeroDivisionError:
        avg_continuation = 0

    stats_dict['Held High Perc'] = held_high_perc
    stats_dict['Avg Continuation'] = avg_continuation
    stats_dict['Total Run Count'] = total_run_count
    stats_dict['VWavg Run'] = vwavg_run

    return stats_dict

def get_volume_stats(stats_dict, num_days='', premarket=bool):
    """
    uses:
    get rvol during trading day
    get rvol on trading day after hours
    get rvol on weekend during normal hours
    get rvol on weekend after hours

    **** NOTES *****

    """

    def find_intraday_vol_percent():
        now = datetime.now()

        last_open = datetime(now.year, now.month, now.day, hour=8, minute=30)

        minutes_passed = 5 * round(((now - last_open).seconds / 60) / 5)  # rounded to nearest 5 minutes

        df = pd.read_csv('Intraday_Vol.csv', delimiter='\t')
        return df.loc[df['Time_Passed'] == minutes_passed]['Percentage'].iloc[0]

    ##############################################################################

    daily_data = stats_dict['Hist Data']

    # if cant get the hist data then return everything as None
    if not isinstance(daily_data, pd.DataFrame) or premarket:
        stats_dict['Curr Rvol'] = None
        stats_dict['Time Adj Rvol'] = None
        stats_dict['Time Adj Vol'] = None
        stats_dict['Curr Vol Rank'] = None
        stats_dict['Time Adj Vol Rank'] = None
        stats_dict['Float Rotation'] = None
        stats_dict['Time Adj Float Rotation'] = None

        return stats_dict

    data = daily_data.copy()

    cur_vol = stats_dict['Curr Day Volume']

    # handles weekends (not necessary now)
    now = datetime.now()
    day = now.weekday()
    # if its a saturday or sunday
    weekend = False
    if helper_functions.is_weekend():
        weekend = True

    # find latest trading day
    if weekend:
        d = day - 4
        now = now - timedelta(days=d)

    # days to calculate RVOL for
    if num_days == '':
        num_days = 365

    data = data[0:num_days]

    # if its not the weekend and its before 3PM then do the time adjusted RVOL (if we're live)
    market_open = now.replace(hour=8, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=0, second=0, microsecond=0)
    # if its between 8:30 and 3:00 PM and not the weekend

    import operator

    # if its not the weekend and the market is currently open
    if not weekend and market_open < now < market_close:  # now < market_close and now > market_open

        perc = find_intraday_vol_percent()
        timestamp = now
        vol_avg = data['Volume'].mean(axis=0)

        cur_RVOL = round(cur_vol / vol_avg,4)

        time_adj_RVOL = cur_RVOL / perc
        time_adj_cur_vol = cur_vol / perc

        now_date = pd.Timestamp(year=now.year, month=now.month, day=now.day)

        # volume ranking for current volume
        date_volume_curr = dict(zip(data['Date'], data['Volume']))
        date_volume_curr[now_date] = cur_vol

        sorted_date_volume = sorted(date_volume_curr.items(), key=operator.itemgetter(1), reverse=True)
        vol_rank = [i for i, v in enumerate(sorted_date_volume) if v[0] == now_date][0] + 1

        # find volume ranking for time adj volume
        date_volume_time_adj = dict(zip(data['Date'], data['Volume']))
        date_volume_time_adj[now_date] = time_adj_cur_vol

        sorted_date_volume = sorted(date_volume_time_adj.items(), key=operator.itemgetter(1), reverse=True)
        time_adj_vol_rank = [i for i, v in enumerate(sorted_date_volume) if v[0] == now_date][0] + 1

    else:  # if it is the weekend or past 3PM/before 8:30AM (if market is not open)

        vol_avg = data.iloc[1:]['Volume'].mean(axis=0)

        cur_RVOL = cur_vol / vol_avg

        time_adj_RVOL = cur_RVOL
        time_adj_cur_vol = cur_vol

        # find volume ranking

        now_date = pd.Timestamp(year=now.year, month=now.month, day=now.day)

        date_volume = dict(zip(data['Date'], data['Volume']))

        date_volume[now_date] = cur_vol

        import operator
        sorted_date_volume = sorted(date_volume.items(), key=operator.itemgetter(1), reverse=True)

        vol_rank = time_adj_vol_rank = [i for i, v in enumerate(sorted_date_volume) if v[0] == now_date][0] + 1

    stats_dict['Curr Rvol'] = round(cur_RVOL, 3)
    stats_dict['Time Adj Rvol'] = round(time_adj_RVOL, 3)
    stats_dict['Time Adj Vol'] = time_adj_cur_vol
    stats_dict['Curr Vol Rank'] = vol_rank
    stats_dict['Time Adj Vol Rank'] = time_adj_vol_rank

    return stats_dict

def get_float_rotation(stats_dict, premarket=bool):
    if premarket:
        stats_dict['Float Rotation'] = None
        stats_dict['Time Adj Float Rotation'] = None
        return stats_dict

    try:
        stats_dict['Float Rotation'] = stats_dict['Curr Day Volume'] / stats_dict['Float']
    except:
        stats_dict['Float Rotation'] = None

    try:
        stats_dict['Time Adj Float Rotation'] = stats_dict['Time Adj Vol'] / stats_dict['Float']
    except:
        stats_dict['Time Adj Float Rotation'] = None

    return stats_dict


