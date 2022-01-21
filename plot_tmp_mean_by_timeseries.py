# https://github.com/sagri-tokyo/hiroshima-sandbox-farming-analysis　より
#　表示プロット機能に絞って動作確認

import argparse
import numpy as np
import pandas as pd
import xarray as xr
import seaborn as sns
import geopandas as gpd
import rasterio as rio
import matplotlib.pyplot as plt
from rasterio.mask import mask
from datetime import timedelta
from pathlib import Path

sns.set(rc={'figure.figsize': (12, 10)})

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

    args = parser.parse_args()
    return args


def main():
    target_index_1 = 'TMP_mea'
    target_index_2 = 'TMP_max'
    target_index_3 = 'TMP_min'
    target_col = '気温(℃)'
    # point_1 さわやか田打 MIHARAS設置位置
    point_1_lat = 34.556717
    point_1_lon = 133.021512
    # point_2 徳永郷 MIHARAS設置位置
    point_2_lat = 34.504685
    point_2_lon = 133.127719
    point_1 = pd.read_csv('downloads/tables/Weather data.xlsx - さわやか田打.csv', header=2)
    point_2 = pd.read_csv('downloads/tables/Weather data.xlsx - 徳永郷.csv', header=2)
    point_1['datetime'] = pd.to_datetime(point_1['データ名称/日付']) + point_1['時'].map(lambda x: timedelta(hours=x))
    point_2['datetime'] = pd.to_datetime(point_2['データ名称/日付']) + point_2['時'].map(lambda x: timedelta(hours=x))

    # メッシュデータが日平均、最大、最小の値
    # MIHARAS取得データは１時間毎の値であるため丸める
    groupby_idx = ['mean', 'max', 'min']
    groupby_cols = ['tmp_' + pat for pat in groupby_idx]
    point1_by_date = point_1.groupby([point_1['datetime'].dt.date])[target_col].agg(['mean', 'max', 'min'])
    point2_by_date = point_2.groupby([point_2['datetime'].dt.date])[target_col].agg(['mean', 'max', 'min'])
    point1_by_date.columns = groupby_cols
    point2_by_date.columns = groupby_cols

    point_1_tmp_mean = xr.open_dataset('downloads/tables/point_1_TMP_mean.nc')
    point_1_tmp_max = xr.open_dataset('downloads/tables/point_1_TMP_max.nc')
    point_1_tmp_min = xr.open_dataset('downloads/tables/point_1_TMP_min.nc')

    # point_1_df = point_1_tmp_mean.mean(dim=['lat', 'lon']).to_dataframe()
    point_1_df_tmp_mean = point_1_tmp_mean.sel(lat=point_1_lat, lon=point_1_lon, method="nearest").to_dataframe()
    point_1_df_tmp_max = point_1_tmp_max.sel(lat=point_1_lat, lon=point_1_lon, method="nearest").to_dataframe()
    point_1_df_tmp_min = point_1_tmp_min.sel(lat=point_1_lat, lon=point_1_lon, method="nearest").to_dataframe()



    # 計測地点徳永郷とさわやか田打、日平均・日最大・日最小それぞれで比較
    idx_name = 'tmp_mean'
    name = f'{idx_name}_timeseries_tauti'
    filename = f'plot_{name}.jpg'
    save_figure_path = figure_path / filename
    sns.lineplot(x='datetime', y=idx_name, data=point1_by_date)
    sns.lineplot(x='time', y=target_index_1, data=point_1_df_tmp_mean)
    plt.xlim(point1_by_date.index.min(), point1_by_date.index.max())
    plt.title(name)
    plt.savefig(save_figure_path)
    plt.close()

    idx_name = 'tmp_max'
    name = f'{idx_name}_timeseries_tauti'
    filename = f'plot_{name}.jpg'
    save_figure_path = figure_path / filename
    sns.lineplot(x='datetime', y=idx_name, data=point1_by_date)
    sns.lineplot(x='time', y=target_index_2, data=point_1_df_tmp_max)
    plt.xlim(point1_by_date.index.min(), point1_by_date.index.max())
    plt.title(name)
    plt.savefig(save_figure_path)
    plt.close()

    idx_name = 'tmp_min'
    name = f'{idx_name}_timeseries_tauti'
    filename = f'plot_{name}.jpg'
    save_figure_path = figure_path / filename
    sns.lineplot(x='datetime', y=idx_name, data=point1_by_date)
    sns.lineplot(x='time', y=target_index_3, data=point_1_df_tmp_min)
    plt.xlim(point1_by_date.index.min(), point1_by_date.index.max())
    plt.title(name)
    plt.savefig(save_figure_path)
    plt.close()


    # for idx in df['id'].unique():
    #     filename = f'plot_ndvi_median_vs_lai_uzuto_per_point_{idx}.jpg'
    #     save_figure_path = figure_path / filename
    #     df[df['id'] == idx].plot.scatter(x='ndvi_median', y='LAI')
    #     plt.savefig(save_figure_path)
    #     plt.close()


if __name__ == '__main__':
    main()