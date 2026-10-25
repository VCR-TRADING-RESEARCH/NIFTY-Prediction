import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from scripts.run_experimental_tracks import metrics

def test_metrics_are_finite_and_bounded():
    y=np.array([0,1,0,1,1,0])
    p=np.array([0.1,0.8,0.4,0.7,0.6,0.2])
    out=metrics(y,(p>=0.5).astype(int),p)
    assert out["n"] == 6
    assert 0 <= out["accuracy"] <= 1
    assert 0 <= out["balanced_accuracy"] <= 1
    assert 0 <= out["brier"] <= 1

def test_metrics_reflect_predictions():
    y=np.array([0,1,0,1])
    p=np.array([0.1,0.9,0.2,0.8])
    out=metrics(y,(p>=0.5).astype(int),p)
    assert out["accuracy"] == accuracy_score(y,(p>=0.5).astype(int))
    assert out["balanced_accuracy"] == balanced_accuracy_score(y,(p>=0.5).astype(int))
