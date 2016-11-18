import datetime
import pandas as pd
import numpy as np
import pickle
import xgboost as xgb

import matplotlib as mpl
import matplotlib.pyplot as plt

def order_features_by_gains1(model, importance_type = 'weight'):
    sorted_feats = sorted(model._Booster.get_score(importance_type = importance_type).items(), key=lambda k: -k[1])
    return sorted_feats
    
def getFeaturesImportance1(fnames, model, importance_type = 'weight'):
    # Feature importance values
    model_fi = pd.DataFrame(fnames)
    model_fi.columns = ['feature']
    ff_gain = order_features_by_gains1(model, importance_type = importance_type)
    ff = np.zeros(len(fnames))
    for k,v in ff_gain:
        ff[fnames.index(k)] = v
    model_fi['importance'] = 100.0 * (ff / ff.max())
    return model_fi.sort_values('importance', ascending=0)

def drawFeaturesImportancePlot(model_fi, topN):
    pos = np.arange(topN)[::-1] + 1
    topn_features = list(model_fi.sort_values('importance', ascending=0)['feature'].head(topN))

    plt.figure(figsize=(6, 6))
    plt.axis([0, 100, 0, topN+1])
    plt.barh(pos, model_fi.sort_values('importance', ascending=0)['importance'].head(topN), align='center')
    plt.yticks(pos, topn_features)

    axes = plt.gca()
    colors=['red'] * 10 + ['blue'] * 10
    for color,tick in zip(colors,axes.yaxis.get_major_ticks()):
        tick.label1.set_color(color) #set the color property

    plt.xlabel('Relative Importance')
    plt.grid()
    plt.title('Model Feature Importance Plot', fontsize=20)
    plt.show()

startDate = datetime.datetime.strptime('Aug 1 2014', '%b %d %Y')
