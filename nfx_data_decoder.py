from typing import List

import c_dtype_utils
from nfx_extended_header import NEURAL_NFX_EXTENDED_HEADER_GROUP
from nfx_standard_header import NEURAL_NFX_STANDARD_HEADER


class NEURAL_NFX_DATA_SINGLE_PACKET:
    def __init__(self, packet_segment: bytes, channels: int):
        self.header:    int = None
        self.timestamp: int = None
        self.number_of_datapoints:  int = None
        self.data_point:            List[float] = []
        self.channels:              int = channels

        self.raw_packet:    bytes = packet_segment

    def decode_packet(self):
        self.header                 = self.raw_packet[0]
        self.raw_packet = self.raw_packet[1:]

        self.timestamp      = c_dtype_utils.decode_uint32( self.raw_packet[0:4] )
        self.raw_packet = self.raw_packet[4:]

        self.number_of_datapoints = c_dtype_utils.decode_uint32( self.raw_packet[0:4] )
        self.raw_packet = self.raw_packet[4:]

        for i in range( self.channels ):
            self.data_point.append( c_dtype_utils.decode_32bit_float( self.raw_packet[0:4] ) )
            self.raw_packet = self.raw_packet[4:]

        #self.timestamp              = c_dtype_utils.decode_uint32( self.raw_packet[1:5] )
        #self.number_of_datapoints   = c_dtype_utils.decode_uint32( self.raw_packet[5:9] )
        #temp = self.raw_packet[9:]
        #for i in range( self.channels ):
        #    self.data_point.append( c_dtype_utils.decode_32bit_float( temp[0:4] ) )
        #    temp = temp[4:]

    def to_string(self):
        print(" header : ",     self.header )
        print(" timestamp : ",  self.timestamp )
        print(" # datapoints :", self.number_of_datapoints )
        print(" datapoint (from each electrode): ", self.data_point )
        print(" channels ", self.channels )


class NEURAL_NFX_DATA_DECODE:
    def __init__(self, standard_header: NEURAL_NFX_STANDARD_HEADER, extended_header: NEURAL_NFX_EXTENDED_HEADER_GROUP):
        self.decoded_data_packets:      List[NEURAL_NFX_DATA_SINGLE_PACKET] = []

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
            print("---------------------------------------------------------------------------------------------------------------------------------")

        try:
            for i in range( 0, len(truncated_data_file), single_packet_length ):
                data_packet = NEURAL_NFX_DATA_SINGLE_PACKET(truncated_data_file[i:(i + single_packet_length)], self.header.channel_count)
                data_packet.decode_packet()
                self.decoded_data_packets.append( data_packet )
        except IndexError:
            print(" error occured with decoding data. Amount of data packets decoded: ", len(self.decoded_data_packets) )
