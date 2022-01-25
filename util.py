import numpy as np
from math import floor, ceil
from datetime import datetime as dt
from datetime import timedelta as td
from constants import MESHLIST

TIMEZERO = dt.strptime("1900-01-01", "%Y-%m-%d")


def ir(x):
    return int(round(x))


class Area:
    def __init__(self, name, num, s, n, w, e):
        self.name = name
        self.num = num
        self.s = s
        self.n = n
        self.w = w
        self.e = e

    def __str__(self):
        return self.name

    def __contains__(self, latlon):
        lat_buffer = 0.00833 / 2
        lon_buffer = 0.0125 / 2
        s = latlon.latmin * 1.5 + lat_buffer
        n = latlon.latmax * 1.5 - lat_buffer
        w = latlon.lonmin - 100.0 + lon_buffer
        e = latlon.lonmax - 100.0 - lon_buffer
        return self.s <= s and self.n + 1 >= n and self.w <= w and self.e + 1 >= e

    def extract(self, mesh):
        lat_orig = mesh.lat.bot * 1.5
        lon_orig = mesh.lon.bot - 100.0
        latsub = mesh.lat.sub * 2 / 3.0
        lonsub = mesh.lon.sub
        y0 = ir((self.s - lat_orig) * latsub)
        y1 = ir((self.n - lat_orig + 1) * latsub)  # -1
        x0 = ir((self.w - lon_orig) * lonsub)
        x1 = ir((self.e - lon_orig + 1) * lonsub)  # -1

        lat = mesh.lat.lin()[y0:y1]
        lon = mesh.lon.lin()[x0:x1]
        return y0, y1, x0, x1, lat, lon


AREAS = {
    "北海道": Area("北海道", 1, 59, 68, 39, 45),
    "東北": Area("東北", 2, 52, 62, 37, 42),
    "関東北陸": Area("関東北陸", 3, 48, 57, 35, 41),
    "西日本": Area("西日本", 4, 49, 54, 30, 37),
    "九州": Area("九州", 5, 43, 52, 28, 32),
    "西南諸島": Area("西南諸島", 6, 36, 43, 22, 31)
}


class LatLonDomain:
    def __init__(self, lonmin, latmin, lonmax, latmax):
        """2d-region: lonmin, latmin, lonmax, latmax"""
        self.latmin = latmin
        self.latmax = latmax
        self.lonmin = lonmin
        self.lonmax = lonmax
        self.check()

    def __str__(self):
        return str((self.latmin, self.latmax, self.lonmin, self.lonmax))

    def check(self):
        if self.latmin > self.latmax:
            raise ValueError("South:" + str(self.latmin) + " North:" + str(self.latmax))
        if self.lonmin > self.lonmax:
            raise ValueError("West:" + str(self.lonmin) + " East:" + str(self.lonmax))

    def get_area(self, areas=None):
        if areas is None:
            areas = AREAS
        matches = [a.num for a in areas.values() if self in a]
        if not matches:
            raise ValueError("No area containing " + str(self) + " found.")
        return "Area" + str(min(matches))

    def latrestrict(self, a):
        if self.latmin != self.latmax:
            b = (a >= self.latmin) & (a <= self.latmax)
        else:
            c = np.abs(a - self.latmin)
            v = np.min(c)
            b = (c == v)
            for i in range(len(b)):
                if b[i]:
                    if i < len(b) - 1:
                        b[i + 1] = False
                    break
        return b

    def lonrestrict(self, a):
        if self.lonmin != self.lonmax:
            b = (a >= self.lonmin) & (a <= self.lonmax)
        else:
            c = np.abs(a - self.lonmin)
            v = np.min(c)
            b = (c == v)
            for i in range(len(b)):
                if b[i]:
                    if i < len(b) - 1:
                        b[i + 1] = False
                    break
        return b

    def geogrid(self):
        return ",".join([str(x) for x in [self.latmax, self.lonmin, self.latmin, self.lonmax]])

    def codes(self):
        lats = [str(x) for x in range(floor(self.latmin * 3 / 2), ceil(self.latmax * 3 / 2))]
        lons = [str(x) for x in range(floor(self.lonmin - 100), ceil(self.lonmax - 100))]
        if len(lats) == 0:
            lats = [str(floor(self.latmin * 3 / 2))]
        if len(lons) == 0:
            lons = [str(floor(self.lonmin - 100))]
        return [f"{lat}{lon}" for lat in lats for lon in lons if lat + lon in MESHLIST]


class TimeDomain:
    """time range, t0,t1 dates in yyyy-mm-dd format"""

    def __init__(self, t0, t1):
        self.beg = t0
        self.end = t1

    def years(self):
        return self.end.year - self.beg.year + 1

    def yrange(self):
        return range(self.beg.year, self.end.year + 1)

    def restrict(self, a):
        b = (a >= self.beg) & (a <= self.end)
        return b

    def geogrid(self):
        a = (self.beg - TIMEZERO).days - 1
        b = (self.end - TIMEZERO).days + 1
        return '"' + str(a) + '&lt;time","time&lt;' + str(b) + '"'


def lalo2mesh(lat, lon):
    lat = lat * 1.5
    lon = lon - 100
    lat1 = int(floor(lat))
    lat = 8 * (lat - lat1)
    lon1 = int(floor(lon))
    lon = 8 * (lon - lon1)
    lat2 = int(floor(lat))
    lat = 10 * (lat - lat2)
    lon2 = int(floor(lon))
    lon = 10 * (lon - lon2)
    lat3 = int(floor(lat))
    lon3 = int(floor(lon))
    return "".join([str(x) for x in [lat1, lon1, lat2, lon2, lat3, lon3]])


def mesh2lalo(code):
    assert len(code) == 8
    lat = int(code[:2]) / 1.5 + int(code[4]) / 12.0 + int(code[6]) / 120.0
    lon = int(code[2:4]) + 100 + int(code[5]) / 8.0 + int(code[7]) / 80.0
    return lat + 1 / 240.0, lon + 1 / 160.0


def timedom(tup):
    t1 = dt.strptime(tup[0], '%Y-%m-%d')
    t2 = dt.strptime(tup[1], '%Y-%m-%d')
    noda = (t2 - t1).days
    tr = [t1 + td(days=oo) for oo in range(noda + 1)]
    return np.array(tr)


def lalodom(tup):
    assert tup[0] < tup[1] and tup[2] < tup[3]
    div = 120.0
    nodi = floor(tup[1] * div) - floor(tup[0] * div)
    deg0 = floor(tup[0] * div) / div + 0.5 / div
    lat = [deg0 + oo / div for oo in range(nodi + 1)]
    div = 80.0
    nodi = floor(tup[3] * div) - floor(tup[2] * div)
    deg0 = floor(tup[2] * div) / div + 0.5 / div
    lon = [deg0 + oo / div for oo in range(nodi + 1)]
    return np.array(lat), np.array(lon)
