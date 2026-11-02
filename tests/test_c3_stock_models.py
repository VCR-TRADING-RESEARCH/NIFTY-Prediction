import numpy as np, pandas as pd
from scripts.constituent_weekly.run_c3_stock_models import weights, score, symbol_frequency, boot_ci

def test_cycle_weights_equalize_cycle_totals():
    ids=pd.Series([1,1,2,2,2,3]); w=weights(ids); sums=pd.Series(w).groupby(ids).sum()
    assert np.allclose(sums.to_numpy(),sums.iloc[0]) and np.isclose(w.mean(),1)

def test_metrics_perfect_prediction():
    m=score([0,0,1,1],[.1,.2,.8,.9]); assert m['accuracy']==1 and m['roc_auc']==1

def test_symbol_frequency_only_uses_prior_training():
    tr=pd.DataFrame({'symbol':['A','A','B'],'stock_label':[1,0,1]})
    te=pd.DataFrame({'symbol':['A','B','C']})
    assert np.allclose(symbol_frequency(tr,te),[(1+1)/(2+2),(1+1)/(1+2),(2+1)/(3+2)])

def test_block_bootstrap_contract():
    x=boot_ci(np.linspace(-.2,.2,24)); assert x['replicates']==2000 and x['block_cycles']==4 and len(x['ci95'])==2
