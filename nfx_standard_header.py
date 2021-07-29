from typing import List

from c_dtype_utils import decode_uint32


class NEURAL_NFX_STANDARD_HEADER:

    def __init__(self):

        self.file_type_id:                  str         = None
        self.file_spec:                     List[str]   = None
        self.num_bytes_in_header:           int         = None
        self.label:                         str         = None
        self.comments:                      str         = None
        self.application_to_create_file:    str         = None
        self.processor_timestamp:           int         = None
        self.period:                        int         = None
        self.time_resolution_of_time_stamps:int         = None
        self.time_origin:                   str         = None
        self.channel_count:                 int         = None

    def decodeHeader(self, data_file: bytes ) -> bytes:

        self.file_type_id       = data_file[0:8].decode('utf-8')
        data_file = data_file[8:]
        print("File type ID : " , self.file_type_id)

        self.file_spec          = [ str ( data_file[0] ), str( data_file[1] ) ]
        data_file = data_file[2:]
        print("File Spec: " , self.file_spec)

        self.num_bytes_in_header    = decode_uint32(data_file[0:4])
        data_file = data_file[4:]
        print("Number of bytes in the header: " , self.num_bytes_in_header)

        self.label              = data_file[0:16].decode('utf-8')
        data_file = data_file[16:]
        print("Label: ", self.label)

        self.comments           = data_file[0:200].decode('utf-8')
        data_file = data_file[200:]
        print("Comments: ", self.comments)

        self.application_to_create_file = data_file[0:52].decode('utf-8')
        data_file = data_file[52:]
        print("Application to create file: " , self.application_to_create_file)

        self.processor_timestamp    = decode_uint32(data_file[0:4])
        data_file = data_file[4:]
        print("Processor Timestamp: ", self.processor_timestamp )

        self.period                 = decode_uint32(data_file[0:4])
        data_file = data_file[4:]
        print("Period: " , self.period)

        self.time_resolution_of_time_stamps    = decode_uint32(data_file[0:4])
        data_file = data_file[4:]
        print("Time resolution of timestamps: " , self.time_resolution_of_time_stamps)

        self.time_origin    = "TODO"
        #self.time_origin    = data_file[0:16].decode('utf-8')
        data_file = data_file[16:]
        print("Time origin : /// TODO : while saved as a string at the moment, this is  Windows SYSTEM TIME structure: " + self.time_origin )

        self.channel_count  = decode_uint32(data_file[0:4])
        data_file = data_file[4:]
        print("Number of channels: ", self.channel_count )

        return data_file