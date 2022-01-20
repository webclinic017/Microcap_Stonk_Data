# Microcap_Stonk_Data
## Usage
This is meant to be used on an intraday basis for day trading microcap stocks experiencing abnormal volatility (>20% intraday). This is extremely helpful when 
decisions need to be made as quickly as possible and theres no time to go sifting through multiple different websites for contradicting/absent data. 
The program gets, processes, scores, and records various data from various sources for the purpose of facilitating intraday trading for microcap stocks

## Operation
fill in ticker input_list.txt with tickers youre interested in
or create a csv file of scans from trade ideas
run get_data_for_tickers (if tickers are imported from the desktop csv file selected from_desktop = True)
pulls data from
	- TOS
	- polygon
	- iex
	- benzinga
	- marketwatch.com
	- finviz.com
	- yahoo finance
	- shortsqueeze.com
	- alphavantage
compiles all data into a dict
	- prints out data into a readable format
	- saves formated data to a text file
	- saves dict to a pickle file
  
  ## Metrics Pulled/Calculated
  ### General Info
  - Ticker
  - Timestamp
  - Company Name
  - Industry and Sector
  - Exchange
  
  ### Price Stats
  - Total Run Count: how many times in the past 500 days did the stock get above 20% in one day
  - Held High Percentage: in the last 500 trading days, how many days had over a 20% gain that also closed within 40% of its highs (does the stock have a history of holding its highs)
  - VWavg Run: volume weighted average run, measure of how much volume and recency are likely to impact the current runner.
  - Avg Continuation: gets a list of day one runners (runners are separated by at least 6 days) and gets the average distance between the day 1 high and the next 7 day high (does the stock have a history of multiday runners)
  
  ### Volume Stats
  - Curr Vol: current total volume for the day at the given timestamp
  - Time Adj Curr Vol: takes current day volume and extrapolates it to what it is likely to be at the end of the day using aggregate volume trends
  - Curr RVOL: current volume relative to historical volume
  - Time Adj Rvol: takes current day relative volume and extrapolates it to what it is likely to be at the end of the day using aggregate volume trends
  - Curr Vol Rank: takes the current volume and ranks it compared to large volume days in the last 500 trading days
  - Time Adj Vol Rank: rank of the projected time adj curr volume compared to volumes recorded in the last 500 days
  - Float Rotation: (Curr Vol/Float), measures how many times the float has changed hands in the day
  - Time Adj Float Rotation: (Time Adj Curr Vol/Float) extrapolates current day volume to end of day and the calculates float rotation based on that number
  
  ### Share Stats
  - Market Cap:
  - Shares Outstanding:
  - Float:
  - Short Float: percentage of float held short
  - Short Interest: total number of shares short as of Report Date
  - Report Date: last report date for short interest
  - Prev Month Short Interest: total number of shares short the previous month
  - Prev Month Report Date: report date for prev month short interest
  
  ### Financials
  - CASTI: cash and short term investments
  - Cash:
  - ST Debt: Short Term Debt
  - LT Debt: Long Term Debt
  
  ### News Headlines
  - [date, headline, link to headline]
  
  ### Errors
  - {source name: [list of any errors that occured with that source]}
  
  ### Score
  - does have a scoring system for price, volume, and share stats, although only displays total stats
  - kind of up in the air at the moment
  
  
