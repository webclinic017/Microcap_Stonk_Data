import concurrent.futures
import data_sources
from datetime import datetime, timedelta
import pandas as pd
import decimal
import helper_functions
decimal.getcontext().rounding = decimal.ROUND_UP

if "passwords" not in locals():
    passwords = helper_functions.get_pwds()

## CLEAN AND ORGANIZE DATA ######################################
def clean_data(result_list):
    """
    creates and populates stats_dict where all stats will be stored
    """

    stats_dict = {}
    error_report = {}

    # rearranges stats to group by stat name: {source: stat}
    for result_dict in result_list:
        for data_source, stats in result_dict.items():
            for stat_name, stat_val in stats.items():

                # filter the errors into the error report dict
                if stat_name == 'ERRORS':
                    if stat_val:
                        error_report[data_source] = stat_val
                    continue

                # print('   ', stat_name, stat_val)
                # if the stat name doesnt yet exist in the dict
                if stat_name not in stats_dict.keys():

                    # handles dataframes
                    if isinstance(stat_val, pd.DataFrame):
                        stats_dict[stat_name] = {data_source: stat_val}

                    elif not stat_val:
                        stats_dict[stat_name] = {}
                    else:
                        stats_dict[stat_name] = {data_source: stat_val}

                # if the stat name does exist in the dict
                else:
                    if not stat_val:
                        continue
                    else:
                        stats_dict[stat_name].update({data_source: stat_val})

    stats_dict['ERRORS'] = error_report
    return stats_dict

def organize_data(stats_dict):
    # declare final stats dict
    final_stat_dict = {}

    # if theres any errors add them to the final stat dict
    try:
        final_stat_dict = {'ERRORS': stats_dict['ERRORS']}
    except:
        pass

    del stats_dict['ERRORS']

    # combine the assigned and calculated short float values into a single dict
    short_float_vals = {}
    for dictionary in [stats_dict['Assigned Short Float'], stats_dict['Calculated Short Float']]:
        x = 1
        for val in dictionary.values():
            short_float_vals[str(x)] = val
            x += 1

    # add short float to stats dict
    stats_dict['Short Float'] = short_float_vals

    # get rid of assigned and calculated short float dicts
    del stats_dict['Assigned Short Float']
    del stats_dict['Calculated Short Float']

    # stats from multiple sources that need to be averaged
    avgd_stats = ['Market Cap', 'Float', 'Short Interest', 'Shares Outstanding', 'Curr Day Volume',
                  'Prev Month Short Interest']

    # loop through stats dict with stat name and the corresponding dictionary
    for stat, nested_stat_dict in stats_dict.items():
        # if the stat needs to be averaged do it
        if stat in avgd_stats:
            try:
                value_list = list(nested_stat_dict.values())
                # run through averaging algo
                final_stat_dict[stat] = int(helper_functions.numeric_stats_weighted_avg(value_list=value_list))
            except:
                final_stat_dict[stat] = None
        # otherwise just take the first occurence

        elif stat == 'News Headlines':  # combine the news lists and filter
            news_list = []
            for headlines in nested_stat_dict.values():
                for headline in headlines:
                    # print('headline', headline)
                    news_list.append(headline)

            # Sort news and cut off anything older than 2 days ago
            news_list = sorted(news_list, key=lambda t: t[0], reverse=True)
            sorted_news_list = []
            cutoff = datetime.now() - timedelta(days=2)

            for headline in news_list:
                if headline[0] > cutoff:
                    sorted_news_list.append(headline)

            final_stat_dict[stat] = sorted_news_list

        else:  # if not news or in the average list -> take the first instance of the stat
            try:
                final_stat_dict[stat] = list(nested_stat_dict.values())[0]
            except:
                final_stat_dict[stat] = None

    return final_stat_dict

## BUILD THE REPORT #################################################
def create_report(ticker, use_proxies=False, premarket=bool, weekend=bool):
    """
    creates a report for an individual ticker from several data sources
    """
    ###############################################################################
    ## main program
    ###############################################################################

    # get_historical_data(ticker=ticker) #!!!
    # print()

    result_list = []

    if premarket:
        # run all functions except the ones to explicity get current day volume and save the results
        funct_list = [data_sources.polygon_ticker_details, data_sources.iex_stock_stats, data_sources.iex_stock_company_info,
                      data_sources.marketwatch_overview, data_sources.benzinga_news, data_sources.yahoo_API, data_sources.shortsqueeze,
                      data_sources.get_historical_data, data_sources.TOS_fundamentals, data_sources.marketwatch_financials]

    else:
        # run all the functions in the function list and save the results
        funct_list = [data_sources.polygon_ticker_details, data_sources.iex_stock_stats, data_sources.iex_stock_company_info,
                      data_sources.marketwatch_overview, data_sources.finviz, data_sources.get_curr_day_volume,
                      data_sources.benzinga_news, data_sources.yahoo_API, data_sources.shortsqueeze,data_sources.get_historical_data,
                      data_sources.TOS_fundamentals, data_sources.marketwatch_financials]

    # start threads and loop through function list
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(funct,ticker,use_proxies) for funct in funct_list]

        for f in concurrent.futures.as_completed(results):
            result_list.append(f.result())

    # clean and organize the data
    stats_dict = clean_data(result_list=result_list)
    final_stat_dict = organize_data(stats_dict=stats_dict)

    # get the price history stats
    final_stat_dict = data_sources.get_price_history_stats(stats_dict=final_stat_dict)

    # if its not premarket then calculate volume stats and float rotation
    if not premarket:
        final_stat_dict = data_sources.get_volume_stats(stats_dict=final_stat_dict, premarket=premarket)
        final_stat_dict = data_sources.get_float_rotation(stats_dict=final_stat_dict, premarket=premarket)

    # assign ticker
    final_stat_dict['Ticker'] = ticker

    # assign timestamp
    if weekend:
        final_stat_dict['Timestamp'] = "Weekend"
    else:
        final_stat_dict['Timestamp'] = datetime.now()

    # if metric was unable to get because is premarket then mark
    if premarket:

        # list of metrics unable to get in premarket
        non_premarket_list = ['Curr Day Volume','Time Adj Vol','Curr Rvol','Curr Vol Rank','Float Rotation',
                          'Time Adj Curr Vol','Time Adj Rvol','Time Adj Vol Rank','Volume Stats Score',
                          'Float Rotation','Time Adj Float Rotation']

        for i in non_premarket_list:
            final_stat_dict[i] = 'IS PREMARKET'

    return final_stat_dict





