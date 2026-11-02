from __future__ import annotations
import gzip, hashlib, json, os, sys
from collections import Counter
from io import BytesIO
from pathlib import Path
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.constituent_weekly import build_c1_private_issuer_queue as queue_builder
from scripts.constituent_weekly import audit_c1_corporate_actions as corporate_actions
from scripts.constituent_weekly.audit_c1_continuous_dhan_coverage import (
    SPECIAL_EVENING_ONLY_SESSIONS, build_expiry_cycles, verified_expiry_dates
)

C2_RUN_ID=41398864378
C2_SOURCE_COMMIT="bff9fae12dbc1396a9e322c3001096bf4d5b0709"
C2_MANIFEST_HASH="9d263e441f09c70693e30f1541440ac6b249c5293da61faceb0af729d699c305"
C2_CYCLES=258
C2_STOCK_ROWS=12807
C2_FIRST_ANCHOR="2021-11-12"
C2_LAST_EXPIRY="2026-10-27"
MIN_MEMBERS=47
MIN_FRACTION=.94
REVIEW_CLASSES={"bonus","split","rights","merger_demerger"}
OUT_JSON=ROOT/"research/constituent_weekly/C1_COMPLEX_EVENT_CYCLE_EXCLUSION_AUDIT.json"
OUT_MD=ROOT/"research/constituent_weekly/C1_COMPLEX_EVENT_CYCLE_EXCLUSION_AUDIT.md"


def sha(data): return hashlib.sha256(data).hexdigest()

def event_overlaps_cycle(anchor,expiry,event_date):
    return str(anchor)<str(event_date)<=str(expiry)

def passes_member_coverage(valid_count,member_count):
    return member_count>0 and valid_count>=MIN_MEMBERS and valid_count/member_count>=MIN_FRACTION

def coverage_sensitivity(member_counts,baseline_counts,additional_exclusions):
    post={c:max(0,int(baseline_counts.get(c,0))-int(additional_exclusions.get(c,0))) for c in member_counts}
    flags={c:passes_member_coverage(n,member_counts[c]) for c,n in post.items()}
    fracs=[post[c]/member_counts[c] for c in member_counts if member_counts[c]>0]
    return {
        "cycles_checked":len(member_counts),
        "baseline_passing_cycles":sum(passes_member_coverage(int(baseline_counts.get(c,0)),m) for c,m in member_counts.items()),
        "post_exclusion_passing_cycles":sum(flags.values()),
        "post_exclusion_failing_cycles":sum(not x for x in flags.values()),
        "minimum_post_exclusion_valid_members":min(post.values(),default=0),
        "minimum_post_exclusion_member_fraction":round(min(fracs),6) if fracs else 0.0,
        "maximum_additional_exclusions_in_one_cycle":max(additional_exclusions.values(),default=0),
        "status":"PASS_47_94_ALL_CYCLES" if all(flags.values()) else "FAIL_47_94_SOME_CYCLES"
    }

def find_one(root,name):
    found=list(root.rglob(name))
    if len(found)!=1: raise ValueError(f"Expected exactly one {name}; found {len(found)}")
    return found[0]

def decrypt_panel(path,token,aad,nbytes,digest):
    cipher=path.read_bytes()
    if len(cipher)!=nbytes or sha(cipher)!=digest or len(cipher)<13:
        raise ValueError("Frozen C2 ciphertext size/hash mismatch")
    key=hashlib.sha256(b"BUP01-TejHQ-EOD-cache-v1:"+token.strip().encode()).digest()
    plain=AESGCM(key).decrypt(cipher[:12],cipher[12:],aad)
    return pd.read_csv(BytesIO(gzip.decompress(plain)))

def load_private_queue(token,cache,c2root):
    members=c2root/"data/constituent_weekly/nifty50_membership_intervals.csv"
    aliases=c2root/"data/constituent_weekly/security_alias_history.csv"
    if not members.is_file() or not aliases.is_file(): raise FileNotFoundError("C2 membership/alias snapshot absent")
    old_alias=corporate_actions.ALIASES
    old_loader=queue_builder.load_member_intervals
    old_classes=queue_builder.REVIEW_CLASSES
    try:
        corporate_actions.ALIASES=aliases
        queue_builder.load_member_intervals=lambda: corporate_actions.load_member_intervals(members)
        queue_builder.REVIEW_CLASSES=set(REVIEW_CLASSES)
        summary,items=queue_builder.build_private_candidate_queue(token,cache)
    finally:
        corporate_actions.ALIASES=old_alias
        queue_builder.load_member_intervals=old_loader
        queue_builder.REVIEW_CLASSES=old_classes
    if len(items)!=37 or summary.get("total_matched_unique_candidates")!=37 or not summary.get("matches_reference_count"):
        raise ValueError("Private complex-event queue does not reconcile to 37 candidates")
    return summary,items

def run_audit():
    token=os.environ.get("HF_TOKEN","").strip()
    c2root=Path(os.environ.get("C2_SOURCE_ROOT","")).resolve()
    artifact=Path(os.environ.get("C2_PANEL_ARTIFACT_DIR","")).resolve()
    cache=queue_builder.resolve_tejhq_encrypted_cache_dir(os.environ.get("TEJHQ_ENCRYPTED_CACHE_DIR"))
    if not token: raise RuntimeError("HF_TOKEN missing")
    if not queue_builder.personal_use_fallback_authorized(os.environ.get("TEJHQ_PERSONAL_USE_ONLY")):
        raise RuntimeError("TejHQ personal-use-only guard not confirmed")
    paths={
        "membership_sha256":c2root/"data/constituent_weekly/nifty50_membership_intervals.csv",
        "expiry_sha256":c2root/"data/reconciliation/expiry_verification.csv",
        "index_daily_sha256":c2root/"data/reconciliation/nifty50_official_daily.csv",
        "alias_sha256":c2root/"data/constituent_weekly/security_alias_history.csv",
        "action_event_sha256":c2root/"data/constituent_weekly/security_corporate_action_events.csv",
    }
    if not c2root.is_dir() or not artifact.is_dir() or any(not p.is_file() for p in paths.values()):
        raise FileNotFoundError("Pinned C2 source snapshot or panel artifact missing")
    manifest=json.loads(find_one(artifact,"C2_PANEL_BUILD.json").read_text())
    im=manifest.get("input_manifest",{})
    if manifest.get("status")!="COMPLETED" or manifest.get("methodology_version")!="bup01-c2-panel-v1":
        raise ValueError("C2 artifact not a completed registered v1 panel")
    if im.get("hash")!=C2_MANIFEST_HASH or im.get("cycle_count")!=C2_CYCLES:
        raise ValueError("C2 manifest does not match the pinned accepted panel")
    for k,p in paths.items():
        if sha(p.read_bytes())!=im.get(k): raise ValueError(f"C2 source snapshot hash mismatch: {k}")
    meta=manifest["encrypted_panel_cache"]
    sm,ixm=meta["stock"],meta["index"]
    stock=decrypt_panel(find_one(artifact,Path(sm["cache_relative_path"]).name),token,
        f"bup01-c2-panel-v1|frozen_panel|{C2_MANIFEST_HASH}|stock".encode(),
        int(sm["ciphertext_bytes"]),str(sm["ciphertext_sha256"]))
    index=decrypt_panel(find_one(artifact,Path(ixm["cache_relative_path"]).name),token,
        f"bup01-c2-panel-v1|frozen_panel|{C2_MANIFEST_HASH}|index".encode(),
        int(ixm["ciphertext_bytes"]),str(ixm["ciphertext_sha256"]))
    if {"cycle_idx","symbol","primary_flag"}-set(stock.columns) or "cycle_idx" not in index.columns:
        raise ValueError("Frozen C2 panel schema incomplete")
    if len(stock)!=C2_STOCK_ROWS or stock.duplicated(["cycle_idx","symbol"]).any():
        raise ValueError("Frozen C2 stock rows/keys do not match accepted panel")
    if len(index)!=C2_CYCLES or index["cycle_idx"].nunique()!=C2_CYCLES:
        raise ValueError("Frozen C2 index rows do not match accepted panel")

    membership=pd.read_csv(paths["membership_sha256"])
    expiry=pd.read_csv(paths["expiry_sha256"])
    index_daily=pd.read_csv(paths["index_daily_sha256"])
    sessions=sorted(pd.to_datetime(index_daily["session_date"],errors="coerce").dropna().dt.strftime("%Y-%m-%d").unique())
    cycles=build_expiry_cycles(verified_expiry_dates(expiry),sessions,membership,
        "2021-11-01","2026-10-30",SPECIAL_EVENING_ONLY_SESSIONS)
    if len(cycles)!=C2_CYCLES or min(c["anchor_date"] for c in cycles)!=C2_FIRST_ANCHOR or max(c["expiry_date"] for c in cycles)!=C2_LAST_EXPIRY:
        raise ValueError("Rebuilt expiry cycles differ from accepted C2 snapshot")
    if sorted(index["cycle_idx"].astype(int).unique())!=list(range(C2_CYCLES)):
        raise ValueError("C2 cycle identifiers do not match expected 0..257")

    qs,items=load_private_queue(token,cache,c2root)
    class_counts={k:sum(str(x.get("event_class"))==k for x in items) for k in sorted(REVIEW_CLASSES)}
    member_counts={i:len(c["members"]) for i,c in enumerate(cycles)}
    primary=stock["primary_flag"]
    if not pd.api.types.is_bool_dtype(primary):
        primary=primary.astype(str).str.strip().str.casefold().isin({"true","1","yes"})
    lookup={(int(r.cycle_idx),str(r.symbol)):bool(flag)
        for r,flag in zip(stock[["cycle_idx","symbol"]].itertuples(index=False),primary.tolist())}
    baseline=Counter()
    for (cycle,symbol),flag in lookup.items():
        if flag: baseline[cycle]+=1
    if len(baseline)!=C2_CYCLES: raise ValueError("Primary panel rows missing for one or more cycles")

    event_hits=set()
    stock_cycle_hits=set()
    class_overlap=Counter()
    no_overlap=0
    for event_id,item in enumerate(items):
        ex=str(item.get("ex_date",""))[:10]
        member=str(item.get("point_in_time_member_key","")).strip().upper()
        kind=str(item.get("event_class","unclassified"))
        hits=[i for i,c in enumerate(cycles) if member in c["members"] and event_overlaps_cycle(c["anchor_date"],c["expiry_date"],ex)]
        if not hits:
            no_overlap+=1
            continue
        event_hits.add(event_id)
        class_overlap[kind]+=1
        for cycle in hits: stock_cycle_hits.add((cycle,member))

    additional=Counter()
    already_flagged=absent=0
    for pair in stock_cycle_hits:
        if pair not in lookup: absent+=1
        elif lookup[pair]: additional[pair[0]]+=1
        else: already_flagged+=1

    before=coverage_sensitivity(member_counts,dict(baseline),{})
    after=coverage_sensitivity(member_counts,dict(baseline),dict(additional))
    return {
        "schema_version":1,"status":"COMPLETED","reviewed_at_utc":pd.Timestamp.utcnow().isoformat(),
        "scope":"conservative complex-event window exclusion sensitivity only; frozen C2 not modified",
        "frozen_c2":{
            "source_run_id":C2_RUN_ID,"source_commit":C2_SOURCE_COMMIT,"methodology_version":"bup01-c2-panel-v1",
            "input_manifest_sha256":C2_MANIFEST_HASH,"scheduled_cycles":C2_CYCLES,"stock_panel_rows":C2_STOCK_ROWS,
            "first_anchor":C2_FIRST_ANCHOR,"last_expiry":C2_LAST_EXPIRY,
        },
        "complex_event_queue":{
            "candidate_count":len(items),"membership_joins_unambiguous":qs["total_matched_unique_candidates"]==37,
            "feed_class_counts":class_counts,"source_partitions":len(qs["partition_metadata"]),
            "encrypted_source_cache_hits":sum(bool(x["encrypted_cache_hit"]) for x in qs["partition_metadata"]),
        },
        "cycle_intersections":{
            "events_overlapping_any_member_window":len(event_hits),"events_not_overlapping_cycle_member_windows":no_overlap,
            "unique_affected_stock_cycle_pairs":len(stock_cycle_hits),
            "affected_cycles":len({x[0] for x in stock_cycle_hits}),
            "affected_pairs_already_excluded_by_c2_flags":already_flagged,
            "affected_pairs_absent_from_c2_stock_panel":absent,
            "additional_primary_stock_cycle_rows_for_sensitivity_exclusion":sum(additional.values()),
            "event_class_counts_with_any_cycle_overlap":dict(sorted(class_overlap.items())),
        },
        "coverage_before_exclusion":before,"coverage_after_conservative_event_exclusion":after,
        "method":{
            "overlap_rule":"anchor_date < event_ex_date <= expiry_date",
            "exclusion_rule":"exclude affected constituent-cycle; no manual price factors, TERP or generic merger adjustment",
            "membership_and_cycle_source":"exact C2 source snapshot verified against frozen manifest",
        },
        "controls":{
            "c2_panel_modified":False,"c2_holdout_reused_for_tuning":False,"model_fitting_or_retraining_performed":False,
            "raw_event_rows_written_to_disk":False,"raw_prices_or_features_published":False,
            "raw_isins_or_subjects_published":False,"private_key_or_token_published":False,
            "personal_use_only_source_rows_published":False,
        },
        "decision":"SENSITIVITY_PRESERVES_47_94_FOR_ALL_258_CYCLES" if after["status"]=="PASS_47_94_ALL_CYCLES" else "SENSITIVITY_BREACHES_47_94_IN_ONE_OR_MORE_CYCLES",
    }

def write_reports(result):
    OUT_JSON.parent.mkdir(parents=True,exist_ok=True)
    OUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    b=result.get("coverage_before_exclusion",{})
    a=result.get("coverage_after_conservative_event_exclusion",{})
    x=result.get("cycle_intersections",{})
    lines=[
        "# C1 Complex-Event Weekly-Cycle Exclusion Sensitivity","",
        f'Updated: {result.get("reviewed_at_utc")}',
        f'Result: {result.get("decision",result.get("status"))}',"",
        "## Frozen C2 source","",
        f"- C2 run: https://github.com/VCR-TRADING-RESEARCH/NIFTY-Prediction/actions/runs/{C2_RUN_ID}",
        f"- C2 source commit: {C2_SOURCE_COMMIT}",
        f"- Frozen C2 manifest: {C2_MANIFEST_HASH}",
        f'- Accepted cycles: {result.get("frozen_c2",{}).get("scheduled_cycles","not rebuilt")}; stock rows: {result.get("frozen_c2",{}).get("stock_panel_rows","not decrypted")}.',"",
        "## Event-to-cycle overlap","",
        f'- Complex candidates reviewed: {result.get("complex_event_queue",{}).get("candidate_count","not built")}.',
        f'- Events intersecting at least one member window: {x.get("events_overlapping_any_member_window","not calculated")}.',
        f'- Unique affected constituent-cycle pairs: {x.get("unique_affected_stock_cycle_pairs","not calculated")}.',
        f'- Affected expiry cycles: {x.get("affected_cycles","not calculated")}.',
        f'- Previously flagged pairs: {x.get("affected_pairs_already_excluded_by_c2_flags","not calculated")}.',
        f'- Pairs absent from C2 panel: {x.get("affected_pairs_absent_from_c2_stock_panel","not calculated")}.',
        f'- Additional primary-eligible rows excluded: {x.get("additional_primary_stock_cycle_rows_for_sensitivity_exclusion","not calculated")}.',"",
        "## Registered 47-member / 94% rule","",
        f'- Before extra exclusions: {b.get("baseline_passing_cycles","not calculated")} / {b.get("cycles_checked","not calculated")} cycles pass.',
        f'- After extra exclusions: {a.get("post_exclusion_passing_cycles","not calculated")} / {a.get("cycles_checked","not calculated")} cycles pass.',
        f'- Failing cycles after exclusion: {a.get("post_exclusion_failing_cycles","not calculated")}.',
        f'- Minimum remaining members: {a.get("minimum_post_exclusion_valid_members","not calculated")}.',
        f'- Minimum remaining fraction: {a.get("minimum_post_exclusion_member_fraction","not calculated")}.',
        f'- Sensitivity status: {a.get("status","not calculated")}.',"",
        "## Interpretation and limitations","",
        "This is a conservative exclusion sensitivity, not an adjustment-factor calculation. It excludes affected constituent-cycle observations rather than inferring split, bonus, rights, demerger or debenture price factors.",
        "The frozen C2 panel, C3 forecasts, holdout and model metrics were not changed or used for tuning. No model was fitted.",
        "A passing sensitivity is not itself C1 acceptance. Full historical identity, price-series continuity, rights TERP/merger scheme treatment and the 49 secondary-event timing gates remain separate.",
        "Only aggregate counts and threshold summaries are published; event dates, securities and underlying vendor rows remain private.",
    ]
    OUT_MD.write_text("\n".join(lines)+"\n")

def main():
    try: result=run_audit()
    except Exception as exc:
        result={"schema_version":1,"status":"BLOCKED_RUNTIME_ERROR","reviewed_at_utc":pd.Timestamp.utcnow().isoformat(),
            "error_type":type(exc).__name__,"controls":{"raw_event_rows_written_to_disk":False,"raw_prices_or_features_published":False,"private_key_or_token_published":False}}
    write_reports(result)
    print("C1_COMPLEX_EVENT_CYCLE_AUDIT_STATUS",result.get("status"))
    if result.get("status")=="COMPLETED":
        x=result["cycle_intersections"]; c=result["coverage_after_conservative_event_exclusion"]
        print("C1_COMPLEX_EVENT_CYCLE_AUDIT_DECISION",result["decision"])
        print("C1_COMPLEX_EVENT_CYCLE_AUDIT_SUMMARY",json.dumps({
            "events":result["complex_event_queue"]["candidate_count"],
            "overlapping_events":x["events_overlapping_any_member_window"],
            "affected_cycles":x["affected_cycles"],
            "additional_rows_excluded":x["additional_primary_stock_cycle_rows_for_sensitivity_exclusion"],
            "cycles_passing_after_exclusion":c["post_exclusion_passing_cycles"],
            "cycles_failing_after_exclusion":c["post_exclusion_failing_cycles"],
        },sort_keys=True))
    else:
        print("C1_COMPLEX_EVENT_CYCLE_AUDIT_ERROR_TYPE",result.get("error_type","UNKNOWN"))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
