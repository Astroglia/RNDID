from typing import List

from nfx_standard_header import NEURAL_NFX_STANDARD_HEADER
from c_dtype_utils import decode_uint16, decode_int16, decode_uint32


class NEURAL_NFX_EXTENDED_HEADER_INDIVIDUAL:
    def __init__(self):
        ############################################################## additional data the python library provides
        self.electrode_number:  int = None
        ############################################################## from data file
        self.type:          str = None
        self.electrode_id:  int = None
        self.electrode_label:   str = None
        self.front_end_id:      str = None
        self.front_end_connector_pin:   str = None
        self.min_digital_value:         int = None
        self.max_digital_value:         int = None
        self.min_analog_value:          int = None
        self.max_analog_value:          int = None
        self.units:                     str = None
        self.high_pass_corner_frequency:int = None
        self.high_pass_filter_order:    int = None
        self.high_pass_filter_type:     int = None
        self.low_pass_corner_frequency: int = None
        self.low_pass_filter_order:     int = None
        self.low_pass_filter_type:      int = None

    def decode_from_truncated_data_file(self, electrode_number: int, data_file: bytes ) -> bytes :
        self.electrode_number = electrode_number
        st_electrode_str = "ELECTRODE: " + str(self.electrode_number) + " : "

        self.type       = data_file[0:2].decode('utf-8')
        data_file       = data_file[2:]
        print( st_electrode_str, "type: ",  self.type)

        self.electrode_id = decode_uint16( data_file[0:2] )
        data_file       = data_file[2:]
        print( st_electrode_str, "electrode ID : ", self.electrode_id )

        self.electrode_label = data_file[0:16].decode('utf-8')
        data_file       = data_file[16:]
        print( st_electrode_str, "electrode label : ", self.electrode_label )

        self.front_end_id   = bytearray(data_file[0]).decode('utf-8')
        data_file       = data_file[1:]
        print( st_electrode_str, "front end id : ", self.front_end_id )

        self.front_end_connector_pin   = bytearray(data_file[0]).decode('utf-8')
        data_file       = data_file[1:]
        print( st_electrode_str, "front end connector pin : ", self.front_end_connector_pin )

        self.min_digital_value      = decode_int16( data_file[0:2] )
        data_file       = data_file[2:]
        print( st_electrode_str, "min digital value : ", self.min_digital_value )

        self.max_digital_value      = decode_int16( data_file[0:2] )
        data_file       = data_file[2:]
        print( st_electrode_str, "max digital value : ", self.max_digital_value )

        self.min_analog_value      = decode_int16( data_file[0:2] )
        data_file       = data_file[2:]
        print( st_electrode_str, "min analog value : ", self.min_analog_value )

        self.max_analog_value      = decode_int16( data_file[0:2] )
        data_file       = data_file[2:]
        print( st_electrode_str, "max analog value : ", self.max_analog_value )

        self.units      = data_file[0:16].decode('utf-8')
        data_file       = data_file[16:]
        print( st_electrode_str, "units for max/min digital/analog values : ", self.units )

        self.high_pass_corner_frequency     = decode_uint32( data_file[0:4] )
        data_file       = data_file[4:]
        print( st_electrode_str, "high pass corner frequency in mHz : ", self.high_pass_corner_frequency )

        self.high_pass_filter_order         = decode_uint32( data_file[0:4] )
        data_file       = data_file[4:]
        print( st_electrode_str, "high pass filter order : ", self.high_pass_filter_order )

        self.high_pass_filter_type          = decode_uint16( data_file[0:2] )
        data_file       = data_file[2:]
        print( st_electrode_str, "high pass filter type (0=None, 1=Butterworth, 2=Chebyshev) : ", self.high_pass_filter_type )

        self.low_pass_corner_frequency     = decode_uint32( data_file[0:4] )
        data_file       = data_file[4:]
        print( st_electrode_str, "low pass corner frequency in mHz : ", self.low_pass_corner_frequency )

        self.low_pass_filter_order         = decode_uint32( data_file[0:4] )
        data_file       = data_file[4:]
        print( st_electrode_str, "low pass filter order : ", self.low_pass_filter_order )

        self.low_pass_filter_type          = decode_uint16( data_file[0:2] )
        data_file       = data_file[2:]
        print( st_electrode_str, "low pass filter type (0=None, 1=Butterworth, 2=Chebyshev) : ", self.low_pass_filter_type )

        return data_file

class NEURAL_NFX_EXTENDED_HEADER_GROUP:
    def __init__(self):
        self.extended_header_group:     List[NEURAL_NFX_EXTENDED_HEADER_INDIVIDUAL] = None

    def decode_header_group(self, truncated_data_file: bytes, standard_header: NEURAL_NFX_STANDARD_HEADER) -> bytes:
        """
            decode headers for all the electrodes from an .NFX data file
        :param truncated_data_file:     data file with the standard header truncated off of it (so it begins at the first individual electrode header)
        :param standard_header:         the standard header for the truncated data file
        :return:                        data file with individual headers truncated off of it (so now the data file should just be recording data)
        """
        self.extended_header_group = []

        ## iterate each electrode channel and extract the header information for that electrode

        for i in range( standard_header.channel_count ) :

            individual_header = NEURAL_NFX_EXTENDED_HEADER_INDIVIDUAL()

            truncated_data_file = individual_header.decode_from_truncated_data_file( i, truncated_data_file )

            self.extended_header_group.append( individual_header )

        return truncated_data_file