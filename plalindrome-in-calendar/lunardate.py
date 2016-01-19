# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 15:56:14 2016

This is modified from lunar project.

lunar project:
   Copyright (C) 1988,1989,1991,1992,2001 Fung F. Lee and Ricky Yeung
   Licensed under GPLv2.

@author: wxt

Limits
------

This library can only deal with year from 1900 to 2049 (in chinese calendar).

"""
import datetime

class LunarDate(object):
    _startDate = datetime.date(1900, 1, 31)

    def __init__(self, year, month, day, isLeapMonth=False):
        self.year = year
        self.month = month
        self.day = day
        self.isLeapMonth = bool(isLeapMonth)

    def __str__(self):
        return 'LunarDate(%d, %d, %d, %d)' % (self.year, self.month, self.day, self.isLeapMonth)

    __repr__ = __str__

    @staticmethod
    def fromSolarDate(year, month, day):
        '''
        >>> LunarDate.fromSolarDate(1900, 1, 31)
        LunarDate(1900, 1, 1, 0)
        >>> LunarDate.fromSolarDate(2008, 10, 2)
        LunarDate(2008, 9, 4, 0)
        >>> LunarDate.fromSolarDate(1976, 10, 1)
        LunarDate(1976, 8, 8, 1)
        >>> LunarDate.fromSolarDate(2033, 10, 23)
        LunarDate(2033, 10, 1, 0)
        '''
        solarDate = datetime.date(year, month, day)
        offset = (solarDate - LunarDate._startDate).days
        return LunarDate._fromOffset(offset)

    def toSolarDate(self):
        '''
        >>> LunarDate(1900, 1, 1).toSolarDate()
        datetime.date(1900, 1, 31)
        >>> LunarDate(2008, 9, 4).toSolarDate()
        datetime.date(2008, 10, 2)
        >>> LunarDate(1976, 8, 8, 1).toSolarDate()
        datetime.date(1976, 10, 1)
        >>> LunarDate(2004, 1, 30).toSolarDate()
        Traceback (most recent call last):
        ...
        ValueError: day out of range
        >>> LunarDate(2050, 1, 1).toSolarDate()
        Traceback (most recent call last):
        ...
        ValueError: year out of range [1900, 2050)
        >>>
        '''
        def _calcDays(yearInfo, month, day, isLeapMonth):
            isLeapMonth = int(isLeapMonth)
            res = 0
            for _month, _days, _isLeapMonth in self._enumMonth(yearInfo):
                if (_month, _isLeapMonth) == (month, isLeapMonth):
                    if 1 <= day <= _days:
                        res += day - 1
                        return res
                    else:
                        raise ValueError("day out of range")
                res += _days

            raise ValueError("month out of range")

        offset = 0
        if self.year < 1900 or self.year >= 2050:
            raise ValueError('year out of range [1900, 2050)')
        yearIdx = self.year - 1900
        for i in range(yearIdx):
            offset += yearDays[i]

        offset += _calcDays(yearInfos[yearIdx], self.month, self.day, self.isLeapMonth)
        return self._startDate + datetime.timedelta(days=offset)

    def __sub__(self, other):
        if isinstance(other, LunarDate):
            return self.toSolarDate() - other.toSolarDate()
        elif isinstance(other, datetime.date):
            return self.toSolarDate() - other
        elif isinstance(other, datetime.timedelta):
            res = self.toSolarDate() - other
            return LunarDate.fromSolarDate(res.year, res.month, res.day)
        raise TypeError

    def __rsub__(self, other):
        if isinstance(other, datetime.date):
            return other - self.toSolarDate()

    def __add__(self, other):
        if isinstance(other, datetime.timedelta):
            res = self.toSolarDate() + other
            return LunarDate.fromSolarDate(res.year, res.month, res.day)
        raise TypeError

    def __radd__(self, other):
        return self + other

    def __eq__(self, other):
        
        if not isinstance(other, LunarDate):
            return False

        return self - other == datetime.timedelta(0)

    def __lt__(self, other):
        
        try:
            return self - other < datetime.timedelta(0)
        except TypeError:
            raise TypeError("can't compare LunarDate to %s" % (type(other).__name__,))

    def __le__(self, other):
        # needed because the default implementation tries equality first,
        # and that does not throw a type error
        return self < other or self == other

    def __gt__(self, other):
        
        return not self <= other

    def __ge__(self, other):
        
        return not self < other

    @classmethod
    def today(cls):
        res = datetime.date.today()
        return cls.fromSolarDate(res.year, res.month, res.day)

    @staticmethod
    def _enumMonth(yearInfo):
        months = [(i, 0) for i in range(1, 13)]
        leapMonth = yearInfo % 16
        if leapMonth == 0:
            pass
        elif leapMonth <= 12:
            months.insert(leapMonth, (leapMonth, 1))
        else:
            raise ValueError("yearInfo %r mod 16 should in [0, 12]" % yearInfo)

        for month, isLeapMonth in months:
            if isLeapMonth:
                days = (yearInfo >> 16) % 2 + 29
            else:
                days = (yearInfo >> (16 - month)) % 2 + 29
            yield month, days, isLeapMonth

    @classmethod
    def _fromOffset(cls, offset):
        def _calcMonthDay(yearInfo, offset):
            for month, days, isLeapMonth in cls._enumMonth(yearInfo):
                if offset < days:
                    break
                offset -= days
            return (month, offset + 1, isLeapMonth)

        offset = int(offset)

        for idx, yearDay in enumerate(yearDays):
            if offset < yearDay:
                break
            offset -= yearDay
        year = 1900 + idx

        yearInfo = yearInfos[idx]
        month, day, isLeapMonth = _calcMonthDay(yearInfo, offset)
        return LunarDate(year, month, day, isLeapMonth)

yearInfos = [
        #    /* encoding:
        #               b bbbbbbbbbbbb bbbb
        #       bit#    1 111111000000 0000
        #               6 543210987654 3210
        #               . ............ ....
        #       month#    000000000111
        #               M 123456789012   L
        #
        #    b_j = 1 for long month, b_j = 0 for short month
        #    L is the leap month of the year if 1<=L<=12; NO leap month if L = 0.
        #    The leap month (if exists) is long one iff M = 1.
        #    */
        0x04bd8,                                    #   /* 1900 */
        0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950,#   /* 1905 */
        0x16554, 0x056a0, 0x09ad0, 0x055d2, 0x04ae0,#   /* 1910 */
        0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540,#   /* 1915 */
        0x0d6a0, 0x0ada2, 0x095b0, 0x14977, 0x04970,#   /* 1920 */
        0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54,#   /* 1925 */
        0x02b60, 0x09570, 0x052f2, 0x04970, 0x06566,#   /* 1930 */
        0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60,#   /* 1935 */
        0x186e3, 0x092e0, 0x1c8d7, 0x0c950, 0x0d4a0,#   /* 1940 */
        0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0,#   /* 1945 */
        0x092d0, 0x0d2b2, 0x0a950, 0x0b557, 0x06ca0,#   /* 1950 */
        0x0b550, 0x15355, 0x04da0, 0x0a5d0, 0x14573,#   /* 1955 */
        0x052d0, 0x0a9a8, 0x0e950, 0x06aa0, 0x0aea6,#   /* 1960 */
        0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260,#   /* 1965 */
        0x0f263, 0x0d950, 0x05b57, 0x056a0, 0x096d0,#   /* 1970 */
        0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250,#   /* 1975 */
        0x0d558, 0x0b540, 0x0b5a0, 0x195a6, 0x095b0,#   /* 1980 */
        0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50,#   /* 1985 */
        0x06d40, 0x0af46, 0x0ab60, 0x09570, 0x04af5,#   /* 1990 */
        0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58,#   /* 1995 */
        0x05ac0, 0x0ab60, 0x096d5, 0x092e0, 0x0c960,#   /* 2000 */
        0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0,#   /* 2005 */
        0x0abb7, 0x025d0, 0x092d0, 0x0cab5, 0x0a950,#   /* 2010 */
        0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0,#   /* 2015 */
        0x0a5b0, 0x15176, 0x052b0, 0x0a930, 0x07954,#   /* 2020 */
        0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6,#   /* 2025 */
        0x0a4e0, 0x0d260, 0x0ea65, 0x0d530, 0x05aa0,#   /* 2030 */
        0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0,#   /* 2035 */
        0x1d0b6, 0x0d250, 0x0d520, 0x0dd45, 0x0b5a0,#   /* 2040 */
        0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0,#   /* 2045 */
        0x0aa50, 0x1b255, 0x06d20, 0x0ada0          #   /* 2049 */
        ]

def yearInfo2yearDay(yearInfo):
    
    yearInfo = int(yearInfo)

    res = 29 * 12

    leap = False
    if yearInfo % 16 != 0:
        leap = True
        res += 29

    yearInfo //= 16

    for i in range(12 + leap):
        if yearInfo % 2 == 1:
            res += 1
        yearInfo //= 2
    return res

yearDays = [yearInfo2yearDay(x) for x in yearInfos]

def day2LunarDate(offset):
    offset = int(offset)
    res = LunarDate()

    for idx, yearDay in enumerate(yearDays):
        if offset < yearDay:
            break
        offset -= yearDay
    res.year = 1900 + idx


