import datetime
import pandas as pd
import numpy as np

def getDaysHolidays(day_holiday, flAfter):
    res = []
    t = 0
    if flAfter == 0:
        day_holiday.sort_values('day', ascending = False, inplace = True)
        t = 30
    else:
        day_holiday.sort_values('day', ascending = True, inplace = True)
        t = 40
    
    for e in day_holiday.itertuples():
        if e.isHoliday2 == 1:
            t = 0
        else:
            t += 1
        res.append(t)
    return res

def prepareTransactions(transactions, startDate):
    if not ('day' in transactions.columns):
        transactions['day'] = transactions.tr_datetime.apply(lambda dt: dt.split()[0]).astype('int16')
    if ('tr_datetime' in transactions.columns):
        transactions['time'] = pd.to_datetime(transactions.tr_datetime.apply(lambda dt: dt.split()[1]), format='%H:%M:%S')
        transactions['hour'] = transactions.time.dt.hour.astype('int8')
        transactions['minute'] = transactions.time.dt.minute.astype('int8')
        transactions['second'] = transactions.time.dt.second.astype('int8')
        transactions['time_second'] = (transactions.hour.astype('int32') * 60 * 60 + transactions.minute.astype('int32') * 60 + transactions.second.astype('int32')).astype('int32')
        transactions.drop('tr_datetime', axis=1, inplace=True)
        transactions.drop('time', axis=1, inplace=True)
    
    day_grid = pd.DataFrame(np.arange(487), columns = ['day'])
    day_grid['date'] = day_grid.day.apply(lambda x: startDate + datetime.timedelta(days=x))

    day_grid['week_num'] = (day_grid['date'].apply(lambda x: x.isocalendar()[1])).astype('int8')
    day_grid['week_day'] = (day_grid['date'].dt.dayofweek).astype('int8')
    day_grid['month_num'] = (day_grid['date'].dt.month).astype('int8')
    day_grid['month_day'] = (day_grid['date'].dt.day).astype('int8')
    day_grid['month_num_1'] = ((day_grid['date'].dt.year - 2014) * 12 + day_grid['date'].dt.month).astype('int32')

    holidays1 = set(['2014-11-04',
                   '2015-01-01', '2015-01-02', '2015-01-03', '2015-01-04', '2015-01-05', '2015-01-06', '2015-01-07', '2015-01-08',
                   '2015-02-23', '2015-03-08',
                   '2015-05-01', '2015-05-09', '2015-06-12', '2015-11-04'])
    holidays = set(['2014-11-03', '2014-11-04',
                   '2015-01-01', '2015-01-02', '2015-01-03', '2015-01-04', '2015-01-05', '2015-01-06', '2015-01-07', '2015-01-08', '2015-01-09',
                   '2015-02-23', '2015-03-08', '2015-03-09',
                   '2015-05-01', '2015-05-04', '2015-05-09', '2015-05-11', '2015-06-12', '2015-11-04'])
    holidays2 = set(['2014-11-01', '2014-11-02', '2014-11-03', '2014-11-04',
                   '2015-01-01', '2015-01-02', '2015-01-03', '2015-01-04', '2015-01-05', '2015-01-06', '2015-01-07', '2015-01-08', '2015-01-09', '2015-01-10', '2015-01-11',
                   '2015-02-20', '2015-02-21', '2015-02-22', '2015-02-23', '2015-03-07', '2015-03-08', '2015-03-09',
                   '2015-05-01', '2015-05-02', '2015-05-03', '2015-05-04', '2015-05-08', '2015-05-09', '2015-05-10', '2015-05-11', '2015-06-12', '2015-06-13', '2015-06-14',
                   '2015-11-04'])

    day_grid['isHoliday'] = (day_grid['date'].isin(holidays)).astype('int8')
    day_grid['isHoliday1'] = (day_grid['date'].isin(holidays1)).astype('int8')
    day_grid['isHoliday2'] = (day_grid['date'].isin(holidays2)).astype('int8')
    day_grid['isWeekend'] = (day_grid['week_day'] >= 5).astype('int8')
    day_grid['isWeekendHoliday'] = day_grid['isHoliday'] | day_grid['isWeekend']
    day_grid['isHoliday6'] = day_grid['isHoliday'] | (day_grid['week_day'] == 6).astype('int8')

    day_grid['isBeforeHoliday'] = (day_grid['date'].apply(lambda x: x + datetime.timedelta(days=1)).isin(holidays)).astype('int8')
    day_grid['isAfterHoliday'] = (day_grid['date'].apply(lambda x: x + datetime.timedelta(days=-1)).isin(holidays)).astype('int8')

    day_grid['isWeekendHoliday1'] = ((day_grid.isWeekendHoliday) | (day_grid.week_day == 4) & (day_grid.isAfterHoliday) | (day_grid.week_day == 0) & (day_grid.isBeforeHoliday)).astype('int8')

    pred_holidays = set(['2014-10-31', '2014-12-31', '2015-02-20', '2015-04-30', '2015-05-08', '2015-06-11', '2015-11-03'])
    day_grid['isPredHolidays'] = (day_grid['date'].isin(pred_holidays) | day_grid['date'].isin(holidays2) | (day_grid.week_day == 4) & (day_grid.isAfterHoliday) | (day_grid.week_day == 0) & (day_grid.isBeforeHoliday)).astype('int8')

    transactions = transactions.merge(day_grid)
    transactions.drop('date', axis=1, inplace=True)
    
    day_holiday = transactions[['day', 'isHoliday2']].drop_duplicates().reset_index(drop = True)
    day_holiday['before'] = getDaysHolidays(day_holiday, 0)
    day_holiday['after'] = getDaysHolidays(day_holiday, 1)
    transactions = transactions.merge(day_holiday)
    return transactions

