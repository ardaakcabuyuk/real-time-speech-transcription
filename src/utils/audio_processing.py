BITMASK = 1
NIBMASK = 0XF
BYTMASK = 0XFF

NIBSHIFT= 4
BYTSHIFT= 8

def u_law_d(i8bit: int) -> int:
    '''
    Decodes 8 bit u-law encoded data to 16 bit PCM data.
    '''
    i8bit &= 0xff # marginalising data larger than byte
    i8bit ^= 0xff #flipping back bytes
    sign = False

    if i8bit&0x80==0x80: # if it is signed negative 1000 0000
        sign = True # bool option since sign is not really used
        i8bit &= 0x7f # removing the sign of value
    
    pos = ( (i8bit&0xf0) >> 4 )+5 # grabing initial value for mantisa
    
    # generating decoded data
    decoded = i8bit&0xf # grabing 1st nibble from 8 bit integer
    decoded <<= pos-4   # shifting by position -4 aka generating mantisa for 16 bit integer
    decoded |= 1 << ( pos-5 ) # OR gate for specific bit
    decoded |= 1<<pos   # OR gate for another specific bit
    decoded -= 0x21 # removing the 10 0001 from value to generate exact value

    if not sign:
        return decoded  # if positive number will be returned as is

    return -decoded # if negative the number will be returned inverted
    
def u_law_e(i16bit: int) -> int: 
    '''
    Encodes 16 bit PCM data to 8 bit u-law encoded data.
    '''
    i16bit &= 0x3fff # strips data bigger than 14 bits

    pos = 12        # position is 12 since we are not calculating sign bit and 0 value
                    # so 14 - sign == 13; so 13 bits, - 0 value ... 12 bits

    msk = 0x1000    # mask 1 0000 0000 0000 # bitwise mask for singular bits

    sign = 0x80 if i16bit&0x2000 else 0 # generating 8bit sign from 14 bit number 

    if sign == 0x80: # if sign is present
        i16bit = _twos_compliment(i16bit) # twos_compliment 
        i16bit &= 0x3ffe               # strips all bits larger than 14 bits

    i16bit+=0b100001                    # adds 33, 0x21 = 10 0001

    if i16bit > 0x1fff: i16bit = 0x1fff # if number is over maximum ... it becomes maximum

    for x in reversed( range(pos) ):    # this number has least significant bits, not bit... so they have often size of 4 bits, that is why it must be larger than 5
        if (i16bit & msk)!=msk and pos>=5:
            pos = x
            msk >>=1

    LSBTS = ( i16bit >> (pos-4) )&0xf # grabbing mantissa from 16 bit integer

    encoded = sign          # sign
    encoded += (pos-5)<<4    # exponent
    encoded += LSBTS        # mantisa

    return encoded^0xff # inverting all bits

def _twos_compliment(int_numb: int) -> int:
    if not int_numb: return ~int_numb

    lsb = _least_significant_bit(int_numb)
    msb = _most_significant_bit(int_numb)
    mask = ( 1<<lsb )-1
    mask ^= ( 1<<msb )-1
    return int_numb^mask

def _least_significant_bit(int_numb: int) -> int: ##returns position of the bit not the value of the bit
    if int_numb == 0 : return 0
    pos = 0
    while 1:
        if int_numb&(BITMASK<<pos)!=0:return pos+1
        pos+=1

def _most_significant_bit(int_numb: int) -> int:
    BYTSHIFT = 8
    mask    = 0x8000000000000000
    chk_msk = 0xff00000000000000
    pos = 64
    while 1:
        if int_numb&chk_msk==0:
            chk_msk     >>= BYTSHIFT
            mask        >>= BYTSHIFT
            pos         -=  BYTSHIFT
        else:
            if int_numb&mask==0:
                mask >>= BITMASK
                pos   -= BITMASK
            else:
                break

        if pos == 0:break
    return pos
