import pandas
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import csv
import time
from datetime import datetime

timeseriesFile = "timeseries.csv"
# generate test timeseries file
# with open(timeseriesFile, 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerow(["timestamp", "cpu_percent", "mem_total"])
#     for i in range(10):
#         csvwriter.writerow([datetime.now().time(), i, 20-i])
#         time.sleep(1)

timeseries = pandas.read_csv(timeseriesFile, parse_dates=["timestamp"])
# # print(timeseries)
# # print(timeseries.dtypes)

# fig, (ax1, ax2) = plt.subplots(2, 1)
# # date_formatter = mpl_dates.DateFormatter('%H:%M:%S')  # "%y-%m-%d %H:%M:%S"
# # ax1.xaxis.set_major_formatter(date_formatter)
# plt.subplot(ax1)
# plt.plot_date(timeseries["timestamp"], timeseries["cpu_percent"])

# plt.subplot(ax2)
# plt.plot_date(timeseries["timestamp"], timeseries["mem_total"])
# # # rotate each xtick label
# # for label in ax2.get_xticklabels():
# #     label.set_horizontalalignment("right")
# #     label.set_rotation(30)

fig = plt.gcf()     # get current figure
# fig.set_size_inches(12.4, 6.8)  # set figure width, height in inches
fig.set_constrained_layout(True)    # automatically adjust subplots and decorations like legends so that they fit in the figure
# fig.set_constrained_layout_pads(hsapce=1, h_pad=0.01)  # specify height padding in inches

data = timeseries
# all 7 plots in a figure
info_topics = ["cpu_percent", "mem_total", "mem_used", "mem_free", "mem_percent", "bytes_sent", "bytes_recv"]
gridspec = fig.add_gridspec(4, 2)  # add_gridspec(nrows, ncols) return a GridSpec: grid layout to place subplots within figure

# memory plots only
# info_topics = ["mem_total", "mem_used", "mem_free", "mem_percent"]
# gridspec = fig.add_gridspec(2, 2)
# bytes plots only
# info_topics = ["bytes_sent", "bytes_recv"]
# gridspec = fig.add_gridspec(2, 1)
# cpu plot only
# info_topics = ["cpu_percent"]
# gridspec = fig.add_gridspec(1, 1)

numinfo = len(info_topics)

for i in range(numinfo):
    info = info_topics[i]
    # add_subplot(nrows, ncols, index): add a subplot that will take the index position on a grid with nrows rows and ncols columns, index starts at 1 in the upper left corner
    # ax = fig.add_subplot(numinfo, 1, i+1)

    if i == 0:      # first subplot
        ax = fig.add_subplot(gridspec[i, :])

        date_formatter = mpl_dates.DateFormatter('%H:%M')  # "%Y-%m-%d %H:%M:%S"
        ax.xaxis.set_major_formatter(date_formatter)
        # plt.setp(ax.xaxis.get_majorticklabels(), horizontalalignment="right", rotation=10)  # ax.get_xticklabels()
        plt.xticks(horizontalalignment="right", rotation=10)
    else:
        ax = fig.add_subplot(gridspec[int((i+1)/2), (i+1)%2])
        # if i < numinfo - 2:     # for all except the first and the very last two subplots
        plt.setp(ax.get_xticklabels(), visible=False)   # set the xtick labels to be invisible

    # memory plots only
    # ax = fig.add_subplot(gridspec[int(i/2), i%2])
    # date_formatter = mpl_dates.DateFormatter('%H:%M')  # "%Y-%m-%d %H:%M:%S"
    # ax.xaxis.set_major_formatter(date_formatter)
    # plt.xticks(horizontalalignment="right", rotation=10)
    # bytes plots only
    # ax = fig.add_subplot(gridspec[i, :])
    # date_formatter = mpl_dates.DateFormatter('%H:%M')  # "%Y-%m-%d %H:%M:%S"
    # ax.xaxis.set_major_formatter(date_formatter)
    # plt.xticks(horizontalalignment="right", rotation=10)
    # cpu plot only
    # ax = fig.gca()
    # date_formatter = mpl_dates.DateFormatter('%H:%M')  # "%Y-%m-%d %H:%M:%S"
    # ax.xaxis.set_major_formatter(date_formatter)
    # plt.xticks(horizontalalignment="right", rotation=10)

    # plot data in the subplot
    ax.plot_date(data["timestamp"], data[info])
    # ax.get_xaxis().set_visible(False)     # hide entire xaxis

    # give relevant title to the subplot
    if info.endswith("_percent"):
        title = info.replace("_percent", " utilization")
        title = title.replace("cpu", "CPU")
        title = title.replace("mem", "Memory")
        # ax.set_title(title + " (%)")
        ax.set_title(title)
        ax.set_ylabel(title + " (%)")
    elif info.startswith("mem_"):
        title = info[4:]
        title = title.capitalize() + " memory"
        # ax.set_title(title + " (MB)")
        ax.set_title(title)
        ax.set_ylabel(title + " (MB)")
    elif info.startswith("bytes_"):
        title = info.replace("_", " ")
        title = title.replace("recv", "received")
        title = title.capitalize() + " on eth0"
        ax.set_title(title)
        ax.set_ylabel(title + " (bytes)")
    

# plt.gcf().autofmt_xdate()   # beautify xlabels, but doesn't apply to figure with multiple subplots, rotate xtick labels manually instead
# # plt.subplots_adjust(hspace=1.2) # incompatible when constrained_layout=True
# plt.tight_layout()                # incompatible when constrained_layout=True
plt.show()
# fig.savefig("timeseries.pdf")


# print(pandas.to_datetime("2021-03-10 00:10:48.956275", format="%Y-%m-%d %H:%M:%S.%f"))




