import os
import json
from matplotlib import pyplot as plt
import matplotlib.dates as dates
import datetime
from typing import List, Dict
from collections import Counter
import math
from typing import NamedTuple
import csv
from scipy import stats

#Class for Fitbit sleep event
class SleepEvent(NamedTuple):
    log_id: int
    hours_asleep: float
    start_time: datetime.datetime
    stop_time: datetime.datetime

#Class for day weather
class DayWeather(NamedTuple):
    date: datetime.date
    temp_max: float
    temp_min: float

#Class for Day
class Day(NamedTuple):
    date: datetime.date
    hours_asleep: float
    temp_max: float
    temp_min: float


fitbit_directory_name = "LukeKippenbrock/user-site-export"
fitbit_directory = os.fsencode(fitbit_directory_name)

#Trying out code to produce dates in a specified range...
'''date1 = datetime.date(2016, 12, 20)
date2 = datetime.date(2016, 12, 30)
mydates = []
while date1<=date2:
    mydates.append(date1)
    date1 += datetime.timedelta(days=1)
for x in mydates: print(x)'''

#Get sleep data from Fitbit directory
sleep_list = []
for file in os.listdir(fitbit_directory):
     filename = os.fsdecode(file)
     log_name = "sleep" 
     if log_name in filename:
        filename_with_directory = f"{fitbit_directory_name}/{filename}"
        with open(filename_with_directory,"r") as f:
            data = f.read()
            obj = json.loads(data)
            for sleep_event in obj:
                #if (sleep_event["type"] != "stages"): continue
                hours_asleep = sleep_event["minutesAsleep"]/60 #Get hours asleep
                string_start_time = sleep_event["startTime"] #Get date in string format
                string_stop_time = sleep_event["endTime"] #Get date in string format
                start_time = datetime.datetime.strptime(string_start_time,'%Y-%m-%dT%H:%M:%S.000') #Convert to datetime format
                stop_time = datetime.datetime.strptime(string_stop_time,'%Y-%m-%dT%H:%M:%S.000') #Convert to datetime format
                log_id = sleep_event["logId"] #Get log id
                sleep_event = SleepEvent(log_id, hours_asleep, start_time, stop_time)
                sleep_list.append(sleep_event)

sleep_list.sort()

#Compare sleep duration and start time
'''plt.scatter(start_list, h_list, alpha=0.2)
plt.scatter(stop_list, h_list, alpha=0.2, c='red')
for start, stop, duration in zip(start_list, stop_list, h_list):
    plt.plot([start,stop],[duration,duration],'k-')

plt.title("Hours Asleep vs. Start time")
plt.xlabel("start time")
plt.ylabel("Hours asleep")
ax = plt.gcf().axes[0]
ax.grid(True)
plt.show()
plt.gca().clear()
plt.close()'''

#max_sleep = max(event.hours_asleep
#            for event in sleep_list)
#print(f"Max sleep is {max_sleep} hours")


corrected_date_list = []
corrected_hours_list = []
start_time_list = []
stop_time_list = []
previous_date = datetime.date(2000, 8, 30)  #random date in the far past

#Exlcude dates when I was not in Seattle
#exclusion dates is a list of dates in the format
#exclusion_dates = [[datetime.date(2016, 12, 20), datetime.date(2017, 1, 4)],...
from vacation_dates import exclusion_dates

previous_log_id = 0

for event in sleep_list:
    start_hour = event.start_time.hour
    if start_hour<11:
        shift = 0
        date = event.start_time.date() - datetime.timedelta(days=1)  #shift date to day before for start times after midnight til 11am
    else:
        date = event.start_time.date() #don't shift date when sleep starts after 11am and before midnight
        shift = -24
    good_date = True
    for date_range in exclusion_dates:
        start_date, stop_date = date_range
        if start_date <= date <= stop_date:
            good_date = False
            break
    if good_date:
        if previous_log_id==event.log_id:  #Remove any duplicate sleep logs (at beginning/end of files)
            continue
        #Remove naps
        elif 12<=event.start_time.hour<20 and event.stop_time.hour<20:
            continue
        #Combine sleep records for events with same dates
        elif previous_date==date:
            corrected_hours_list[-1] += event.hours_asleep
            stop_time_list[-1] = event.stop_time.hour+event.stop_time.minute*1/60
        else:
            corrected_date_list.append(date)
            corrected_hours_list.append(event.hours_asleep)
            start_time_list.append(event.start_time.hour+shift+event.start_time.minute*1/60)
            stop_time_list.append(event.stop_time.hour+event.stop_time.minute*1/60)
        previous_date = date
        previous_log_id = event.log_id

plt.plot(corrected_date_list, corrected_hours_list)
ax = plt.gcf().axes[0]
formatter = dates.DateFormatter('%Y-%m')

#Make the time axis have major ticks for every year and minor ticks for every month
years = dates.YearLocator()   # every year
months = dates.MonthLocator()  # every month
years_fmt = dates.DateFormatter('%Y') #Label only the major ticks
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(years_fmt)
ax.xaxis.set_minor_locator(months)
ax.grid(True)

plt.gcf().autofmt_xdate(rotation=25)

#plt.scatter(day, hours_asleep)
#plt.plot_date(day, hours_asleep)

plt.title("Hours Asleep vs. Date")
plt.xlabel("Date")
plt.ylabel("Hours asleep")
#plt.show()
plt.gca().clear()
plt.close()

#Functions taken from "Data Science from Scratch", second edition, by Joel Grus
def bucketize(point: float, bucket_size: float) -> float:
    """Floor the point to the next lower multiple of bucket_size"""
    return bucket_size * math.floor(point / bucket_size)

def make_histogram(points: List[float], bucket_size: float) -> Dict[float, int]:
    """Buckets the points and counts how many in each bucket"""
    return Counter(bucketize(point, bucket_size) for point in points)

def plot_histogram(points: List[float], bucket_size: float, title: str = ""):
    histogram = make_histogram(points, bucket_size)
    plt.bar(histogram.keys(), histogram.values(), width=bucket_size)
    plt.title(title)
    plt.show()
    plt.close()
    
#plot_histogram(corrected_hours_list,0.2,"Sleep data")

hour_list = []
for event in sleep_list:
    start_time_hour = event.start_time.hour
    hour_list.append(start_time_hour)

#plot_histogram(hour_list,1,"Start time")


#Get Seattle weather data
weather_list = []
with open('SeattleWeather.csv') as f:
    comma_reader = csv.reader(f, delimiter=',')
    next(comma_reader) #skip the first row of the file (header row)
    for row in comma_reader:
        string_date = row[2]
        converted_date = datetime.datetime.strptime(string_date, '%Y-%m-%d').date()
        temp_max = float(row[4])
        temp_min = float(row[5])
        day_weather = DayWeather(converted_date, temp_max, temp_min)
        weather_list.append(day_weather)

temp_max_list = []
temp_min_list = []
for date in corrected_date_list:
    for day in weather_list:
        if date == day.date:
            temp_max_list.append(day.temp_max)
            temp_min_list.append(day.temp_min)
#print(date)

print("Max temperature correlation is " + str(stats.pearsonr(temp_max_list, corrected_hours_list)))
print("Min temperature correlation is " + str(stats.pearsonr(temp_min_list, corrected_hours_list)))

plt.scatter(temp_max_list, corrected_hours_list, alpha=0.2)
plt.title("Hours Asleep vs. Max Temperature")
plt.xlabel("Max temperature")
plt.ylabel("Hours asleep")
ax = plt.gcf().axes[0]
ax.grid(True)
plt.show()
plt.gca().clear()
plt.close()

plt.scatter(temp_min_list, corrected_hours_list, alpha=0.2)
plt.title("Hours Asleep vs. Min Temperature")
plt.xlabel("Min temperature")
plt.ylabel("Hours asleep")
ax = plt.gcf().axes[0]
ax.grid(True)
plt.show()
plt.gca().clear()
plt.close()

print("start time correlation is " + str(stats.pearsonr(start_time_list, corrected_hours_list)))
print("stop time correlation is " + str(stats.pearsonr(stop_time_list, corrected_hours_list)))

#Compare sleep duration and start time
plt.scatter(start_time_list, corrected_hours_list, alpha=0.2)
# label each point
'''for time, hours, date in zip(start_time_list, corrected_hours_list, corrected_date_list):
    plt.annotate(date,
                 xy=(time, hours), # Put the label with its point
                 xytext=(5, -5),                  # but slightly offset
                 textcoords='offset points',
                 size=5)'''
plt.title("Hours Asleep vs. Start time")
plt.xlabel("Time relative to midnight (hours)")
plt.ylabel("Hours asleep")
ax = plt.gcf().axes[0]
ax.grid(True)
plt.show()
plt.gca().clear()
plt.close()

#Compare sleep duration and stop time
plt.scatter(stop_time_list, corrected_hours_list, alpha=0.2, c='red')
plt.title("Hours Asleep vs. Stop time")
plt.xlabel("Time relative to midnight (hours)")
plt.ylabel("Hours asleep")
ax = plt.gcf().axes[0]
ax.grid(True)
plt.show()
plt.gca().clear()
plt.close()


#Checking SleepEvent class
ev = SleepEvent(5, 7.5, datetime.datetime(2018, 12, 14, 12, 4, 30), datetime.datetime(2018, 12, 14, 12, 5, 30))
assert ev.log_id == 5
assert ev.hours_asleep == 7.5
assert ev.start_time == datetime.datetime(2018, 12, 14, 12, 4, 30)
assert ev.stop_time == datetime.datetime(2018, 12, 14, 12, 5, 30)

#Checking Day class
day = Day(datetime.date(2018, 12, 14), 7.5, 75, 40)
assert day.date == datetime.date(2018, 12, 14)
assert day.hours_asleep == 7.5
assert day.temp_max == 75
assert day.temp_min == 40

#Checking DayWeather class
day_weather = DayWeather(datetime.date(2018, 12, 14), 75, 40)
assert day.date == datetime.date(2018, 12, 14)
assert day.temp_max == 75
assert day.temp_min == 40
