import gzip
import numpy as np, pandas as pd
from scripts.constituent_weekly.run_c3_stock_models import weights, score, symbol_frequency, boot_ci, encrypt, read_decrypted_csv, holdout_start_index

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


def test_encrypted_csv_round_trip_uses_file_like_buffer(tmp_path):
    token='unit-test-hf-token'; aad=b'unit-test-aad'
    frame=pd.DataFrame({'cycle_idx':[1,2], 'symbol':['A','B'], 'stock_label':[1,0]})
    raw=gzip.compress(frame.to_csv(index=False).encode())
    path=tmp_path/'panel.aesgcm'; path.write_bytes(encrypt(raw,token,aad))
    loaded=read_decrypted_csv(path,token,aad)
    pd.testing.assert_frame_equal(loaded,frame)

def test_holdout_boundary_is_dynamic_final_twenty_percent():
    assert holdout_start_index(258) == 206
    assert holdout_start_index(260) == 208
    assert 260 - holdout_start_index(260) == 52
