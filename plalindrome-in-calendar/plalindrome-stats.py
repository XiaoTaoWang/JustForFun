# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 16:08:59 2016

@author: wxt

To Zejia Cui, since this script was born for her amazing birthday date.
"""
import datetime, lunardate

startday = datetime.date(1900, 1, 31)
endday = datetime.date(2049, 12, 31)

total = 0
valid = 0
plalindromes = []

cur = startday
while cur <= endday:
    triple = (cur.year, cur.month, cur.day)
    lunar = lunardate.LunarDate.fromSolarDate(*triple)
    solar_string = '{0:04d}'.format(int(''.join(map(str, triple[1:]))))
    lunar_string = '{0:04d}'.format(int(''.join(map(str, (lunar.month, lunar.day)))))
    if solar_string[::-1] == lunar_string:
        plalindromes.append((cur, lunar, solar_string, lunar_string))
    
    total += 1
    check_1 = lunardate.LunarDate(cur.year, int(solar_string[::-1][:2]),
                                  int(solar_string[::-1][2:]))
    check_2 = lunardate.LunarDate(lunar.year, int(solar_string[::-1][:2]),
                                  int(solar_string[::-1][2:]))
    
    label = 1
    try:
        check_1.toSolarDate()
    except ValueError:
        try:
            check_2.toSolarDate()
        except ValueError:
            label = 0
    
    valid += label
    
    cur += datetime.timedelta(1)

print 'There are total {0:d} days from {1:%Y-%m-%d} to {2:%Y-%m-%d}'.format(len(plalindromes), startday, endday)
print 'But there are only {:d} plalindromes among them.'
print '-'*75
print '{0:>20s} {1:>20s} {2:>20s}'.format('Solar Date', 'Lunar Date', 'Plalindromes')
for member in plalindromes:
    solar = '{0:04d}-{1:02d}-{2:02d}'.format(member[0].year, member[0].month, member[0].day)
    lunar = '{0:04d}-{1:02d}-{2:02d}'.format(member[1].year, member[1].month, member[1].day)
    if member[0] == datetime.date(1994, 1, 21):
        print '{0:>20s} {1:>20s} {2:>20s}*'.format(solar, lunar, ' <-> '.join(member[2:]))
    else:
        print '{0:>20s} {1:>20s} {2:>20s}'.format(solar, lunar, ' <-> '.join(member[2:]))
        