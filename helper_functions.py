from datetime import datetime,timedelta

import pandas as pd
import requests
import os
from user_agent import generate_user_agent


## Helper Functions ###############################################
def is_weekend():
    day = datetime.now().weekday()
    weekend = False
    if day == 5 or day == 6:
        weekend = True
    return weekend

def is_premarket():

    now = datetime.now()
    premarket = False
    #market_open = str(int(dt.datetime(year=now.year, month=now.month, day=now.day, hour=8, minute=30).timestamp() * 1000))
    market_open = datetime(year=now.year, month=now.month, day=now.day, hour=8, minute=30)
    if now < market_open:
        premarket = True

    return premarket

def do_error_msg(msg, *details):
    spacer = '-----------------------------------------------------------------------------------------'
    print(spacer)
    print('ERROR: '+msg)
    for detail in details:
        print('     ',detail)
    print(spacer)

def run_request(url, use_proxy=False, header=None, timeout=5):

    ############################################################

    response = None

    if not header:
        headers = {'User-Agent': generate_user_agent()}

    if use_proxy:
        passwords = get_pwds()

        proxybot_key = passwords['proxy_bot_key']
        proxybot_API_url = "https://proxybot.io/api/v1/" + proxybot_key + "?url=" + url + "&custom_headers=true"

        try:  # try the proxy bot
            response = requests.get(proxybot_API_url, headers=headers, timeout=15)
        except:  # try with your own IP
            try:
                response = requests.get(url=url, headers=headers, timeout=7)
            except:
                # print(funct_name, '/proxybot(X)', end="", flush=True)
                do_error_msg('PROBLEM GETTING REQUEST',url)

    # dont use a proxy
    else:
        try:
            response = requests.get(url=url, headers=headers, timeout=timeout)
        except:
            do_error_msg('PROBLEM GETTING REQUEST', url)

    # if there was a response but the status code != 200 -> set response to None
    if response:
        if response.status_code != 200:
            do_error_msg('PROBLEM GETTING REQUEST', url,'response code: '+str(response.status_code))

    return response

def check_for_zeroes(input):
    if not input:
        output = None
    else:
        output = input
    return output

def string_num_converter(value, convert_to=''):
    if value == '-' or value == '' or value == None or value == 'N/A':  # or math.isnan(string) == True:
        return None

    if convert_to == 'num':
        # convert string to number
        multipliers = {'K': 1000, 'k': 1000, 'M': 1000000, 'm': 1000000,
                       'B': 1000000000, 'b': 1000000000, 'T': 1000000000000, 't': 1000000000000}

        # # check if getting passed an integer or float
        # test = isinstance(value, (int, float))
        # if test == True:
        #     return value

        # gets rid of unwanted characters
        char_set = [' ', '$', ',']
        for char in char_set:
            if char in value:
                value = value.replace(char, '')

        # check if value is a percentage
        if value[-1] == '%':
            value = value.replace('%', '')
            value = float(value) / 100.00
            return value

        # check if theres a suffix at the end i.e (5.89M, 600K, ect)
        if value[-1].isalpha():
            mult = multipliers[value[-1]]  # look up suffix to get multiplier
            value = int(float(value[:-1]) * mult)  # convert number to float, multiply by multiplier, then make int
            return value

        # else if theres nothing else that needs to be done return string as number
        else:
            value = float(value)
            if value % 1 == 0:
                return int(value)
            else:
                return value

    if convert_to == 'str':  # convert number to string
        # if the number isn't a percentage
        if value >= 1:
            value = '{:,}'.format(value)
            return value

        if value < 1 and value > -1:
            value = str(round((value * 100), 2)) + '%'
            return value

def numeric_stats_weighted_avg(value_list):
    # inputs a list of numeric values to average

    # if all the items in the list are the same
    if all(x == value_list[0] for x in value_list):
        avg = value_list[0]
        return avg

    # if theres 3 or more unique items stored in the value list
    if len(value_list) >= 3:
        avg_dict = {}

        for num1 in value_list:  # loops through populated value list
            row = []
            for num2 in value_list:  # loops through populated value list again
                # if num2 == num1:
                if value_list.index(num1) == value_list.index(num2) and num1 == num2:
                    continue

                diff = 100 / (abs(num1 - num2))
                row.append(diff)

            row_sum = sum(row)
            avg_dict.update({num1: row_sum})  # sums all proximity measures

        val_sum = sum(avg_dict.values())

        # sums together the weighted avgs
        avg = 0
        for k, v in avg_dict.items():
            try:
                avg += (k * (v / val_sum))
            except ZeroDivisionError:
                avg += 0
        return avg

    if len(value_list) == 2:  # just do regular average of
        avg = (value_list[0] + value_list[1]) / 2
        return avg

def get_pwds():
    from configparser import ConfigParser

    file = 'passwords.ini'
    config = ConfigParser()
    config.read(file)

    pwd_dict = {}
    for i in config['info'].items():
        pwd_dict[i[0]] = i[1]

    return pwd_dict

def change_pwds(change_dict):
    from configparser import ConfigParser

    file = 'passwords.ini'
    config = ConfigParser()
    config.read(file)

    # create a quick copy of the file in case something goes wrong while writing to it
    original = 'passwords.ini'
    target = 'passwords_copy.ini'
    os.system('copy '+original+' '+target)

    # rename the entry values
    for entry,value in change_dict.items():
        config.set('info',entry,str(value))

    try:
        with open(file, 'w') as f:
            config.write(f)
        # removes the copy
        os.remove(target)
        print('UPDATED PASSWORD INFO')
    except:
        # removes the original
        os.remove(original)

        do_error_msg('DIDNT SAVE PASSWORD CHANGES')
        # renames the copy to the original name
        os.rename(target,original)
