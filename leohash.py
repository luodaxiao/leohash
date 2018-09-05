import sys
from math import log10


#base64编码顺序。
#decodemap:解码索引
__base64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/+'
__decodemap2 = {}
for i in range(len(__base64)):
    __decodemap2[__base64[i]] = i
del i


def encode(latitude, longitude, precision=12):
    '''
    step1: cut whole longtitudes into 2 parts:left part(L) and right part(R).
    step2: everytime cut cube into 64 parts(8*8)
    '''
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    leohash = []
    bits = [ 32,16, 8, 4, 2, 1 ]
    bit = 0
    ch = 0
    even = True

    if len(leohash)==0:
        mid =(lon_interval[0] + lon_interval[1]) / 2
        if longitude > mid:
            leohash+="R" 
            lon_interval = (0.0, 180.0)                                                               
        else:
            leohash+="L" 
            lon_interval = (-180.0,0.0) 
    else:
        pass

    while len(leohash) < precision:
        if even:
            mid =(lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch|=bits[bit]
                lon_interval = (mid, lon_interval[1])                                                               
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= bits[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 5:
            bit += 1
        else:
            leohash += __base64[ch]
            bit = 0
            ch = 0
    return ''.join(leohash)

def decode_exactly(leohash):
    """
    Decode to its exact values, including the error
    margins of the result.  Returns four float values: latitude,
    longitude, the plus/minus error for latitude (as a positive
    number) and the plus/minus error for longitude (as a positive
    number).
    """
    lat_interval = (-90.0, 90.0)  
    lat_err, lon_err = 90.0, 90.0
    if leohash[0]=="R":
        lon_interval=(0, 180.0)
    if leohash[0]=="L":
        lon_interval=(-180.0,0)

    is_even=True   
    for c in leohash[1:]:
        cd = __decodemap2[c]
        for mask in [32,16, 8, 4, 2, 1]:
            if is_even: # adds longitude info
                lon_err /= 2
                if cd & mask:
                    lon_interval = ((lon_interval[0]+lon_interval[1])/2, lon_interval[1])
                else:
                    lon_interval = (lon_interval[0], (lon_interval[0]+lon_interval[1])/2)
            else:      # adds latitude info
                lat_err /= 2
                if cd & mask:
                    lat_interval = ((lat_interval[0]+lat_interval[1])/2, lat_interval[1])
                else:
                    lat_interval = (lat_interval[0], (lat_interval[0]+lat_interval[1])/2)
            is_even = not is_even
    lat = (lat_interval[0] + lat_interval[1]) / 2
    lon = (lon_interval[0] + lon_interval[1]) / 2
    return lat, lon, lat_err, lon_err

def decode(leohash):
    """
    Decode geohash, returning two strings with latitude and longitude
    containing only relevant digits and with trailing zeroes removed.
    """
    lat, lon, lat_err, lon_err = decode_exactly(leohash)
    # Format to the number of decimals that are known
    lats = "%.*f" % (max(1, int(round(-log10(lat_err)))) - 1, lat)
    lons = "%.*f" % (max(1, int(round(-log10(lon_err)))) - 1, lon)
    if '.' in lats: lats = lats.rstrip('0')
    if '.' in lons: lons = lons.rstrip('0')
    return lats, lons
