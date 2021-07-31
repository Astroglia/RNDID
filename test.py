import matplotlib.pyplot
import numpy as np

import nfx_extended_header
from nfx_data_decoder import NEURAL_NFX_DATA_DECODE
from nfx_standard_header import NEURAL_NFX_STANDARD_HEADER

from streamGraph import grapher

data = None



with open('example_data/baseline.nf3', 'rb') as cFile:
    data = cFile.readlines()

data_concat = data[0] + data[1]

standard_header     = NEURAL_NFX_STANDARD_HEADER()
truncated_datafile  = standard_header.decodeHeader( data_concat )
extended_header     = nfx_extended_header.NEURAL_NFX_EXTENDED_HEADER_GROUP()
truncated_datafile  = extended_header.decode_header_group( truncated_datafile, standard_header )

data_decoder        = NEURAL_NFX_DATA_DECODE( standard_header, extended_header )

data_decoder.decode_dataset( truncated_datafile )

dpacket = data_decoder.decoded_data_packets[0:10]
for d in dpacket:
    print( d.to_string() )
    print( d.print_data() )

bulk_data = data_decoder.decoded_data_packets[0].electrode_bulk_data.numpy_data

bulk_data = bulk_data[ 0:8, ... ]
bulk_data = grapher.normalize_numpy_array( bulk_data, cap_outliers= True, checknan = True )

matplotlib.pyplot.hist( bulk_data[3, ... ] )
matplotlib.pyplot.show()

#data_plotter = grapher.sequentialDataGrapher( data = bulk_data, data_channels = 8, sampling_frequency = 2000 )
#data_plotter.begin_plotting()


# for packet in data_decoder.decoded_data_packets:
#     print( packet.to_string() )
# testPlot = grapher.sequentialDataGrapher()
# testPlot.begin_plotting()






















