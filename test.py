import nfx_extended_header
from nfx_data_decoder import NEURAL_NFX_DATA_DECODE
from nfx_standard_header import NEURAL_NFX_STANDARD_HEADER

data = None



with open( 'vroomvroomTEST.nf3', 'rb' ) as cFile:
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
# for packet in data_decoder.decoded_data_packets:
#     print( packet.to_string() )
