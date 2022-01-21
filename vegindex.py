def ndvi(red, nir):
    _ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)
    return _ndvi


def ndwi(green, nir):
    '''
    https://en.wikipedia.org/wiki/Normalized_difference_water_index
    '''
    _ndwi = (green.astype(float) - nir.astype(float)) / (green + nir)
    return _ndwi


def evi(red, blue, nir, gain=2.5, c1=6, c2=7.5, l=1):
    '''
    https://en.wikipedia.org/wiki/Enhanced_vegetation_index
    '''
    _evi = gain * (nir.astype(float) - red.astype(float)) / ((nir + c1 * red) - (c2 * blue + l))
    return _evi


def evi2(red, nir, gain=2.5, c=2.4, l=1.0):
    '''
    https://en.wikipedia.org/wiki/Enhanced_vegetation_index
    '''
    _evi = gain * ((nir.astype(float) - red.astype(float)) / (nir + (c * red) + l))
    return _evi


def savi(red, nir, l=0.5):
    '''
    https://en.wikipedia.org/wiki/Soil-adjusted_vegetation_index
    '''
    _savi = ((1 + l) * (nir.astype(float) - red.astype(float))) / (nir + red + l)
    return _savi


def wdrvi(red, nir, alpha=0.1):
    '''
    https://www.sciencedirect.com/science/article/abs/pii/S0176161704705726
    '''
    _wdrvi = alpha * ndvi(red, nir)
    return _wdrvi


def cigreen(green, nir):
    '''
    https://www.indexdatabase.de/db/i-single.php?id=128
    '''
    _cigreen = nir.astype(float) / green.astype(float) - 1
    return _cigreen