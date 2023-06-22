from datetime import datetime, timedelta
from dateutil.relativedelta import *
import pandas as pd

# generate datetime field in past rides csv, from given month and start time of ride
rides = pd.read_csv('past_rides.csv')
rides['start_datetime'] = pd.to_datetime(rides['date'] + ' ' + rides['start_time'], format='%B %d, %Y %I:%M %p').dt.floor('H')
rides['end_datetime'] = pd.to_datetime(rides['date'] + ' ' + rides['end_time'], format='%B %d, %Y %I:%M %p').dt.floor('H')

# if start time has PM and end time has AM (rode into the next day), add 1 day to end time
for i in range(len(rides)):
    if 'PM' in rides['start_time'].iloc[i] and 'AM' in rides['end_time'].iloc[i]:
        rides.loc[i, 'end_datetime'] += timedelta(days=1)

# create a hacky foreign key to match up rides based on start/end locs and times (rounded down to nearest hour)
rides['hacky_key'] = rides['start_datetime'].astype(str) + rides['end_datetime'].astype(str) + rides['start_loc'] + rides['end_loc']

# iterate through 05/21 to 05/23 and open up respective csv, match up respective ride
monthly_dfs = []
curr_date = datetime(2021, 5, 1)
end_date = datetime(2023, 6, 1)
while curr_date < end_date:
    month, year = curr_date.month, curr_date.year
    # isolate personal rides from a specific month
    month_rides = rides[(rides['start_datetime'].dt.month == month) & (rides['start_datetime'].dt.year == year)]

    # get csv for baywheels rides from specific month
    baywheels = pd.read_csv('data/{year}{month}-baywheels-tripdata.csv'.format(year=year, month=str(month).zfill(2)))
    baywheels['start_datetime'] = pd.to_datetime(baywheels['started_at'])
    baywheels['end_datetime'] = pd.to_datetime(baywheels['ended_at'])
    baywheels['hacky_key'] = baywheels['start_datetime'].dt.floor('H').astype(str) + baywheels['end_datetime'].dt.floor('H').astype(str) + baywheels['start_station_name'] + baywheels['end_station_name']

    # left merge by hacky key
    monthly_dfs.append(month_rides.merge(baywheels, how='left', on='hacky_key'))

    curr_date += relativedelta(months=1)

# save csv
pd.concat(monthly_dfs).to_csv('merged.csv')