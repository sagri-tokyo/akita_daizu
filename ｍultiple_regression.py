import numpy as np

import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import ShuffleSplit, cross_val_score


def sklearn_calc(labels, params):
    """LassoModel,RidgeModel,LinRegModelで重回帰分析を実施

    Args:
        labels ([List]): 目的変数
        params ([List]): 説明変数
    """
    # トレーニングデータとテストデータに分割
    x_train, x_test, y_train, y_test = train_test_split(
        params, labels.ravel(), test_size=0.2)

    # Lasso
    LassoModel = Lasso(alpha=1.0, random_state=0)
    LassoModel.fit(x_train, y_train)

    # Rideg
    RidgeModel = Ridge(alpha=1.0, random_state=0)
    RidgeModel.fit(x_train, y_train)

    # LinReg
    LinRegModel = LinearRegression()
    LinRegModel.fit(x_train, y_train)

    # 各モデルによる回帰の評価(決定係数の表示)
    print("R-squared_Lasso : ", LassoModel.score(x_test, y_test))
    print("R-squared_Ridge : ", RidgeModel.score(x_test, y_test))
    print("R-squared_LinReg : ", LinRegModel.score(x_test, y_test))

    # データセットをランダムに５分割するための変数cvを定義
    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    print('###################################################')
    scores = cross_val_score(LassoModel, x_train, y_train, cv=cv)
    print(scores)
    print("R-squared_Average_Lasso　: {0:.2f}".format(scores.mean()))
    print('###################################################')
    scores = cross_val_score(RidgeModel, x_train, y_train, cv=cv)
    print(scores)
    print("R-squared_Average_Ridge　: {0:.2f}".format(scores.mean()))
    print('###################################################')
    scores = cross_val_score(LinRegModel, x_train, y_train, cv=cv)
    print(scores)
    print("R-squared_Average_LinReg　: {0:.2f}".format(scores.mean()))

    # matplotでグラフ化
    min_label = labels.ravel().min()
    max_label = labels.ravel().max()
    Lasso_predicted = LassoModel.predict(params)
    Ridge_predicted = RidgeModel.predict(params)
    LinReg_predicted = LinRegModel.predict(params)

    fig, ax = plt.subplots()
    ax.scatter(labels.ravel(), Lasso_predicted, edgecolors=(0, 0, 0))
    ax.scatter(labels.ravel(), Ridge_predicted, edgecolors=(0, 0, 0))
    ax.scatter(labels.ravel(), LinReg_predicted, edgecolors=(0, 0, 0))
    ax.plot([min_label, max_label],
            [min_label, max_label], 'k--', lw=4)
    ax.set_xlabel('Measured')
    ax.set_ylabel('Predicted')
    plt.show()


def main():
    csv_file_name = r"SiO2"
    csv_file_path = r"C:\MyProgram\python\sklearn"
    labels, params = csv_data_formatting(csv_file_name, csv_file_path)
    sklearn_calc(labels, params)


if __name__ == "__main__":
    main()