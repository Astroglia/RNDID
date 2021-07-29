from bitarray import bitarray
from bitarray.util import ba2int
import struct

def byte_to_bstring(input_int: int) -> str:
    return "{:08b}".format( input_int )

def decode_uint32( uint32_as_uint8: bytes ):
    if len( uint32_as_uint8 ) < 4: return None

    uint32_extracted_bin = byte_to_bstring(uint32_as_uint8[3]) + byte_to_bstring(uint32_as_uint8[2]) + \
                           byte_to_bstring(uint32_as_uint8[1]) + byte_to_bstring(uint32_as_uint8[0])

    extracted_int =  ba2int( bitarray( uint32_extracted_bin ), signed = False )

    return extracted_int


def decode_uint16( uint16_as_uint8: bytes ):
    if len( uint16_as_uint8 ) < 2:  return None

    uint16_extracted_bin = byte_to_bstring(uint16_as_uint8[1]) + byte_to_bstring(uint16_as_uint8[0])

    extracted_int = ba2int( bitarray( uint16_extracted_bin ), signed= False )

    return extracted_int

def decode_int16(int16_as_int8: bytes):
    if len(int16_as_int8) < 2:  return None

    int16_extracted_bin = byte_to_bstring(int16_as_int8[1]) + byte_to_bstring(int16_as_int8[0])

    extracted_int = ba2int( bitarray( int16_extracted_bin ), signed= True )

    return extracted_int

def decode_32bit_float( btfloat: bytes ):
    if len(btfloat) < 4:    return None
    return struct.unpack('f', btfloat )[0]

    # bstring_float       = byte_to_bstring( btfloat[3] ) + byte_to_bstring( btfloat[2] ) + byte_to_bstring( btfloat[1] ) + byte_to_bstring( btfloat[0] )
    #
    # exponent = bstring_float[1:9]
    # mantissa = bstring_float[]
