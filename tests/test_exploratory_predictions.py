from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.constituent_weekly.run_exploratory_predictions import (
    action_excluded, cache_read, cache_write, key_for, causal_features,
    metrics, bootstrap_diff, FEATURES,
)

def synthetic_frame(days=32, post_anchor_close=110.0):
    rows=[]
    start=datetime(2026,1,1)
    for i in range(days):
        day=start+timedelta(days=i)
        if day.weekday()>=5: continue
        stamp=day.strftime("%Y-%m-%d")
        # Prior sessions have a valid open, pre-anchor, and 15:14 close.
        base=100+i*0.2
        values=[("09:15",base,base+0.4,base-0.1,base+0.2,1000),
                ("09:59",base+0.2,base+0.5,base+0.1,base+0.3,500),
                ("10:00",base+0.3,base+0.6,base+0.2,base+0.4,400),
                ("15:14",post_anchor_close if i==days-1 else base+0.8,
                 (post_anchor_close if i==days-1 else base+0.8)+0.2,
                 (post_anchor_close if i==days-1 else base+0.8)-0.2,
                 post_anchor_close if i==days-1 else base+0.8,2000)]
        for clock,o,h,l,c,v in values:
            rows.append({"timestamp":pd.Timestamp(f"{stamp} {clock}"),"open":o,"high":h,
                         "low":l,"close":c,"volume":v,"day":stamp,"clock":clock})
    return pd.DataFrame(rows)

def test_known_event_exclusion_covers_pre_anchor_feature_window_and_cycle():
    events=[(datetime(2026,1,15).date(),{"AAA","BBB"})]
    assert action_excluded("AAA","2026-02-01","2026-02-05",events)
    assert not action_excluded("CCC","2026-02-01","2026-02-05",events)
    assert not action_excluded("AAA","2026-03-01","2026-03-05",events)

def test_features_are_causal_and_anchor_open_is_used():
    f1=synthetic_frame(32,110.0)
    f2=synthetic_frame(32,900.0)
    stamp=sorted(f1.day.unique())[-1]
    x1=causal_features(f1,stamp); x2=causal_features(f2,stamp)
    assert set(x1)==set(FEATURES)
    assert all(np.isclose(x1[k],x2[k]) for k in FEATURES)
    assert np.isfinite(list(x1.values())).all()

def test_encrypted_panel_cache_round_trip_and_manifest_binding(tmp_path):
    path=tmp_path/"panel.enc"; key=cache_key("stable-test-secret","client")
    payload={"input_manifest":{"sha":"abc"},"rows":[{"x":1.25}]}
    cache_write(path,key,payload)
    raw=path.read_bytes()
    assert raw[:5]==b"BUP1E"
    assert b"1.25" not in raw
    assert cache_read(path,key,{"sha":"abc"})==payload
    assert cache_read(path,key,{"sha":"different"}) is None
    assert cache_read(path,cache_key("rotated-secret","client"),{"sha":"abc"}) is None

def test_metrics_and_cycle_block_bootstrap_are_reproducible():
    y=np.array([0,1,0,1,1,0,1,0])
    m=metrics(y,np.array([.2,.8,.4,.7,.6,.1,.9,.3]))
    assert m["n"]==8 and m["accuracy"]==1.0
    a=np.array([0,1,0,1,1,0,1,0])
    b=np.array([1,1,0,0,1,0,0,0])
    r1=bootstrap_diff(y,a,b); r2=bootstrap_diff(y,a,b)
    assert r1==r2
    assert r1["replicates"]==2000
    assert len(r1["ci95"])==2
