from queue import Queue
from typing import Union, List

import numpy as np

from PySide2 import QtCore, QtWidgets, QtGui

import sys
import threading
import time

from PySide2.QtCore import QFile, QObject, Signal, Slot, QTimer
from PySide2.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide2.QtUiTools import QUiLoader

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MatplotlibWidget(QWidget):
    def __init__(self , parent=None):
        super().__init__(parent)
        self.data_queue: Queue[ np.ndarray ] = Queue()

        self.stream_figure = None
        self.canvas = None
        self.toolbar = None

        self._init_stream()
        self._init_widget()
        self._init_device_properties()
        self.offsets = 200

        self.axis_one = self.stream_figure.add_subplot(111)
        self._setup_axes()
        self.line, *_ = self.axis_one.plot([])

        self.data_thread_obj = threading.Thread(target=self._monitor_data)
        self.data_thread_obj.start()

    ##################################################################
    ################### UPDATING
    #
    def plot_new_data(self, data: Union[ np.ndarray, List ] ):
        if type( data ) is list:
            data = self.format_list_data( data )        # TODO implement
        self.data_queue.put( data )
    def _monitor_data(self):
        while True :
            if self.data_queue.qsize() > 0:
                self._plot_new_data( self.data_queue.get() )
                time.sleep(0.1)

    def _plot_new_data(self, input_data: np.ndarray ):
        #################################################################################   format data
        formatted_plot_data = input_data
        dshape = input_data.shape
        if dshape[0] == self.channels:
            formatted_plot_data = input_data.reshape( [ dshape[-1], dshape[0] ]  )
        #################################################################################   push new data to the plot (TODO this probably causes expensive redraws)
        formatted_plot_data = self._offset(formatted_plot_data, self.offsets, self.channels)  # offset so minimal overlapping of data occurs.
        self._shift_current_data_multi(formatted_plot_data)
        self._shift_time(formatted_plot_data.shape[1])                                          # shift the time axis onto the plot

        self.set_data(self.channels, self.time_axis, self.current_data, self.data_line_set)
        #   self.axis_one.set_xlim( 0, new_data.shape[1])
        self.axis_one.set_xlim(self.time_axis[0], self.time_axis[-1])                           # shift time axis xlimits to ensure new data shows

        #  plt.xlim(self.time_axis[0], self.time_axis[-1])
        # self.canvas.draw()
        ##################################################################################  canvas i/o
        self.stream_figure.canvas.draw()
        self.stream_figure.canvas.flush_events()



    ##################################################################
    ################### INITIALIZATION

    def _init_device_properties(self):
        self.channels = 8
        self.points_to_plot = 3000
        self.current_data = np.random.random_integers(low=-2000, high=2000, size=(self.channels, self.points_to_plot))
        self.time_axis = np.array(list(range(self.points_to_plot)))
        self.time_axis_latest = 0

    def _init_stream(self):
        INTERACTIVE_ON = plt.ion()
        plt.style.use('dark_background')
        self.stream_figure = Figure(figsize=(12, 12), dpi=65)
        self.canvas = FigureCanvas(self.stream_figure)

    # self.toolbar = NavigationToolbar(self.canvas, self)
    def _init_widget(self):
        self.layout = QVBoxLayout(self)
        # self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        ########################################### PLOTTING HELPER FUNCTIONS #################################################

    def _offset(self, data, offset_amount, channels):
        if data is not None:
            temp_offset = offset_amount * int(channels / 2)
            for i in range(data.shape[0]):
                data[i, :] = data[i, :] + temp_offset
                temp_offset = temp_offset - offset_amount
        return data

    def set_data(self, channels, time_axis, data, line_set):
        for i in range(channels):
            line_set[i].set_data(time_axis, data[i, :])

    def _shift_time(self, new_data_shape):
        # self.time_axis = np.array(list(range(new_data_shape)))
        self.time_axis = np.array( list(range(self.time_axis_latest + new_data_shape, self.time_axis_latest + self.current_data.shape[1] + new_data_shape)))
        self.time_axis_latest = self.time_axis_latest + new_data_shape

    def _shift_current_data_multi(self, new_data, is_predictions=False):
        #  self.current_data = new_data
        data_shifted = self.current_data[0:self.channels, new_data.shape[1]:self.current_data.shape[1]]
        self.current_data = np.concatenate([data_shifted, new_data], axis=1)

    def _setup_axes(self):
        plt.ylim((-1000, 1000))

        self.axis_one.grid('grid', linestyle="-.", color='mediumslateblue', axis='y')
        self.axis_one.spines['right'].set_visible(False)
        self.axis_one.spines['left'].set_visible(False)
        self.axis_one.spines['bottom'].set_visible(False)
        self.axis_one.spines['top'].set_visible(False)
        self.axis_one.tick_params(direction='in', length=10, width=2, colors='mediumslateblue',
                                  grid_color='mediumslateblue', grid_alpha=0.5)

        self.data_line_set = []

        color_legend = ['lightpink', 'lightblue', 'crimson', 'linen', 'purple', 'salmon', 'limegreen', 'deeppink']
        for i in range(self.channels):
            data_line, = self.axis_one.plot(self.time_axis, self.current_data[i, :], color=color_legend[i], linewidth=0.4)  # just plot nothing first.
            self.data_line_set.append(data_line)


class dataStream:
    def __init__(self):
        self.testtextedit = QtWidgets.QTextEdit(" ")
        self.testtextedit.setProperty("class", "dataStreamPanel")

        self.data_stream_plot = MatplotlibWidget()
        self.data_stream_plot.show()

        self.data_stream_widgets = [self.data_stream_plot]


class dataStreamTester:
    def __init__(self, channels_to_plot: int = 8, sampling_frequency: int = 2000):
        self.channels_to_plot   = channels_to_plot
        self.sampling_frequency = sampling_frequency

        rise    = np.linspace( 0, 1, self.sampling_frequency )          # linear rise to 1
        rise    = np.expand_dims( rise, 0 )                             # add dim for stacking
        decay   = rise[::-1]                                            # linear fall to 0
        concat  = np.concatenate( rise, decay, axis= 1 )                # rise / fall sequence

        for i in range( channels_to_plot ):                             # copy for all electrodes.
            concat = np.concatenate( concat, axis = 0 )

        # we want to add new data available every ~20 milliseconds, so:
        # take the sampling frequency to get 20 milliseconds # of datapoints, split the data into that
        self.plotting_interval_ms = 0.02
        num_datapoints_in_20ms = sampling_frequency * self.plotting_interval_ms

        self.concat_split_list: List[np.ndarray] = [  ]

        try:
            for i in range( 0, concat.shape[1], int(num_datapoints_in_20ms) ):
                self.concat_split_list.append( concat[ ..., i:(i+num_datapoints_in_20ms) ] )
        except IndexError:
            print("index error splitting concat list; still moving along")

        self.is_plotting = True
        self.dthread = threading.Thread(target=self._dplotter)

    def begin_plotting(self):
        self.is_plotting = True
        self.dthread.start()

    def _dplotter(self):
        while self.is_plotting:
            currplot = self.concat_split_list.pop()
            # TODO plot
            self.concat_split_list.append( currplot )
            time.sleep( self.plotting_interval_ms )
