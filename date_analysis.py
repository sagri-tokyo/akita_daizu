import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#箱ひげ図表示関数
def get_box(output_df,num_list):
  fig = plt.figure(figsize=(10,10))
  for i in range(len(num_list)):
    plt.subplot(len(num_list), 4, i+1)
    output_df[num_list[i]].plot(kind="box")
  return 

#四分位数と外れ値のindex値を取得する関数
def box_Outlier(output_df,num_list):
  for i in range(len(num_list)):
    #第1四分位数を取得
    q1=output_df[num_list[i]].quantile(0.25)
    #第2四分位数を取得
    q3=output_df[num_list[i]].quantile(0.75)
    #IQRを取得
    iqr=q3-q1
    #外れ値基準の下限を取得
    bottom=q1-(1.5*iqr)
    #外れ値基準の上限を取得
    up=q3+(1.5*iqr)
    #列名、Q1、Q3、IQR、外れ値を表示
    print(str(num_list[i]))
    print("Q1は："+str(q1))
    print("Q3は："+str(q3))
    print("IQRは："+str(iqr))
    print("外れ値は↓")
    print(output_df[num_list[i]][(output_df[num_list[i]] < bottom) | (output_df[num_list[i]] > up) ])
    print("*********************")
  return 
    
# データ分布を確認するためのヒストグラムの作成
def get_histlist(output_df,num_list ):
  fig = plt.figure(figsize=(10,10))
  for i in range(len(num_list)):
    #1出力に複数の図を表示できるように設定
    plt.subplot(len(num_list), 4, i+1)
    #ヒストグラムの表示
    output_df[num_list[i]].plot.hist(bins=15)
  return 
