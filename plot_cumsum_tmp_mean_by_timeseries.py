import argparse
import japanize_matplotlib
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
japanize_matplotlib.japanize()


root_path = Path('downloads')
figure_path = root_path / 'figures'
table_path = root_path / 'tables'


def main():
    target_index_1 = 'TMP_mea'
    target_col = '気温(℃)'
    # point_1 さわやか田打 MIHARAS設置位置
    point_1_lat = 34.556717
    point_1_lon = 133.021512
    point_1 = pd.read_csv('downloads/tables/Weather data.xlsx - さわやか田打.csv', header=2)
    point_1['datetime'] = pd.to_datetime(point_1['データ名称/日付']) + point_1['時'].map(lambda x: timedelta(hours=x))

    # メッシュデータが日平均、最大、最小の値
    # MIHARAS取得データは１時間毎の値であるため丸める
    groupby_idx = ['mean']
    groupby_cols = ['tmp_' + pat for pat in groupby_idx]
    point1_by_date = point_1.groupby([point_1['datetime'].dt.date])[target_col].agg(groupby_idx)
    point1_by_date.columns = groupby_cols
    point1_by_date['cumsum_tmp_mean'] = point1_by_date['tmp_mean'].cumsum()

    target_date_range = point1_by_date.index

    point_1_tmp_mean = xr.open_dataset('downloads/tables/point_1_TMP_mean.nc')
    # point_1_df = point_1_tmp_mean.mean(dim=['lat', 'lon']).to_dataframe()
    point_1_df_tmp_mean = point_1_tmp_mean.sel(lat=point_1_lat, lon=point_1_lon, method="nearest").to_dataframe()
    point_1_df_tmp_mean = point_1_df_tmp_mean.loc[target_date_range]
    point_1_df_tmp_mean['cumsum_tmp_mean'] = point_1_df_tmp_mean[target_index_1].cumsum()

    # plot_point_1_df = pd.DataFrame(
    #     {'MIHARAS': point1_by_date['cumsum_tmp_mean'], '農研機構メッシュデータ': point_1_df_tmp_mean['cumsum_tmp_mean']})
    # plot_point_2_df = pd.DataFrame(
    #     {'MIHARAS': point2_by_date['cumsum_tmp_mean'], '農研機構メッシュデータ': point_2_df_tmp_mean['cumsum_tmp_mean']})
    # plot_point_1_df.
    # plot_point_1_df.to_csv(table_path / f'.csv')
    # plot_point_2_df.to_csv(table_path / f'.csv')
    # 計測地点徳永郷とさわやか田打、日平均・日最大・日最小それぞれで比較
    idx_name = 'cumsum_tmp_mean'
    name = f'{idx_name}_timeseries_tauti'
    filename = f'plot_{name}.jpg'
    save_figure_path = figure_path / filename
    ax = sns.lineplot(x='datetime', y=idx_name, data=point1_by_date)
    sns.lineplot(x='time', y=idx_name, data=point_1_df_tmp_mean)
    diff = point1_by_date['cumsum_tmp_mean'] - point_1_df_tmp_mean['cumsum_tmp_mean']
    _diff = round(diff[diff.index == pd.to_datetime('2021-08-11')].iloc[0], 3)
    label = f'出穂日までの積算気温差分: {_diff}[℃]'
    ax.text(point1_by_date.index.min(), point1_by_date[idx_name].max(), label, fontsize=15)
    plt.xlim(point1_by_date.index.min(), pd.to_datetime('2021-08-11'))
    plt.title('計測地点: さわやか田打')
    plt.ylabel('積算気温')
    plt.legend(['MIHARAS観測値', 'メッシュ農業気象データ'])
    plt.savefig(save_figure_path)
    # plt.tight_layout()
    plt.close()


if __name__ == '__main__':
    main()