import os
import math
from datetime import datetime
import datetime as dt
from pandas.tseries.offsets import BDay
import numpy as np
import create_report
import decimal
import data_sources
import helper_functions
import pickle
from tabulate import tabulate

decimal.getcontext().rounding = decimal.ROUND_UP

if "passwords" not in locals():
    passwords = helper_functions.get_pwds()

def get_data_for_tickers(use_proxies=False, from_desktop=False):

    def get_completed_tickers(folder_name):
        # folder name = 'text' or 'pickle'
        # looks through the date file directory and returns list of completed tickers

        now = datetime.now()
        date_folder = str(now.year) + '-' + str(now.month) + '-' + str(now.day)

        if folder_name == 'text' or folder_name == 'Text' or folder_name == 'txt':
            folder_name = 'Text_Dates'
        elif folder_name == 'pkl' or folder_name == 'pickle':
            folder_name = 'Pickle_Dates'

        directory = 'Stock_Notes/'+folder_name+'/' + date_folder
        ticker_list = []

        for filename in os.listdir(directory):
            if folder_name == 'Pickle_Dates' and filename.endswith(".pickle"):
                ticker_list.append(filename.split('.')[0])

            elif folder_name == 'Text_Dates' and filename.endswith(".txt"):
                ticker_list.append(filename.split('.')[0])

        return ticker_list

    def get_ticker_blacklist():
        with open('ticker_blacklist.txt', 'r') as infile:
            ticker_blacklist = infile.read()
            ticker_blacklist = ticker_blacklist.split('\n')
            ticker_blacklist = list(filter(lambda a: a != '', ticker_blacklist))  # removes blank spaces

        return ticker_blacklist

    def create_watchlist():

        file = open('returned_watchlist.txt', 'r')
        tickers = file.read()
        file.close()

        if not tickers:
            return []

        tickers = tickers.split('\n')

        tickers = list(filter(lambda a: a != '', tickers))  # removes blank spaces

        ticker_check_list = []

        for result in tickers:
            # result = result.split(' ')
            # result[1] = float(result[1])
            ticker_check_list.append(result)

        return ticker_check_list

    def get_ticker_input_list(from_desktop):

        def import_ticker_list_from_desktop(folder_name):
            # saves ticker list from desktop into the local ticker_input_list.txt file
            # is only if youre saving a watchlist from tradeideas to the desktop
            now = datetime.now().strftime('%Y-%m-%d')

            file = open('C:/Users/dlnbl/Desktop/' + now + '-WatchListScanner.csv', 'r')
            in_file = file.read()
            file.close()

            in_file = in_file.split('\n')
            del in_file[0:4]

            ticker_saved_list = []

            for row in in_file:
                row = row.split(',')
                ticker_saved_list.append(row[0])

            ticker_saved_list = list(filter(lambda a: a != '', ticker_saved_list))  # removes blank spaces

            file = open('ticker_input_list.txt', 'w')

            for i in ticker_saved_list:
                file.write(i + '\n')

            file.close()

        ###########################################################

        # if the ticker list is coming from the desktop (only applies if using tradeideas
        if from_desktop:
            import_ticker_list_from_desktop(folder_name=date_folder_name)

        # opens the local input list file and converts it to a list
        with open('ticker_input_list.txt', 'r') as infile:
            ticker_input_list = infile.read()
            ticker_input_list = ticker_input_list.split('\n')
            ticker_input_list = list(filter(lambda a: a != '', ticker_input_list))  # removes blank spaces

        # convert to uppercase and remove dups from ticker input list
        ticker_input_list = [ticker.upper() for ticker in ticker_input_list]
        ticker_input_list = list(set(ticker_input_list))
        return ticker_input_list

    def create_date_folder_name():
        # creates date folder name of the current business day or last business day if its the weekend
        now = datetime.now()
        if helper_functions.is_weekend():
            date_folder_name = str((now - BDay()).year) + '-' + str((now - BDay()).month) + '-' + str(
                (now - BDay()).day)
            print('IS WEEKEND GETTING INFO FOR DATE:')
        else:
            date_folder_name = str(now.year) + '-' + str(now.month) + '-' + str(now.day)

        return date_folder_name

    def create_directory_paths(date_folder_name):
        # creates directories for the pickle and text file paths
        pkl_directory = 'Stock_Notes/Pickle_Dates/' + date_folder_name
        txt_directory = 'Stock_Notes/Text_Dates/' + date_folder_name

        return [pkl_directory, txt_directory]

    def create_directories(pkl_directory,txt_directory):
        # create the pickle_date and text_date directories if it doesnt exist
        if not os.path.exists(pkl_directory):
            os.mkdir(pkl_directory)

        if not os.path.exists(txt_directory):
            os.mkdir(txt_directory)

    def create_text_file(report, txt_filepath):
        """prints out stats template with filled in values and then saves template to text file"""
        def to_str(value):
            if not value:
                return ' - '
            if isinstance(value, float) or isinstance(value, np.float):
                value = round(value, 2)
                value = '{:,}'.format(value)

            if isinstance(value, int):
                value = '{:,}'.format(value)

            return str(value)

        #######################################################

        general_info = [['Ticker',report['Ticker']],
                        ['Timestamp',to_str(report['Timestamp'])],
                        ['Comp Name',report['Comp Name']],
                        ['Industry',report['Industry']],
                        ['Sector',report['Sector']],
                        ['Exchange', report['Exchange']]]

        price_stats = [['Total Run Count',to_str(report['Total Run Count'])],
                       ['Held High Perc',to_str(report['Held High Perc'])],
                       ['VWavg Run',to_str(report['VWavg Run'])],
                       ['Avg Continuation',to_str(report['Avg Continuation'])]]

        volume_stats = [['Curr Vol',to_str(report['Curr Day Volume']),'Time Adj Curr Vol',to_str(report['Time Adj Vol'])],
                        ['Curr RVOL',to_str(report['Curr Rvol']),'Time Adj RVOL',to_str(report['Time Adj Rvol'])],
                        ['Curr Vol Rank',to_str(report['Curr Vol Rank']),'Time Adj Vol Rank',to_str(report['Time Adj Vol Rank'])],
                        ['Float Rotation',to_str(report['Float Rotation']),'Time Adj Float Rotation',to_str(report['Time Adj Float Rotation'])]]

        share_stats = [['Market Cap',to_str(report['Market Cap'])],
                       ['Shares Outstanding',to_str(report['Shares Outstanding'])],
                       ['Float',to_str(report['Float'])],
                       ['Short Float', to_str(report['Short Float'])],
                       ['Short Interest', to_str(report['Short Interest']),'Report Date',to_str(report['Report Date'])],
                       ['Prev Month Short Interest',to_str(report['Prev Month Short Interest']),'Prev Month Report Date',to_str(report['Prev Month Report Date'])]]

        financials = [['CASTI', to_str(report['CASTI'])],
                    ['Cash',to_str(report['Cash'])],
                    ['ST Debt',to_str(report['ST debt'])],
                    ['LT Debt', to_str(report['LT debt'])]]


        with open(txt_filepath, 'a') as file:
            print(tabulate(general_info, headers=['### GENERAL INFO -- Total Score:'+str(report['Total Score']),'']),file=file)
            print('',file=file)
            print(tabulate(price_stats, headers=['### PRICE STATS -- Score:'+str(report['Price Stats Score']), '']), file=file) #!!! insert score into here
            print('', file=file)
            print(tabulate(volume_stats, headers=['### VOLUME STATS -- Score:'+str(report['Volume Stats Score']),'','','']), file=file)  #!!! insert score into here
            print('', file=file)
            print(tabulate(share_stats, headers=['### SHARE STATS -- Score:'+str(report['Share Stats Score']), '', '', '']), file=file) #!!! insert score into here
            print('', file=file)
            print(tabulate(financials, headers=['### FINANCIALS', '', '', '']), file=file)
            print('',file=file)
            print('### NEWS HEADLINES', file=file)

            for hl in report['News Headlines']:
                #convert datetime to string
                hl[0] = datetime.strftime(hl[0], '%Y-%m-%d %H:%M:%S')
                print(hl,file=file)

            print('', file=file)
            print('', file=file)
            print('### ERRORS', file=file)
            for k,v in report['ERRORS'].items():
                print(k,v, file=file)

    def score(report):
        """
        scores all parts of the report
        price and volume
        share stats
        news
        """
        def price_stats_score(report):

            held_high_cutoff = .40
            total_runners_cutoff = 15

            # Held High Perc -------------------------------------
            # if report['Held High Perc'] <  held_high_cutoff:
            #     dont_trade_reasons.append("Cant hold highs")
            # if report['Held High Perc'] < held_high_cutoff and total_runners > total_runners_cutoff:
            #     dont_trade_reasons.append("Cant hold highs over large sample size")
            #
            # if report['Held High Perc'] > .4:
            #     do_trade_reasons.append("Holds highs")
            # if report['Held High Perc'] > .4 and total_runners > 20:
            #     do_trade_reasons.append("Holds highs over large sample size")

            HHP_score = (1 + report['Held High Perc']) ** 2  ###multiply by total runners score

            # TOTAL RUNNERS ------------------------------
            total_runners_score = math.sqrt(report['Total Run Count']) #take the square of total runners

            # if report['Total Run Count'] == 0:
            #     dont_trade_reasons.append("No previous runners")
            #
            # if report['Total Run Count'] >= 25:
            #     do_trade_reasons.append("Previous runners")

            # AVG CONTINUATION ---------------------------------
            if report['Avg Continuation'] > 0:
                # if report['Avg Continuation'] > .2:
                #     do_trade_reasons.append("History of day 2s")
                avg_continuation_score = 1 + report['Avg Continuation']

            elif report['Avg Continuation'] < 0:
                # if report['Avg Continuation'] < (-.25):
                #     dont_trade_reasons.append("Bad history of day 2s")
                avg_continuation_score = -1 + report['Avg Continuation']
            else: # if avg cont == 0
                avg_continuation_score = 0

            return round((total_runners_score * HHP_score) + avg_continuation_score,4)

        def volume_stats_score(report):

            # TIME ADJ RVOL -----------------------------------------

            # if report['Time Adj RVOL'] > 15:
            #     do_trade_reasons.append("High projected RVOL")
            # if report['Time Adj RVOL'] < 4:
            #     dont_trade_reasons.append("Low projected RVOL, no interest")

            TA_rvol_score = math.sqrt(report['Time Adj Rvol'])  # works with time adjusted RVOL

            # FLOAT ROTATION ---------------------------------
            if report['Time Adj Float Rotation'] < 1:
                #dont_trade_reasons.append("No projected float rotation")
                TA_float_rotation_score = 0

            elif report['Time Adj Float Rotation'] > 1:
                TA_float_rotation_score = (report['Time Adj Float Rotation'] / 2)

                # if report['Time Adj Float Rotation'] > 3:
                #     do_trade_reasons.append("Large projected float rotation")
            else:
                TA_float_rotation_score = 1

            # VOLUME RANK ---------------------------------------
            # reward if its in the top 5 on an exponential scale
            if report['Time Adj Vol Rank'] <= 5:
                vol_rank_score = math.sqrt(1+(100/report['Time Adj Vol Rank']))
            else:
                vol_rank_score = 1

            return  round((TA_rvol_score + TA_float_rotation_score) * vol_rank_score,4)

        def share_stats_score(report):

            # MARKET CAP --------------------------------------
            if report['Market Cap']:
                # if report['Market Cap'] < 70000000:
                #     do_trade_reasons.append("Low market cap")
                # if report['Market Cap'] > 650000000:
                #     dont_trade_reasons.append("High market cap")

                marketcap_score = math.sqrt(1 / math.sqrt(report['Market Cap']) * 18000) ** 3

                if marketcap_score < 1:
                    marketcap_score = 0

            else:
                marketcap_score = 0

            # SHARES OUTSTANDING ------------------------
            if report['Shares Outstanding']:
                sharesOutstanding_score = math.sqrt(1 / math.sqrt(report['Shares Outstanding']) * 65000)
            else:
                sharesOutstanding_score = 0

            # STOCK FLOAT -------------------------------------
            if report['Float']:
                stock_float_score = math.sqrt(1 / math.sqrt(report['Float']) * 65000) * 2
                # if report['Float'] < 12000000:
                #     do_trade_reasons.append("Low float")
                # if report['Float'] > 90000000:
                #     dont_trade_reasons.append("High float")
            else:
                stock_float_score = 0

            if report['Short Float']:

                short_float_cutoff = .055

                # if report['Short Float'] > short_float_cutoff:
                #     do_trade_reasons.append("High short % float")
                # if report['Short Float'] > short_float_cutoff and report['Short Interest'] > (.3 * curr_volume):
                #     do_trade_reasons.append("High short % current vol")

                shortPercfloat_score = (1 + report['Short Float']) ** 3
            else:
                stock_float_score = shortPercfloat_score = 0

            return round((stock_float_score * shortPercfloat_score) + sharesOutstanding_score +
                         (stock_float_score - sharesOutstanding_score) + marketcap_score, 4)

        def news_score(report):
            # !!! NOT DONE, NEED TO SORT OUT RETURN VALUES FOR THE MULTIPLE HEADLINES IT PUTS IN
            def find_consec_index_vals(idx_list):
                """inputs index list and return nested list of all consecutive indexes"""

                consec_number_lists = []
                consec_number_list = []

                idx_list.sort()

                y = 0
                while y < len(idx_list):
                    num1 = idx_list[y]
                    try:  # if num2 index is out of bounds
                        num2 = idx_list[y + 1]
                    except:
                        consec_number_list.append(num1)

                        if len(consec_number_list) > 1:
                            consec_number_lists.append(consec_number_list)
                        break
                    # print('--------------------------')
                    # print(num1,num2)

                    # if the two numbers are consecutive
                    if (num1 + 1) == num2:
                        consec_number_list.append(num1)

                    # if the two numbers are not consecutive
                    else:
                        consec_number_list.append(num1)

                        if len(consec_number_list) > 1:
                            consec_number_lists.append(consec_number_list)

                        consec_number_list = []

                    # print(consec_number_list)
                    y += 1

                # print(consec_number_lists)
                return consec_number_lists

            ##########################################################

            keyword_list = ['announces', 'announced', 'announce', 'reports', 'reported', 'report', 'recieves', 'files',
                            'analyst',
                            'enters', 'into', 'present', 'signs', 'secured', 'secure', 'secures', 'first', 'quarter',
                            'second', 'third',
                            'fourth', 'q1', 'q2', 'q3', 'q4', 'earnings', 'transcript', 'financial', 'results',
                            'snapshot', 'outlook',
                            'conference', 'call', 'guidance', 'beat', 'beats', 'revenue', 'business', 'update', 'sales',
                            'eps', 'new',
                            'data', 'clinical', 'trial', 'positive', 'fda', 'clearance', 'approval', 'fast', 'track',
                            'orphan',
                            'topline', 'phase', 'ii', '2,', 'i', '1', 'meeting', 'designation', 'upcoming', 'investor',
                            'presented',
                            'presents', 'annual', 'host', 'partnership', 'collaboration', 'partners', 'collaborates',
                            'collab',
                            'collaborate', 'contract', 'contracts', 'order', 'orders', 'award', 'awarded', 'received',
                            'purchase',
                            'price', 'target', 'raised', 'raises', 'analysts', 'upgrade', 'upgrades', 'upgraded',
                            'overweight',
                            'neutral', 'underweight', 'buy', 'financing', 'registered', 'direct', 'offering', 'priced',
                            'market',
                            'common', 'stock', 'share', 'shares', 'public']

            connector_keywords = ["at", "to", "be", "with", "from", "and", "of", "in", 'the', 'a']

            preface_keywords = ["announces", "announced", "announce", "reports", "reported" "to report", "recieves",
                                "files", "analyst", "enters into",
                                "to present", "signs", "secured", "secure", "secures"]

            headline_keywords = {
                "Earnings": ["first quarter", "second quarter", "third quarter", "fourth quarter", "q1", "q2",
                             "q3", "q4", "earnings", "transcript", "financial results", "snapshot", "outlook",
                             "conference call", "guidance", "quarter financial results",
                             "beat", "beats", "reports", "revenue", "business update", "sales", "eps"],

                "Trials/New Product": ["new data", "clinical data", "clinical trial", "trial",
                                       "results", "positive", "fda", "clearance", "approval", "fast track", "orphan",
                                       "topline",
                                       "phase ii", "phase 2, phase i", "phase 1", "meeting", "designation"],

                "Conference": ["upcoming", "conference", "investor conference", "to be presented", "to present",
                               "presents",
                               "to present at", "annual", "to host"],

                "Partnership News": ["partnership", "a partnership", "collaboration", "a collaboration",
                                     "partners with", "collaborates", "collab",
                                     "collaborate"],

                "Contract News": ["contract", "contracts", "order", "orders", "contract award", "awarded",
                                  "received purchase"],

                "Analyst Upgrade": ["price target raised", "raises price target", "raises target", "analysts upgrade",
                                    "price target", "upgrade", "upgrades", "upgraded",
                                    "to overweight", "from neutral to overweight", "from underweight to overweight",
                                    "to buy"],

                "Financing": ["in financing", "financing", "registered direct offering", "priced", "at the market",
                              "common stock offering",
                              'share', 'shares', "public offering of common", 'offering of common', 'registered direct',
                              'common stock']
            }

            # append the preface words to each catalyst
            for catalyst in headline_keywords.keys():
                headline_keywords[catalyst] += preface_keywords

            print('----------------------------------------------------------------------------')
            print(report['Ticker'])

            # loop through headlines
            for news in report['News Headlines']:
                headline = news[1].lower()
                print('headline: ', headline)
                # get rid of any fucky symbols
                headline = headline.replace(',', '')
                headline = headline.replace('.', '')
                headline = headline.replace('?', '')
                headline = headline.replace('!', '')
                headline = headline.replace('-', ' ')
                headline = headline.split(' ')

                date = news[0]

                found_keywords = []
                # loop through keyword list and look for keywords in headline
                for keyword in keyword_list:
                    if keyword in headline:
                        # print('   ',keyword)
                        found_keywords.append(keyword)

                ret_val = []
                # if theres 3 or more keywords found in the headline, look to build phrases
                if len(found_keywords) >= 3:
                    print('--- found keywords', found_keywords)
                    #####################################
                    ## BUILD PHRASES ####################
                    #####################################

                    index_vals = []
                    # collect the indexes of all keywords
                    for word in found_keywords:
                        index_vals.append(headline.index(word))

                    # find indexes of any existing connector words
                    for word in connector_keywords:
                        if word in headline:
                            index_vals.append(headline.index(word))

                    print('--- index vals', index_vals)

                    # get consecutive index values (returns nested list)
                    consec_index_vals = find_consec_index_vals(idx_list=index_vals)

                    print('--- consec idx vals', consec_index_vals)

                    # if theres no phrases, bail
                    if not consec_index_vals:
                        continue

                    # build phrases based on index values
                    phrases = []
                    for vals_list in consec_index_vals:
                        phrase = []
                        for val in vals_list:
                            phrase.append(headline[val])

                        phrases.append(phrase)

                    print('--- phrases', phrases)

                    # populate the count_dict with the catalysts and assign counter
                    count_dict = {}
                    for catalyst in headline_keywords.keys():
                        count_dict[catalyst] = []

                    # form the target headline phrase to test with catalyst keywords/phrases
                    for words in phrases:
                        sentence = ' '.join(words)
                        print('--- sentence', sentence)

                        for catalyst, keywords, in headline_keywords.items():
                            for keyword in keywords:
                                if keyword in sentence:
                                    count_dict[catalyst].append(keyword)

                    # go through count_dict and find the longest value(s) list
                    print(count_dict)

                    longest = []
                    for catalyst, phrase_list in count_dict.items():
                        # print('---------------------------------------------')
                        # print('     catalyst:', catalyst)
                        # print('     phrase list:', phrase_list)
                        if not longest:
                            if len(phrase_list) > 0:
                                longest.append([catalyst, phrase_list])
                                # print('  creating longest')

                        elif len(phrase_list) > len(longest[0][1]):
                            longest[0] = [catalyst, phrase_list]
                            # print('  phrase longer than longest')

                        elif len(phrase_list) == len(longest[0][1]):
                            longest.append([catalyst, phrase_list])
                            # print('  phrase lenght = to longest length')

                        # print(' longest list so far', longest)
                        # print('')

                    # assign catalyst

                    ret_val = []
                    if not longest:
                        pass
                    elif len(longest) == 1:
                        ret_val = longest[0][0]
                    elif len(longest) > 1:
                        for c in longest:
                            ret_val.append(c[0])

            return ret_val

        ##################################################
        # only calculate the price and vol score if its not premarket
        # if its premarket only calculate the share stats score

        # do_trade = []
        # dont_trade = []

        report['Price Stats Score'] = None
        report['Volume Stats Score'] = None
        report['Share Stats Score'] = None
        report['News Score'] = None
        report['Total Score'] = None

        if helper_functions.is_premarket():
            report['Price Stats Score'] = price_stats_score(report=report)
            report['Share Stats Score'] = share_stats_score(report=report)
            # report['News Score'] = news_score(report=report)
            report['Total Score'] = 'NA'

            return report

        else:
            report['Price Stats Score'] = price_stats_score(report=report)
            report['Volume Stats Score'] = volume_stats_score(report=report)
            report['Share Stats Score'] = share_stats_score(report=report)
            #report['News Score'] = news_score(report=report)

            report['Total Score'] = round(report['Price Stats Score'] + report['Volume Stats Score']\
                                    + report['Share Stats Score'],4) #+ report['News Score']

        return report

    def update_premarket_scans(use_proxies=False):
        """updates scans done premarket to update the stats that cant be calculated while in premarket"""

        print('')
        print('updating scans done premarket...')

        # if its at least 15 minutes past the market open get the volume stats for tickers ran in premarket
        now = datetime.now()
        market_open = dt.datetime(year=now.year, month=now.month, day=now.day, hour=8, minute=30)

        none_found = True

        if now > market_open:
            # loop through pickle dates folder for current day
            date_folder_name = str(now.year) + '-' + str(now.month) + '-' + str(now.day)

            pkl_directory = 'Stock_Notes/Pickle_Dates/' + date_folder_name
            txt_directory = 'Stock_Notes/Text_Dates/' + date_folder_name

            scanned_tickers = get_completed_tickers(folder_name='pkl')

            for ticker in scanned_tickers:
                pkl_filepath = pkl_directory + "/" + ticker + ".pickle"
                txt_filepath = txt_directory + "/" + ticker + ".txt"

                with open(pkl_filepath, "rb") as data:
                    report = pickle.load(data)

                # if the report was made on the weekend then continue
                if report['Timestamp'] == 'Weekend':
                    continue

                # if the last timestamp was before market open
                if report['Timestamp'] < market_open:
                    print('     ',ticker)

                    none_found = False

                    # update the volume info
                    report['Timestamp'] = datetime.now()
                    report['Curr Day Volume'] = data_sources.get_curr_day_volume(ticker=ticker,use_proxies=use_proxies)

                    report = data_sources.get_volume_stats(stats_dict=report, premarket=premarket)
                    report = data_sources.get_float_rotation(stats_dict=report, premarket=premarket)

                    report = score(report=report)

                    # write to text file
                    create_text_file(report=report, txt_filepath=txt_filepath)

                    # write to the file
                    with open(pkl_filepath, 'wb') as data:
                        pickle.dump(report, data)

        if none_found:
            print('None found')

    def remove_bad_tickers(input_list):

        ret_list = []

        for ticker in input_list:

            ticker = ticker.upper()

            # FILTER OUT BAD TICKERS
            if len(ticker) >= 5:
                continue

            # if the tickers is in a blacklist skip it
            if ticker in ticker_blacklist:
                continue

            ret_list.append(ticker)

        return ret_list

    ##########################################################

    data_sources.check_subscriptions()

    # test if its the weekend or premarket
    weekend = helper_functions.is_weekend()
    premarket = helper_functions.is_premarket()

    # establish the time of the week/day
    if weekend:
        # if its the weekend you dont want to collect data for today, it need to be from the last business day
        print('--------- IS WEEKEND ----------')
    elif premarket:
        print('--------- IS PREMARKET ----------')

    date_folder_name = create_date_folder_name()

    pkl_directory_path, txt_directory_path = create_directory_paths(date_folder_name=date_folder_name)

    create_directories(pkl_directory=pkl_directory_path, txt_directory=txt_directory_path)

    # gets the list of tickers that are either blank or dont play nice with the system
    ticker_blacklist = get_ticker_blacklist()

    # gets input list either from desktop or manual input
    ticker_input_list = get_ticker_input_list(from_desktop=from_desktop)

    # gets rid of the bad tickers and blacklist tickers
    ticker_input_list = remove_bad_tickers(input_list=ticker_input_list)

    # gets list of already completed tickers in pickle dates for that day
    completed_pickle_list = get_completed_tickers(folder_name='pickle')

    # gets list of already completed tickers in text dates for that day
    completed_text_list = get_completed_tickers(folder_name='text')

    # loops through the input list
    for ticker in ticker_input_list:

        # create text and pickle filepath for each ticker
        pkl_filepath = pkl_directory_path + "/" + ticker + ".pickle"
        txt_filepath = txt_directory_path + "/" + ticker + ".txt"

        print(ticker, ' ', end='', flush=True)

        # if ticker does not exist in completed_ticker_list -> create report
        if ticker not in completed_pickle_list:

            timer_start = datetime.now() # records how long the report takes

            # create the report for that ticker
            report = create_report.create_report(ticker=ticker, use_proxies=use_proxies, premarket=premarket, weekend=weekend)

            # score the report
            report = score(report=report)

            print((datetime.now()-timer_start).total_seconds(),' secs') # records how long the report takes

            # write the report results to a pickle file
            with open(pkl_filepath, 'wb') as data:
                pickle.dump(report, data)

                # create a text file for viewing
            create_text_file(report=report,txt_filepath=txt_filepath)

        # if ticker exists in the pickle dates but not the text dates create the report
        elif ticker in completed_pickle_list and ticker not in completed_text_list:
            print('ticker in pickle list but not text list')
            with open(pkl_filepath, 'rb') as data:
                report = pickle.load(data)

            create_text_file(report=report, txt_filepath=txt_filepath)

        else:
            print('[c]')

    update_premarket_scans(use_proxies=use_proxies)

get_data_for_tickers(use_proxies=False, from_desktop=False)

