#!/usr/bin/env python
import sys
import os
from numpy import arange
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MONDAY
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter

class PlotManager():
  def __init__(self,archive_name):

    self.archive_name = archive_name
    root = archive_name.split('.')[0]
    date_file = os.path.join(
        archive_name, 'results', 'tag_date_data_{0}.txt'.format(root))
    rank_file = os.path.join(
        archive_name, 'results', 'tag_rank_data_{0}.txt'.format(root))

    self.tag_data = dict()
    self.top_tags = list()
    with open(date_file, mode='r') as input_dates:
      for line in input_dates.readlines():
        line = line.strip()
        line = line.split(',')
        tag = line[0]
        dates = line[1:]
        self.tag_data[tag] = dates

    with open(rank_file, mode='r') as input_ranks:
      for line in input_ranks.readlines():
        # Tag rank file is of form (rank,tag_name,count)
        line = line.strip()
        tag = line.split(',')[1]
        self.top_tags.append(tag)

  def make_freq_plot(self,tag=''):
    """make some plots"""

    # Every monday
    mondays = WeekdayLocator(MONDAY)

    # Every 3rd month
    months = MonthLocator(range(1, 13), bymonthday=1, interval=3)
    monthsFmt = DateFormatter("%b '%y")

    dates = self.tag_data[tag]
    date_converter = mdates.strpdate2num("%Y-%m-%dT%H:%M:%S.%f")
    dates = [date_converter(d) for d in dates]

    dates = sorted(dates)
    number_of_months = int((dates[-1]-dates[0]))/30

    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(dates, number_of_months, 
        facecolor='green', alpha=0.75, label=[tag])
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(mondays)
    ax.autoscale_view()
    ax.set_ylabel('Events per 30 days')
    ax.set_xlabel('Post Date')
    ax.set_title('Tag Frequency')
    #ax.xaxis.grid(False, 'major')
    #ax.xaxis.grid(True, 'minor')
    ax.grid(True)

    fig.autofmt_xdate()
    plt.legend(loc='upper left')
    output_name = os.path.join(
        self.archive_name,'plots',
        'freq_{0}_{1}_tight'.format(self.top_tags.index(tag)+1,tag))
    #plt.savefig('{0}.png'.format(output_name))
    plt.savefig('{0}.png'.format(output_name), bbox_inches='tight')
    #plt.show()

  def make_day_plot(self,tag=''):
    """Make plot of tag usage count per day of the week. Save output."""
    NDAYS = 7
    # 7 days of week, 0 is M, 6 is Sunday
    days_tag1 = {i:0 for i in range(NDAYS)}
    data_tag1 = self.tag_data[tag]
    for d in data_tag1:
      a_date = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%f")
      weekday = a_date.weekday()
      days_tag1[weekday]+=1
    ind = arange(NDAYS)  # the x locations for the groups
    width = 0.30       # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, days_tag1.values(), width, color='b', label=tag)
    # add some text for labels, title and axes ticks
    ax.set_ylabel('Post Count')
    ax.set_xlabel('Day of Week')
    ax.set_title('Tag Usage per Day')
    ax.set_xticks(ind+width)
    ax.set_xticklabels( ('M', 'T', 'W', 'Th', 'F', 'S', 'Su') )
    ax.legend()

    # Save file.
    output_name = os.path.join(
        self.archive_name,'plots',
        'days_{0}_{1}_tight'.format(self.top_tags.index(tag)+1,tag))
    plt.savefig('{0}.png'.format(output_name), bbox_inches='tight')

  def make_top_freq_plots(self, N=10):
    """Make frequency plots of top N tags. Save output to file."""
    for tag in self.top_tags[:N]:
      self.make_freq_plot(tag)

  def make_top_day_plots(self, N=10):
    """Make usage per day plots of top N tags. Save output to file."""
    for tag in self.top_tags[:N]:
      self.make_day_plot(tag)

def main(argv):
  archive_name = argv[1]

  plotter = PlotManager(archive_name)

  # Default to make frequency plots of top N=10 tags
  plotter.make_top_freq_plots(N=5)
  plotter.make_top_day_plots(N=5)


if __name__ == "__main__":
  main(sys.argv)
