#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on Sun Dec 13 12:32:09 2015

# Author: XiaoTao Wang
# Organization: HuaZhong Agricultural University

import calendar, datetime

class Schedule:
    """
    Make a schedule on the calender automatically in the given date interval.    
    
    Parameters
    ----------
    startpoint : string
        Start point of the date. Format: Year-Month-Day
        
    endpoint : string
        End point of the date. Format: Year-Month-Day
    
    remove : list of strings
        Exclude the date points in the list from the schedule.
        
    """
    dayindex = [6] + range(6)
    weekheader = [calendar.day_abbr[i] for i in dayindex]
    outfile = 'Workers.txt'
    
    def __init__(self, startpoint, endpoint, remove = []):
        
        self.startpoint = datetime.date(*tuple(int(i) for i in startpoint.split('-')))
        self.endpoint = datetime.date(*tuple(int(i) for i in endpoint.split('-')))
        self.customcalendar = calendar.TextCalendar(firstweekday = self.dayindex[0])
        assert self.startpoint < self.endpoint, 'Invalid date interval'
        
        self.remove = []
        for days in remove:
            if '~' not in days: # Year-Month-Day~Year-Month-Day indicates a date interval
                datepoint = datetime.date(*tuple(int(i) for i in days.split('-')))
                self.remove.append(datepoint)
            else:
                HSS, HES = days.split('~')
                HS = datetime.date(*tuple(int(i) for i in HSS.split('-'))) # Start of the holiday
                HE = datetime.date(*tuple(int(i) for i in HES.split('-'))) # End of the holiday
                while HS <= HE:
                    self.remove.append(HS)
                    HS += datetime.timedelta(1)
            
        
    def gencalendar(self):
        
        self.months = []
        
        for year in range(self.startpoint.year, self.endpoint.year + 1):
            for month in range(1, 13):
                lb = datetime.date(year, month, calendar.mdays[month])
                rb = datetime.date(year, month, 1)
                if lb < self.startpoint:
                    continue
                if rb > self.endpoint:
                    continue
                mondays = self.customcalendar.monthdatescalendar(year, month)
                daylist = self.customcalendar.monthdayscalendar(year, month)
                mask = []
                for num, week in enumerate(mondays):
                    temp = []
                    for i, d in enumerate(week):
                        if (d in self.remove) or (d < self.startpoint) or (d > self.endpoint) \
                            or (self.dayindex[i] == 6) or (self.dayindex[i] == 5):
                            temp.append(0)
                        else:
                            temp.append(int(bool(1) and bool(daylist[num][i])))
                    
                    mask.append(temp)
                
                pool = [year, calendar.month_name[month], daylist, mask]
                self.months.append(pool)
    
    def genworkers(self):
		
        while True: # Persistent Generator
            with open(self.outfile, 'r') as workers:
                for line in workers:
                    members = line.rstrip().decode('gbk').split()
                    yield members
    
    def genschedule(self, row, col):
        
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        from scipy.interpolate import interp1d
        from matplotlib import style
        import matplotlib
        
        style.use('grayscale')
        
        topFunc = dict(zip(range(1, 5), [0.77, 0.84, 0.85, 0.86]))
        matplotlib.rcParams['figure.subplot.top'] = topFunc[row]
        
        figsize = (10, np.sqrt(2) * 10)
        rotation = np.log2(row * col)
        if rotation % 2 == 0:
            figsize = (np.sqrt(2) * 10, 10)
        
        daysize = dict(zip(range(1, 5), [27, 14, 13, 11]))
        namesize = dict(zip(range(1, 5), [18, 9, 8, 6]))
        weeksize = dict(zip(range(1, 5), [21, 13, 10, 8]))
        monthsize = dict(zip(range(1, 5), [25, 15, 11, 9]))
        
        gs = gridspec.GridSpec(row, col, hspace = 0.3, wspace = 0.2)
        
        workers = self.genworkers()
        
        suptitle = u'521值日表'
        fig = plt.figure(figsize = figsize)
        for i, item in enumerate(self.months):
            mask = np.array(item[-1])
            
            ax = fig.add_subplot(gs[i])
            ax.pcolor(np.logical_not(mask), cmap = plt.cm.Greys, vmax = 5)
            
            ax.set_yticks(np.arange(mask.shape[0]), minor = False)
            ax.set_xticks(np.arange(mask.shape[1]), minor = False)
            # Want a more natural, table-like display
            ax.invert_yaxis()
            ax.xaxis.tick_top()
            ax.grid(linestyle = '--', lw = 1)
            
            for t in ax.xaxis.get_major_ticks(): 
                t.tick1On = False 
                t.tick2On = False 
            for t in ax.yaxis.get_major_ticks():
                t.tick1On = False
                t.tick2On = False
            
            for j in range(mask.shape[0]):
                for k in range(mask.shape[1]):
                    day = item[-2][j][k]
                    Text = []
                    if day:
                        Text.append(str(day))
                    if mask[j, k]:
                        worker = workers.next()
                        wx = '\n'.join(worker)
                        Text.append(wx)
                    
                    if len(Text) == 1:
                        ax.text(k + 0.5, j + 0.5, Text[0], ha = 'center',
                                va = 'center', fontsize = daysize[row])
                    if len(Text) == 2:
                        ax.text(k + 0.5, j + 0.35, Text[0], ha = 'center',
                                va = 'center', fontsize = daysize[row])
                        ax.text(k + 0.5, j + 0.95, Text[1], ha = 'center',
                                va = 'bottom', fontsize = namesize[row],  fontproperties = 'STKaiti')
            
            ax.set_xlim(0, mask.shape[1])
            Xmin = ax.get_position().xmin
            Xmax = ax.get_position().xmax
            Ymin = ax.get_position().ymin
            Ymax = ax.get_position().ymax
            funcX = interp1d([0, mask.shape[1]], [Xmin, Xmax])
            funcY = interp1d([0, mask.shape[0]], [0, Ymax - Ymin])
            
            for j in range(len(self.weekheader)):
                fig.text(funcX(j + 0.5), Ymax + funcY(0.08), self.weekheader[j],
                         va = 'bottom', ha = 'center', fontsize = weeksize[row])
            
            fig.text((Xmin + Xmax) / 2, Ymax + funcY(0.45), ', '.join([item[1], str(item[0])]),
                     va = 'bottom', ha = 'center', fontsize = monthsize[row])
            
            ax.set_xticklabels('')
            ax.set_yticklabels('')
                     
        
        fig.text(0.5, 0.9, suptitle, fontsize = 40,
                 va = 'bottom', ha = 'center', fontproperties = 'STKaiti')
                 
        remarks = u'备注：值日范围包括扫地、拖地、以及公共桌面的清洁'
        fig.text(0.12, Ymin - funcY(0.3), remarks, fontsize = 13,
                 va = 'top', ha = 'left', fontproperties = 'STKaiti')
        plt.savefig('Schedule.pdf')
        plt.close()


if __name__ == '__main__':

    ## Example
    Holidays = ['2015-12-31', '2016-1-1', '2016-2-1~2016-2-20']
            
    task = Schedule('2015-12-14', '2016-2-29', Holidays)
    task.gencalendar()
    task.genschedule(3, 1) # Three rows and one column in the output schecule