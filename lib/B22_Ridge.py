import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_validate, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn import preprocessing
from sklearn import metrics
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt



def trainAndPlotAll(df_data):
    # On ne garde que les jours où au moins 3 arrivées sont enregistrées
    df_data = df_data[(df_data['A_EU'] + df_data['A_NA'] + df_data['A_AS'] >= 3)]
    
    # On enlève les colonnes non utilisées pour le machine learning
    list_dates = np.array(df_data['Atime'])
    df_data = df_data.drop(columns=['Atime', 'A_AS', 'A_NA'])

    X = np.array(df_data.drop(columns=['A_EU']))
    y = np.array(df_data['A_EU'])

    kf = KFold(n_splits=5, shuffle=True, random_state=13)

    r2_scores = []
    rmse_scores = []

    # loop over the different folds
    for i, (train_index, test_index) in enumerate(kf.split(X)):
        print("fold: {0} | nb_train: {1} | nb_test: {2}".format(i, len(train_index), len(test_index)))

        # get train and validation dataset
        X_train = X[train_index]
        X_test = X[test_index]
        y_train = y[train_index]
        y_test = y[test_index]

        list_dates_train = list_dates[train_index]
        list_dates_test = list_dates[test_index]
        
        # train model
        ridge = Ridge(alpha=0.01, random_state=13)
        ridge.fit(X_train, y_train)

        y_pred = ridge.predict(X_test)

        # measure performance
        r2_score_ridge_test = r2_score(y_test, y_pred)
        print("R2: {0:0.2f}".format(r2_score_ridge_test))
        r2_scores.append(r2_score_ridge_test)
        rmse_ridge_test = mean_squared_error(y_test, y_pred, squared=False)
        print("RMSE : {0:0.2f}".format(rmse_ridge_test))
        rmse_scores.append(rmse_ridge_test)

        # On regarde les coefficients des différentes variables
        num_features = X_train.shape[1]
        feature_names = df_data.drop(columns=['A_EU']).columns
        plt.scatter(range(num_features), np.abs(ridge.coef_))
        plt.xlabel('Variables')
        tmp = plt.xticks(range(num_features), feature_names, rotation=90)
        tmp = plt.ylabel('Coefficients')
        plt.title("Coefficients avec ridge")
        plt.savefig(f'../figure/B22_Ridge_coeff_{i}.png')
        plt.show()

        # On compare les prédictions aux valeurs réelles
        fig = plt.figure(figsize=(5, 5))
        plt.scatter(y_test, y_pred)
        plt.xlabel("Nombre réel")
        plt.ylabel("Nombre prédit")
        plt.title(f'Ridge : nombre de navires arrivant en Europe (RMSE = {metrics.mean_squared_error(y_test, y_pred, squared=False)})')
        axis_min = np.min([np.min(y_test), np.min(y_pred)])-1 # Mêmes valeurs sur les deux axes
        axis_max = np.max([np.max(y_test), np.max(y_pred)])+1
        plt.xlim(axis_min, axis_max)
        plt.ylim(axis_min, axis_max)
        plt.plot([axis_min, axis_max], [axis_min, axis_max], 'k-') # Diagonale y=x
        plt.savefig(f'../figure/B22_Ridge_diag_{i}.png')
        plt.show()

        # Evolution temporelle
        plt.plot(list_dates, y, 'b')
        plt.plot(list_dates_test, y_pred, 'r')
        plt.xlabel("Temps")
        plt.ylabel("Nombre de navires arrivant en Europe")
        plt.legend(('Evolution réelle', 'Evolution prédite (ridge)'), loc='upper right')
        plt.title("RMSE : %.2f" % metrics.mean_squared_error(y_test, y_pred, squared=False))
        plt.savefig(f'../figure/B22_Ridge_vesselsperday_{i}.png')
        plt.show()


    print()
    
    # performance on the test set
    average_r2_score = np.mean(r2_scores)
    std_r2_score = np.std(r2_scores)
    print("Average R2: {0:0.3f}".format(average_r2_score))
    print("Standard deviation R2: {0:0.3f}".format(std_r2_score))
    average_rmse_score = np.mean(rmse_scores)
    std_rmse_score = np.std(rmse_scores)
    print("Average RMSE: {0:0.3f}".format(average_rmse_score))
    print("Standard deviation RMSE: {0:0.3f}".format(std_rmse_score))


if __name__ == '__main__':
    df_trips = pd.read_csv('../data/loadAll_agg_all.csv')
    trainAndPlotAll(df_trips)