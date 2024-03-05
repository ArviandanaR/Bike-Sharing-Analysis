import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
import datetime
import os
from PIL import Image


st.title(':red[Count of Bike Rented]')
path = os.path.dirname(__file__)
full_path = path+'/hour.csv'
df = pd.read_csv(full_path)

#Preprocess

df['yr'] = df['yr'].map({0: 2011, 1: 2012})
df['season'] = df['season'].map({1: 'Springer', 2: 'Summer', 3: 'Fall', 4: 'Winter'})

hour_map = {0: '12 AM',1: '1 AM',2: '2 AM',3: '3 AM',4: '4 AM',5: '5 AM',6: '6 AM',
            7: '7 AM',8: '8 AM',9: '9 AM',10: '10 AM',11: '11 AM',12: '12 PM',
            13: '1 PM',14: '2 PM',15: '3 PM',16: '4 PM',17: '5 PM',18: '6 PM',
            19: '7 PM',20: '8 PM',21: '9 PM',22: '10 PM',23: '11 PM'}
df['hour'] = df['hr'].map(hour_map)

month_map = {1: 'January',2: 'February',3: 'March',
             4: 'April', 5: 'May', 6: 'June',
             7: 'July',8: 'August',9: 'September',
             10: 'October', 11: 'November', 12: 'Desember'}
df['month'] = df['mnth'].map(month_map)

day_map = {0: 'Monday',1: 'Tuesday',2: 'Wednesday',
           3: 'Thursday', 4: 'Friday',5: 'Saturday',6: 'Sunday'}
df['day'] = df['weekday'].map(day_map)

df['dteday'] = pd.to_datetime(df['dteday'])

min_date = df['dteday'].min()
max_date = df["dteday"].max()

path = os.path.dirname(__file__)
img_path = path+'/Bike.png'
img = Image.open(img_path)

with st.sidebar:
    st.image(img)

    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    measure = st.radio(
        'Choose your measurement:',
        ['Total Bike Rent', 'Average Bike Rent'],
        index = 0
    )

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

if measure == 'Total Bike Rent':
    ukuran = 'sum'
else:
    ukuran = 'mean'


df_dateindex = df.copy()
df_dateindex.set_index('dteday', inplace = True)

df_weekly = df_dateindex.resample('W-SUN', label='left', closed='left').agg({'cnt': ukuran, 'casual': ukuran, 'registered': ukuran}).reset_index()
df_daily = df_dateindex.resample('D', label='left', closed='left').agg({'cnt': ukuran, 'casual': ukuran, 'registered': ukuran}).reset_index()

df_dated = df[(df['dteday'] >= str(start_date)) & (df['dteday'] <= str(end_date))]
weekly_dated = df_weekly[(df_weekly['dteday'] >= str(start_date)) & (df_weekly['dteday'] <= str(end_date))]
daily_dated = df_daily[(df_daily['dteday'] >= str(start_date)) & (df_daily['dteday'] <= str(end_date))]


#Visualize

option = st.selectbox(
    label = 'Choose type of Users:',
    options = ('Casual', 'Registered', 'All'),
    index = 2
)

if option == 'All':
    user = 'cnt'
elif option == 'Registered':
    user = 'registered'
else:
    user = 'casual'

col1, col2 = st.columns(2)

sb.set_theme(rc={'axes.facecolor':'0E1117', 'figure.facecolor':'0E1117', 
                 "axes.spines.right": False, "axes.spines.top": False,
                 'axes.edgecolor':'FFFFFF', 'axes.grid': False,
                 'xtick.color':'FFFFFF', 'ytick.color':'FFFFFF',
                 "axes.labelcolor":'FFFFFF'})


with col1:
    Rent = df_dated[user].sum()
    st.metric('Total Bike Rented',
              value = '{:,} Bike'.format(Rent))

st.header('Bike Rented Count by Season', divider = 'red')

options = st.multiselect(
     'Choose the Season:',
     options = ['Springer', 'Summer', 'Fall', 'Winter'],
     default = ['Springer', 'Summer', 'Fall', 'Winter']
)

season = df_dated[df_dated['season'].isin(options)]

fig1, ax1 = plt.subplots(figsize = (16,12))

ax1 = sb.barplot(data = season, x = 'season', y = user, estimator = ukuran, dodge = False, ax = ax1, palette = 'turbo', errorbar = None)
for bars_group in ax1.containers:
    ax1.bar_label(bars_group, padding=2, fontsize=15, fmt = human_format, color = 'white')

ax1.tick_params(axis='y', labelsize=18)
ax1.tick_params(axis='x', labelsize=13)
ax1.set_xlabel('Season', fontsize = 20)
ax1.set_ylabel('Count of Bike Rent', fontsize = 20)
 
st.pyplot(fig1)

st.header('Bike Rented Count by Month', divider = 'red')

start_month, end_month = st.select_slider(
    'Select range of Month:',
    options = [1, 2, 3, 4, 5,  6, 7, 8, 9, 10, 11, 12],
    value = (1,12),
    format_func = lambda x: month_map.get(x)
)

month_data = df_dated[(df_dated['mnth'] >= start_month) & (df_dated['mnth'] <= end_month)]

fig3, ax3 = plt.subplots(figsize = (16,12))

ax3 = sb.barplot(data = month_data, x = 'month', y = user, estimator = ukuran, dodge = False, ax = ax3, palette = 'turbo', errorbar = None)
for bars_group in ax3.containers:
    ax3.bar_label(bars_group, padding=2, fontsize=15, fmt = human_format, color = 'white')

ax3.tick_params(axis='y', labelsize=18)
ax3.tick_params(axis='x', labelsize=13)
ax3.set_xlabel('Month', fontsize = 20)
ax3.set_ylabel('Count of Bike Rent', fontsize = 20)
 
st.pyplot(fig3)

st.header('Bike Rented Count by Day', divider = 'red')

start_day, end_day = st.select_slider(
    'Select range of Day:',
    options = [0, 1, 2, 3, 4, 5, 6],
    value = (0,6),
    format_func = lambda x: day_map.get(x)
)

day_data = df_dated[(df_dated['weekday'] >= start_day) & (df_dated['weekday'] <= end_day)]

fig4, ax4 = plt.subplots(figsize = (16,12))

ax4 = sb.barplot(data = day_data, x = 'day', y = user, dodge = False, ax = ax4, palette = 'turbo', errorbar = None, estimator = ukuran)
for bars_group in ax4.containers:
    ax4.bar_label(bars_group, padding=2, fontsize=15, fmt = human_format, color = 'white')

ax4.tick_params(axis='y', labelsize=18)
ax4.tick_params(axis='x', labelsize=13)
ax4.set_xlabel('Days', fontsize = 20)
ax4.set_ylabel('Count of Bike Rent', fontsize = 20)
 
st.pyplot(fig4)

st.header('Bike Rented Count by Hour', divider = 'red')

start_hour, end_hour = st.select_slider(
    'Select range of Hour:',
    options = [0, 1, 2, 3, 4, 5,  6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    value = (0,23),
    format_func = lambda x: hour_map.get(x)
)

hour_data = df_dated[(df_dated['hr'] >= start_hour) & (df_dated['hr'] <= end_hour)]

fig2, ax2 = plt.subplots(figsize = (16,12))

ax2 = sb.barplot(data = hour_data, x = 'hour', y = user, estimator = ukuran, dodge = False, ax = ax2, palette = 'turbo', errorbar = None)
for bars_group in ax2.containers:
    ax2.bar_label(bars_group, padding=2, fontsize=15, fmt = human_format, color = 'white')

ax2.tick_params(axis='y', labelsize=18)
ax2.tick_params(axis='x', labelsize=13)
ax2.set_xlabel('Rented Hour', fontsize = 20)
ax2.set_ylabel('Count of Bike Rent', fontsize = 20)
 
st.pyplot(fig2)

st.header('Bike Rent Trend', divider = 'red')

opsi = st.selectbox(
    label = 'Choose type of Users:',
    options = ('Weekly', 'Daily'),
    index = 1
)

if opsi == 'Weekly':
    data_tren = weekly_dated
else:
    data_tren = daily_dated

fig5, ax5 = plt.subplots(figsize = (16,12))

ax5 = sb.lineplot(data_tren, x = 'dteday', y = user, color = 'red')

ax5.tick_params(axis='y', labelsize=18)
ax5.tick_params(axis='x', labelsize=13)
ax5.set_xlabel('Date', fontsize = 20)
ax5.set_ylabel('Count of Bike Rent', fontsize = 20)
 
st.pyplot(fig5)