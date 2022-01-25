import os
import argparse
import urllib
import urllib.request
import geopandas as gpd
from pathlib import Path
from datetime import datetime as dt
from urllib.parse import urljoin
from functools import reduce
from constants import BASE_URL
from util import TimeDomain, LatLonDomain

root_path = Path('downloads')


def get_args():
    def str2date(s):
        return dt.strptime(s, '%Y-%m-%d')
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('begin_date', type=str2date, help='searching begin_date grater than(ex format:2020-03-01)')
    parser.add_argument('end_date', type=str2date, help='searching end_date less than(ex format:2020-03-01)')
    parser.add_argument('element', type=str,
                        help='気象要素(気象要素データ表の記号参照 https://amu.rd.naro.go.jp/wiki_open/doku.php?id=about)')
    parser.add_argument('aoi_path', type=Path, help='対象エリアファイルパス(shp, geojson etc...)')
    parser.add_argument('dest_path', type=Path, help='ダウンロード後のファイルパス')
    parser.add_argument('--is_cli', type=bool, default=False, help='True -> 平年値が返される / False -> 観測値が返される')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    user = os.getenv('MESH_USER')
    password = os.getenv('MESH_PASSWORD')
    if not (user and password):
        raise ValueError('set env MESH_USER AND MESH_PASSWORD')
    gdf = gpd.read_file(args.aoi_path)
    aoi = gdf['geometry'].iloc[0]

    td = TimeDomain(args.begin_date, args.end_date)
    lld = LatLonDomain(*aoi.bounds)
    area = lld.get_area()

    filename = 'AMD_' + area + '_' + ('Cli_' if args.is_cli else '') + args.element + '.nc.nc'
    geogrid = '?geogrid(' + args.element + ',' + lld.geogrid() + ',' + td.geogrid() + ')'
    url = reduce(urljoin, [BASE_URL, 'opendap/AMD/', area + '/', str(td.beg.year) + '/', filename, geogrid])
    print(url)
    q = urllib.request.Request(url)
    q.add_header('User-Agent', 'curl/7.50.1')

    mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    mgr.add_password(None, url, user, password)

    auth_handler = urllib.request.HTTPBasicAuthHandler(mgr)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)

    with urllib.request.urlopen(q) as resp:
        data = resp.read()
        with open(args.dest_path, 'wb') as f:
            f.write(data)


if __name__ == '__main__':
    main()
