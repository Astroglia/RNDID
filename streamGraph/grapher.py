from queue import Queue
from typing import Union, List

import matplotlib
import numpy as np

import sys
import threading
import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


## works on any dimensional image.
def normalize_numpy_array(numpy_img, cap_outliers=False, checknan: bool = False ):
    if checknan:
        nan_data = np.isnan( numpy_img )
        numpy_img[nan_data] = 0
#        numpy_img[nanLocals] = np.average( numpy_img )
    if cap_outliers:
        mean = np.mean(numpy_img.flatten())  # Get mean/sdev
        sdev = np.std(numpy_img.flatten())
        if cap_outliers:
            thresh = mean + sdev + sdev
            numpy_img_threshold = numpy_img > thresh  # Exclude large values > 2 sdev
            numpy_img[numpy_img_threshold] = thresh

    numpy_img = (numpy_img - np.min(numpy_img)) / (np.max(numpy_img) - np.min(numpy_img))
    return numpy_img


class MatplotlibWidget:
    def __init__(self, num_channels: int = 8, sampling_frequency: int = 1000):
        self.data_queue: Queue[ np.ndarray ] = Queue()

        self.canvas = None
        self.toolbar = None

        self.offsets = 200
        self.num_channels       = num_channels
        self.points_to_plot     = sampling_frequency * 5
        if self.points_to_plot > 5000:
            self.points_to_plot = 5000
        self.graph_dataset      = np.random.random_integers(low=-2000, high=2000, size=(self.num_channels, self.points_to_plot))
        self.graph_dataset      = self.graph_dataset * 0
        self.time_axis          = np.array(list(range(self.points_to_plot)))
        self.time_axis_latest   = 0


        self.data_thread_obj = threading.Thread(target=self._monitor_data)
        self.data_thread_obj.start()

        matplotlib.use('GTK3Agg')
        INTERACTIVE_ON = plt.ion()  # set interactive mode on.
        plt.style.use('dark_background')  # pretty
        self._setup_axes()  ## setup the current axes
        plt.show()
        self.figure.show()
        self.figure.canvas.draw()  ## draw to the plot
        self.figure.canvas.flush_events()  ## and execute the drawing.
        print("DONE SETTING UP MATPLOTLIB PLOTTER")

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
                while self.data_queue.qsize() > 0:
                    self._plot_new_data( self.data_queue.get()*self.offsets )
            time.sleep(0.1)

    def _plot_new_data(self, input_data: np.ndarray ):
        #################################################################################   format data
        formatted_plot_data = input_data
        if (formatted_plot_data.shape[0] != self.graph_dataset.shape[0]) and (formatted_plot_data.shape[1] == self.graph_dataset.shape[1]):
            formatted_plot_data = np.swapaxes( formatted_plot_data, 0, 1)
        #################################################################################   push new data to the plot (TODO this probably causes expensive redraws)
        formatted_plot_data = self._offset(formatted_plot_data, self.offsets, self.num_channels)  # offset so minimal overlapping of data occurs.
        self._shift_graph_dataset(formatted_plot_data)
        self._shift_time(formatted_plot_data.shape[1])                                          # shift the time axis onto the plot

        self.set_channel_data(self.num_channels, self.time_axis, self.graph_dataset, self.data_line_set)
        #   self.axis_one.set_xlim( 0, new_data.shape[1])
        plt.xlim(self.time_axis[0], self.time_axis[-1])

        #  plt.xlim(self.time_axis[0], self.time_axis[-1])
        # self.canvas.draw()
        ##################################################################################  canvas i/o
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        ########################################### PLOTTING HELPER FUNCTIONS #################################################

    def _offset(self, data, offset_amount, channels):
        if data is not None:
            temp_offset = offset_amount * int(channels / 2) - offset_amount
            for i in range(data.shape[0]):
                data[i, :] = data[i, :] + temp_offset
                temp_offset = temp_offset - offset_amount
        return data

    def set_channel_data(self, channels, time_axis, data, line_set):
        for i in range(channels):
            line_set[i].set_data(time_axis, data[i, :])

    def _shift_time(self, new_data_shape):
        # self.time_axis = np.array(list(range(new_data_shape)))
        self.time_axis          = np.array(list(range(self.time_axis_latest + new_data_shape, self.time_axis_latest + self.graph_dataset.shape[1] + new_data_shape)))
        self.time_axis_latest   = self.time_axis_latest + new_data_shape

    def _shift_graph_dataset(self, new_data):
        self.graph_dataset = np.roll(self.graph_dataset, new_data.shape[1], 1)
        self.graph_dataset[... , (self.graph_dataset.shape[1] - new_data.shape[1]):self.graph_dataset.shape[1]] = new_data

    def _setup_axes(self):
        self.figure, (self.axis_one, self.axis_two) = plt.subplots(2,1 , sharey=True, sharex=True, figsize=(15,10), gridspec_kw={'height_ratios': [3, 1]}, num=2)
        plt.ylim( ( -self.num_channels*self.offsets / 1.5 , self.num_channels*self.offsets / 1.5 ))      # show all electrodes in range; allow a bit of padding (instead of /2)

        self.axis_one.grid('grid', linestyle="-.", color='mediumslateblue', axis='y')
        self.axis_two.grid('grid', linestyle="-.", color='mediumslateblue', axis='y')
        self.axis_one.spines['right'].set_visible(False)
        self.axis_one.spines['left'].set_visible(False)
        self.axis_one.spines['bottom'].set_visible(False)
        self.axis_one.spines['top'].set_visible(False)
        self.axis_one.tick_params(direction='in', length=10, width=2, colors='mediumslateblue', grid_color='mediumslateblue', grid_alpha=0.5)

        self.data_line_set = []
        self.prediction_line_set = []

        color_legend = ['lightpink', 'lightblue', 'crimson', 'linen', 'purple', 'salmon', 'limegreen', 'deeppink']
        for i in range(self.num_channels):
            data_line, = self.axis_one.plot(self.time_axis, self.graph_dataset[i, :], color=color_legend[i], linewidth=0.4)  # just plot nothing first.
            self.data_line_set.append(data_line)










class sequentialDataGrapher:
    def __init__( self, data: np.ndarray = None, data_channels: int = 8, sampling_frequency: int = 5000):
        """
        :param data_channels:           number of electrodes recorded
        :param sampling_frequency:      frequency the data is sampled at
        :param data:                    the (full) data array, at the moment ( TODO support dynamic input )
        """
        if data is None:
            data = self.get_test_dataset( data_channels, sampling_frequency )
        if data.ndim > 2:
            raise ValueError("only two dimension data arrays supported at the moment")
        if data.shape[1] == data_channels:
            data = np.swapaxes( data, 0, 1 )

        nan_data = np.isnan( data )
        data[nan_data] = 0

        # normalize dataset ; cap large outlier values
        data = normalize_numpy_array( data, cap_outliers = True  )

        # we want to add new data available every ~20 milliseconds, so:
        # take the sampling frequency to get 20 milliseconds # of datapoints, split the data into that
        self.plotting_interval_ms = 0.02
        num_datapoints_in_20ms = sampling_frequency * self.plotting_interval_ms

        self.concat_split_queue: Queue[ np.ndarray ] = Queue()

        try:
            for i in range( 0, data.shape[1], int(num_datapoints_in_20ms) ):
                self.concat_split_queue.put( data[ ..., i:(i+int(num_datapoints_in_20ms) ) ] )
        except IndexError:
            print("index error splitting concat list; still moving along")

        print("----------- data setup for plotting -----------")
        print("packet insertion shape: " + str([ data_channels, int(num_datapoints_in_20ms) ] ) )
        print("num packets before rollover: " + str( self.concat_split_queue.qsize() ) )
        print("packet insertion rate: " + str( self.plotting_interval_ms ) )
        print("-----------------------------------------------")

        self.is_plotting = False
        self.dthread = threading.Thread(target=self._dplotter)

        self.plot_interface     = MatplotlibWidget()


    def begin_plotting(self):
        self.is_plotting = True
        self.dthread.start()
    def stop_plotting(self):
        self.is_plotting = False
        self.dthread.join( 3.0 )

    def _dplotter(self):
        while self.is_plotting:
            currplot = self.concat_split_queue.get()
            self.plot_interface.plot_new_data( currplot.copy() )
            self.concat_split_queue.put( currplot )
            time.sleep( self.plotting_interval_ms )


    def get_test_dataset(self, num_channels: int , sampling_frequency: int):
        rise    = np.linspace( 0, 4, sampling_frequency )          # linear rise to 1
        rise    = np.sin( rise )
        decay   = rise[::-1]                                            # linear fall to 0
        concat  = np.concatenate(  (rise, decay) , axis= 0 )              # rise / fall sequence
        concat  = np.expand_dims( concat, 0 )                           # add dim for stacking
        concat_copy = concat.copy()
        for i in range( 1, num_channels ):                             # copy for all electrodes.
            concat = np.concatenate( (concat, concat_copy) )

        return concat