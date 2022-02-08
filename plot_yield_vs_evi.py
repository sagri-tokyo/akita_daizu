import argparse
import japanize_matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import rasterio as rio
import matplotlib.pyplot as plt
from rasterio.mask import mask
from pathlib import Path

from vegindex import evi2, ndvi, evi

sns.set(rc={'figure.figsize': (12, 10)})
japanize_matplotlib.japanize()

root_path = Path('downloads')
figure_path = root_path / 'figures'
table_path = root_path / 'tables'


def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('aoi_path', type=Path,
                        help='file containing location information and inference results(e.g. shp/geojson ...)')
    parser.add_argument('tif_path', type=Path,
                        help='file containing location information and inference results(e.g. shp/geojson ...)')
    parser.add_argument('seed', type=str,
                        help='file containing location information and inference results(e.g. shp/geojson ...)')
    parser.add_argument('index_name', type=str,
                        help='file containing location information and inference results(e.g. shp/geojson ...)')
    parser.add_argument('filename', type=str,
                        help='file containing location information and inference results(e.g. shp/geojson ...)')

    args = parser.parse_args()
    return args


def rio_mask(image, geometry):
    try:
        # all_touched=Trueにすることにより、農地ポリゴンが触れているピクセルの値も取得する
        out_image, _ = mask(image, [geometry], crop=True, all_touched=True, filled=False)
    except ValueError:
        #
        return None
    return out_image


def calc_evis(geoms, tif_path):
    with rio.open(tif_path) as image:
        mask_geoms = map(lambda geom: rio_mask(image, geom), geoms)
        _indicies = map(lambda mask_image: None if mask_image is None else evi(
            mask_image[2], mask_image[0], mask_image[3]), mask_geoms)
        _indicies_median = list(map(lambda x: 0 if x is None else np.ma.median(x), _indicies))
    return np.array(_indicies_median)


def calc_evi2s(geoms, tif_path):
    with rio.open(tif_path) as image:
        mask_geoms = map(lambda geom: rio_mask(image, geom), geoms)
        _indicies = map(lambda mask_image: None if mask_image is None else evi2(
            mask_image[2], mask_image[3]), mask_geoms)
        _indicies_median = list(map(lambda x: 0 if x is None else np.ma.median(np.ma.masked_invalid(x)), _indicies))
    return np.array(_indicies_median)


def calc_ndvis(geoms, tif_path):
    with rio.open(tif_path) as image:
        mask_geoms = map(lambda geom: rio_mask(image, geom), geoms)
        _indicies = map(lambda mask_image: None if mask_image is None else ndvi(
            mask_image[2], mask_image[3]), mask_geoms)
        _indicies_median = list(map(lambda x: 0 if x is None else np.ma.median(np.ma.masked_invalid(x)), _indicies))
    return np.array(_indicies_median)


def main():
    args = get_args()
    aois = gpd.read_file(args.aoi_path)

    if args.index_name == 'ndvi':
        target_col = 'ndvi_median'
    elif args.index_name == 'evi':
        target_col = 'evi_median'
    elif args.index_name == 'evi2':
        target_col = 'evi2_median'
    else:
        raise ValueError('')

    # indicies = np.empty((len(tif_paths), uzuto_aoi.shape[0]))
    # # sorted timestamp
    # for idx, (tif_path, date) in enumerate(sorted(paths_and_datetimes, key=lambda x: x[1])):
    aois['geometry'] = aois.to_crs('epsg:2445').buffer(-5).to_crs('epsg:4326')

    _aois = aois[aois['品種名'] == args.seed]
    evi_med = calc_evi2s(_aois['geometry'], args.tif_path)

    df = pd.DataFrame()
    target_col = 'kg/10a'
    index_name = 'evi2_median'
    df[target_col] = _aois[target_col]
    df['id'] = _aois['id']
    df[index_name] = evi_med
    print(df)

    # save_table_path = table_path / 'ndvi_median_uzuto_per_aoi.csv'
    # df.to_csv(save_table_path)
    filename = f'{args.seed}_{args.filename}'
    save_figure_path = figure_path / filename
    _corr = round(df.corr()[target_col].loc[index_name], 3)
    label = f'n = {df.shape[0]}, 相関係数 = {_corr}'
    ax = sns.scatterplot(x=index_name, y=target_col, hue='id', palette="deep", data=df)
    ax.text(df[index_name].min(), df[target_col].max(), label, fontsize=15)
    plt.title(save_figure_path.stem)
    plt.savefig(save_figure_path)
    plt.tight_layout()
    plt.close()
    # for idx in df['id'].unique():
    #     filename = f'plot_ndvi_median_vs_lai_uzuto_per_point_{idx}.jpg'
    #     save_figure_path = figure_path / filename
    #     df[df['id'] == idx].plot.scatter(x='ndvi_median', y='LAI')
    #     plt.savefig(save_figure_path)
    #     plt.close()


if __name__ == '__main__':
    main()