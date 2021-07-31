from typing import List, Iterable
import numpy as np
import c_dtype_utils
from nfx_extended_header import NEURAL_NFX_EXTENDED_HEADER_GROUP
from nfx_standard_header import NEURAL_NFX_STANDARD_HEADER

# TODO:
    # - timestamp management
    # - electrode ID association with bulk data ( even though its 1:1, should still have something that states this )

class NEURAL_NFX_ELECTRODE_DATA:
    def __init__(self):
        self.data:          List[float] = []
        self.electrode_id:  str         = None

class NEURAL_NFX_ELECTRODE_BULK_DATA:
    def __init__( self, electrode_list_data: List[NEURAL_NFX_ELECTRODE_DATA]) :
        dat_arrs = [ x.data for x in electrode_list_data ]
        min_list_len =  min(map(len, dat_arrs))
        electrode_list_data = [ x[0:min_list_len] for x in dat_arrs  ]

        self.numpy_data = np.array(electrode_list_data)

class NEURAL_NFX_DATA_SINGLE_PACKET:
    def __init__(self, channels: int):
        self.header:                int = None

        self.packet_start_timestamp:int = None

        self.number_of_datapoints:  int = None

        self.all_electrode_data:    List[ NEURAL_NFX_ELECTRODE_DATA ] = [ NEURAL_NFX_ELECTRODE_DATA() for i in range(channels ) ]
        # TODO after electrode bulk data has been populated, get rid of all-electrode-data to save memory
        self.electrode_bulk_data:   NEURAL_NFX_ELECTRODE_BULK_DATA  = None

        self.channels:              int = channels

        self.dpoint_set_skip:       int = int( self.channels * 4 )

    def decode_single_datapoint_set(self, data: bytes ):
        current_electrode = 0
        for i in range( 0, len(data), 4 ):
            self.all_electrode_data[ current_electrode ].data.append( c_dtype_utils.decode_32bit_float( bytearray(data[ i:(i+4) ])[::-1] ) )
            current_electrode+=1

    def decode_packet(self, data: bytes ):
        self.header     = data[0]
        data = data[1:]

        self.packet_start_timestamp      = c_dtype_utils.decode_uint32( data[0:4] )
        data = data[4:]

        self.number_of_datapoints       = c_dtype_utils.decode_uint32( data[0:4] )
        data = data[4:]

        if ( (len(data)-1) % self.number_of_datapoints) != 0:
            print(" warning - channel datasets may not have equivalent lengths ")

        try:
            for i in range(0, len(data), self.dpoint_set_skip):
                self.decode_single_datapoint_set(data[i:(i + self.dpoint_set_skip)])
        except IndexError:
            print( "index error @ index : ", i )
            pass

        self.electrode_bulk_data = NEURAL_NFX_ELECTRODE_BULK_DATA( self.all_electrode_data )

        # self.number_of_datapoints = c_dtype_utils.decode_uint32( self.raw_packet[0:4] )
        # self.raw_packet = self.raw_packet[4:]
        #
        # for i in range( self.channels ):
        #     self.data_point.append( c_dtype_utils.decode_32bit_float( self.raw_packet[0:4] ) )
        #     self.raw_packet = self.raw_packet[4:]

        #self.timestamp              = c_dtype_utils.decode_uint32( self.raw_packet[1:5] )
        #self.number_of_datapoints   = c_dtype_utils.decode_uint32( self.raw_packet[5:9] )
        #temp = self.raw_packet[9:]
        #for i in range( self.channels ):
        #    self.data_point.append( c_dtype_utils.decode_32bit_float( temp[0:4] ) )
        #    temp = temp[4:]

    def to_string(self):
        print(" header : ",     self.header )
        print(" timestamp : ",  self.packet_start_timestamp )
        print(" # datapoints :", self.number_of_datapoints )
        print(" channels ", self.channels )

    def print_data(self):
        # for i in range( 1, len( self.all_electrode_data[5].data ) ):
        #     if abs(self.all_electrode_data[5].data[i - 1] - self.all_electrode_data[5].data[i]) > 5000:
        #         print( self.all_electrode_data[5].data[i] )
        print( max( self.all_electrode_data[5].data ) )
        print( min( self.all_electrode_data[5].data ) )

        # for i in self.all_electrode_data[0].data:
        #     print(i)
        # for i in range( self.all_electrode_data[0].data )
        #
        # for i in range( self.channels)


class NEURAL_NFX_DATA_DECODE:
    def __init__(self, standard_header: NEURAL_NFX_STANDARD_HEADER, extended_header: NEURAL_NFX_EXTENDED_HEADER_GROUP):
        self.decoded_data_packets:      List[NEURAL_NFX_DATA_SINGLE_PACKET]     = []

        self.header             = standard_header
        self.extended_header    = extended_header

    def decode_dataset(self, truncated_data_file: bytes ):
        header_bytecount    = 1
        tstamp_bytecount    = 4
        num_datapoint_bytecount = 4
        data_bytecount          = int( 4 * self.header.channel_count )      # 4 bytes per datapoint, number of datapoints is # of channels

        single_packet_length = header_bytecount + tstamp_bytecount + num_datapoint_bytecount + data_bytecount

        if int( len(truncated_data_file) % single_packet_length) != 0 :
            print("---------------------------------------------------------------------------------------------------------------------------------")
            print("warning - data size does not divide up correctly; may have (overall) incorrect data or corruption near the end of the data file.")
            print(" data file length: ", len(truncated_data_file) )
            print(" single data packet length", single_packet_length )
            print(" After decoding all electrode data is converted to a numpy array. the list with the least amount of data will be what all data is \n truncated to")
            print("---------------------------------------------------------------------------------------------------------------------------------")

        data_packet = NEURAL_NFX_DATA_SINGLE_PACKET( self.header.channel_count )
        data_packet.decode_packet( truncated_data_file )

        self.decoded_data_packets.append( data_packet )

        # try:
        #     for i in range( 0, len(truncated_data_file), single_packet_length ):
        #         print( i )
        #         print( i + single_packet_length )
        #         data_packet = NEURAL_NFX_DATA_SINGLE_PACKET(truncated_data_file[i:(i + single_packet_length)], self.header.channel_count)
        #         data_packet.decode_packet()
        #         self.decoded_data_packets.append( data_packet )
        # except IndexError:
        #     print(" error occured with decoding data. Amount of data packets decoded: ", len(self.decoded_data_packets) )
