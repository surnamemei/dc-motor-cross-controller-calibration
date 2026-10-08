#!/usr/bin/env python3
"""Confirmatory STM32 analysis, exactly as frozen in STM32_PROTOCOL.md (sha 3421f408...).

  python3 tools/analysis_C.py --verify-only   integrity + split + procedure checks, no model fitted
  python3 tools/analysis_C.py                 the single confirmatory execution (refuses to run twice)

Stage 1 opens ONLY source-calibration runs (run02-07 of each arm), fits each source's ARX(2,2,1)+c,
applies the frozen acceptance checks, computes the 99th-percentile threshold and writes everything to
results_C/calibration_models.json BEFORE stage 2 opens any holdout, target or interleaved-pass run.
"""
import argparse, hashlib, json, sys, time, zipfile
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "raw" / "candidate_C_zenodo" / "extracted" / "benchmark" / "hw_results"
ZIP = ROOT / "raw" / "candidate_C_zenodo" / "etrls-str-stm32-v1.0.zip"
OUT = ROOT / "results_C"
FROZEN = {
    "STM32_PROTOCOL.md": "3421f408cd4a7afc0d13ea408e2f8d488ffe0f3e0574a9686888ae655f56b280",
    "protocol/candidate_C_splits.json": "0ef7f6a8311ea46c1751b42d3df443252047e81b9112198467a274bcb18a7d2e",
    "manifests/candidate_C_units.csv": "4e4ed2efd05f732873d21efdf8875f9188a7f4f7ad1e5079aec156b17265a62e",
    "raw/candidate_C_zenodo/etrls-str-stm32-v1.0.zip": "2df790e4e2f1fba74022e2f3fad2d7f3d8f9dad4f1a4b02dd6f40b7425fb9af6",
}
ARMS = ["ZN", "PT", "GS", "PSO"]
SCEN = ["S1", "S3"]
PAIRS = [("ZN", "PT"), ("PT", "GS"), ("GS", "PSO")]
B, SEED, Q = 600, 33043, 0.99
LOG, OPENED = [], []


def log(m):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}  {m}"
    LOG.append(line); print(line)


def sha_b(b): return hashlib.sha256(b).hexdigest()
def sha(p): return sha_b(Path(p).read_bytes())


# ------------------------------------------------------------------ verification
def verify():
    for rel, h in FROZEN.items():
        if sha(ROOT / rel) != h:
            sys.exit(f"ABORT: frozen input changed: {rel}")
    S = json.load(open(ROOT / "protocol/candidate_C_splits.json"))
    U = pd.read_csv(ROOT / "manifests/candidate_C_units.csv")
    E = U[U.eligibility == "ELIGIBLE_fixed_PI_nominal"]
    assert len(E) == 88 and set(E.arm) == set(ARMS) and set(E.scenario) == set(SCEN)
    assert E.groupby(["scenario", "arm"]).size().eq(11).all()
    z = zipfile.ZipFile(ZIP)
    zmap = {n[n.index("hw_results/") + len("hw_results/"):]: n for n in z.namelist() if "hw_results/" in n}
    for _, r in E.iterrows():
        b = (DATA / r.file).read_bytes()
        if sha_b(b) != r.sha256 or sha_b(z.read(zmap[r.file])) != r.sha256:
            sys.exit(f"ABORT: hash mismatch {r.file}")
    split_files = set()
    for s in SCEN:
        sc = S["scenarios"][s]
        got = [(p["source"], p["target"]) for p in sc["chain_pairs"]]
        assert got == PAIRS, got
        for a in ARMS:
            src = sc["sources"][a]
            assert [x["run"] for x in src["calibration"]] == list(range(2, 8))
            assert [x["run"] for x in src["holdout"]] == list(range(8, 12))
            assert [x["run"] for x in src["interleaved_pass_run01"]] == [1]
            for role in ("calibration", "holdout", "interleaved_pass_run01"):
                for x in src[role]:
                    assert x["file"] == f"data/{a}/{s}/run{x['run']:02d}.csv" and x["sha256"] == sha(DATA / x["file"])
                    split_files.add(x["file"])
        for p in sc["chain_pairs"]:
            assert [x["run"] for x in p["target_runs"]] == list(range(2, 6))
            # chronology: every target run is later than every source-holdout run
            th = max(pd.Timestamp(x["time"]) for x in sc["sources"][p["source"]]["holdout"])
            assert min(pd.Timestamp(x["time"]) for x in p["target_runs"]) > th
    assert split_files == set(E.file), "splits do not cover exactly the 88 eligible files"
    log("verified: 4 frozen inputs; 88/88 eligible files (extracted bytes == zip bytes == manifest); "
        "6 comparisons = (ZN->PT, PT->GS, GS->PSO) x (S1, S3); calibration=02-07, holdout=08-11, "
        "targets=next block 02-05, all targets later than source holdout")
    return S


# ------------------------------------------------------------------ model
def load(rel):
    OPENED.append(rel)
    d = pd.read_csv(DATA / rel)
    return dict(t=d.time.to_numpy(float), f=d.feedback.to_numpy(float), u=d.output.to_numpy(float),
                sp=d.setpoint.to_numpy(float))


def design(run, intercept=True):
    f, u = run["f"], run["u"]
    k = np.arange(2, len(f))
    cols = [-f[k - 1], -f[k - 2], u[k - 1], u[k - 2]] + ([np.ones(len(k))] if intercept else [])
    return np.column_stack(cols), f[k], k


def fit(runs, intercept=True):
    Xs, Ys = zip(*[design(r, intercept)[:2] for r in runs])
    X, Y = np.vstack(Xs), np.concatenate(Ys)
    th, *_ = np.linalg.lstsq(X, Y, rcond=None)
    poles = np.roots([1.0, th[0], th[1]])
    reasons = []
    if not (np.isfinite(X).all() and np.isfinite(Y).all()): reasons.append("nonfinite_rows")
    if len(Y) < 20000: reasons.append("rows_lt_20000")
    cond = float(np.linalg.cond(X))
    if cond >= 1e8: reasons.append("cond_ge_1e8")
    if np.any(np.abs(poles) > 0.9999): reasons.append("pole_gt_0.9999")
    if th[2] + th[3] <= 0: reasons.append("b1_plus_b2_le_0")
    return th, reasons, dict(cond=cond, poles=[complex(p) for p in poles], n_rows=int(len(Y)))


def mask(run, rule):
    t = run["t"][2:]
    if rule == "all":
        return np.ones(len(t), bool)
    if rule == "t_ge_2s":
        return t >= 2.0
    if rule == "excl_1p5s_after_setpoint_change":
        sp = run["sp"]; ch = run["t"][np.flatnonzero(np.diff(sp) != 0) + 1]
        m = np.ones(len(t), bool)
        for tc in ch:
            m &= ~((t >= tc) & (t < tc + 1.5))
        return m
    raise ValueError(rule)


def scores(theta, run, intercept=True, rule="all"):
    X, Y, _ = design(run, intercept)
    return np.abs(Y - X @ theta)[mask(run, rule)]


def far(s, thr): return float(np.mean(s > thr))


CONFIGS = {"primary": dict(intercept=True, q=0.99, rule="all"),
           "sens_a_no_intercept": dict(intercept=False, q=0.99, rule="all"),
           "sens_b_5pct": dict(intercept=True, q=0.95, rule="all"),
           "sens_c_t_ge_2s": dict(intercept=True, q=0.99, rule="t_ge_2s"),
           "sens_d_excl_ramp": dict(intercept=True, q=0.99, rule="excl_1p5s_after_setpoint_change")}


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if len(x) else [None, None]


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--verify-only", action="store_true"); a = ap.parse_args()
    S = verify()
    if a.verify_only:
        (ROOT / "protocol" / "candidate_C_preflight.txt").write_text("\n".join(LOG) + "\n")
        return
    if (OUT / "run_log.txt").exists():
        sys.exit("ABORT: confirmatory analysis already executed once (results_C/run_log.txt exists)")
    OUT.mkdir(exist_ok=True)
    log(f"analysis_C.py sha256 {sha(Path(__file__))}")

    # ---------------- stage 1: calibration runs only
    cal = {s: {A: [load(x["file"]) for x in S["scenarios"][s]["sources"][A]["calibration"]] for A in ARMS} for s in SCEN}
    cal_files = {x["file"] for s in SCEN for A in ARMS for x in S["scenarios"][s]["sources"][A]["calibration"]}
    assert set(OPENED) == cal_files and len(OPENED) == 48
    models, failures = {}, []
    for s in SCEN:
        for A in ARMS:
            for cname, c in CONFIGS.items():
                key = f"{s}|{A}|{cname}"
                th, reasons, info = fit(cal[s][A], c["intercept"])
                if reasons:
                    failures.append(dict(stage="point_fit", key=key, reasons=reasons)); models[key] = None
                    continue
                sc = [scores(th, r, c["intercept"], c["rule"]) for r in cal[s][A]]
                pooled = np.concatenate(sc)
                thr = float(np.quantile(pooled, c["q"], method="higher"))
                res_all = np.concatenate([design(r, c["intercept"])[1] - design(r, c["intercept"])[0] @ th for r in cal[s][A]])
                models[key] = dict(theta=[repr(float(v)) for v in th], threshold=thr, n_rows=info["n_rows"],
                                   cond=info["cond"], poles=[repr(p) for p in info["poles"]],
                                   pole_abs=[float(abs(p)) for p in info["poles"]],
                                   dc_gain_rpm_per_V=float((th[2] + th[3]) / (1 + th[0] + th[1])),
                                   calibration_far_per_run=[far(x, thr) for x in sc],
                                   calibration_far=float(np.mean([far(x, thr) for x in sc])),
                                   n_scores_equal_threshold=int(np.sum(pooled == thr)),
                                   resid_std=float(np.std(res_all)),
                                   resid_lag1_autocorr=float(np.corrcoef(res_all[1:], res_all[:-1])[0, 1]),
                                   frac_abs_resid_lt_0p05=float(np.mean(np.abs(res_all) < 0.05)))
    (OUT / "calibration_models.json").write_text(json.dumps({"models": models, "point_fit_failures": failures},
                                                            indent=2) + "\n")
    log(f"stage 1 complete: opened only the 48 calibration files; 40 source models written "
        f"(point-fit failures: {len(failures)}); calibration_models.json sha {sha(OUT / 'calibration_models.json')}")

    # ---------------- stage 2: holdout, targets, passes
    hold = {s: {A: [load(x["file"]) for x in S["scenarios"][s]["sources"][A]["holdout"]] for A in ARMS} for s in SCEN}
    pas = {s: {A: load(S["scenarios"][s]["sources"][A]["interleaved_pass_run01"][0]["file"]) for A in ARMS} for s in SCEN}
    block = {s: {A: {r: (cal[s][A][r - 2] if r <= 7 else hold[s][A][r - 8]) for r in range(2, 12)} for A in ARMS} for s in SCEN}
    log("stage 2: holdout, target and interleaved-pass files opened")

    def M(s, A, cname):
        m = models[f"{s}|{A}|{cname}"]
        return None if m is None else (np.array([float(v) for v in m["theta"]]), m["threshold"])

    rows_hold, rows_pairs, rows_time, rows_I, rows_R, boot_fail = [], [], [], [], [], []
    for cname, c in CONFIGS.items():
        for s in SCEN:
            for A in ARMS:
                mm = M(s, A, cname)
                if mm is None: continue
                th, thr = mm
                hf = [far(scores(th, r, c["intercept"], c["rule"]), thr) for r in hold[s][A]]
                # whole-run bootstrap for the same-controller baseline
                rng = np.random.default_rng(SEED); bh, nf = [], {}
                for b in range(B):
                    ci_ = rng.integers(0, 6, 6); hi = rng.integers(0, 4, 4)
                    thb, rs, _ = fit([cal[s][A][i] for i in ci_], c["intercept"])
                    if rs:
                        for x in rs: nf[x] = nf.get(x, 0) + 1
                        continue
                    tb = float(np.quantile(np.concatenate([scores(thb, cal[s][A][i], c["intercept"], c["rule"]) for i in ci_]),
                                           c["q"], method="higher"))
                    bh.append(np.mean([far(scores(thb, hold[s][A][i], c["intercept"], c["rule"]), tb) for i in hi]))
                if nf: boot_fail.append(dict(analysis="holdout", config=cname, scenario=s, source=A, failures=nf))
                rows_hold.append(dict(config=cname, scenario=s, controller=A,
                                      calibration_far=models[f"{s}|{A}|{cname}"]["calibration_far"],
                                      holdout_far=float(np.mean(hf)), holdout_far_per_run=hf,
                                      holdout_ci95=ci(bh), boot_success=len(bh), boot_failed=B - len(bh)))
                if cname == "primary":
                    pf = far(scores(th, pas[s][A]), thr)
                    rows_time.append(dict(scenario=s, controller=A, pass_run01_far=pf, holdout_far=float(np.mean(hf)),
                                          delta_time=pf - float(np.mean(hf))))
                    for Bm in ARMS:
                        rows_I.append(dict(scenario=s, source=A, evaluated=Bm,
                                           far_run01=far(scores(th, pas[s][Bm]), thr)))
                        if Bm != A:
                            rows_R.append(dict(scenario=s, source=A, evaluated=Bm,
                                               mean_far_run02_11=float(np.mean([far(scores(th, block[s][Bm][r]), thr)
                                                                                for r in range(2, 12)]))))
            for (A, Bm) in PAIRS:
                mm = M(s, A, cname)
                if mm is None:
                    rows_pairs.append(dict(config=cname, scenario=s, source=A, target=Bm, status="STOP_model_failure"))
                    continue
                th, thr = mm
                hf = [far(scores(th, r, c["intercept"], c["rule"]), thr) for r in hold[s][A]]
                tf = [far(scores(th, block[s][Bm][r], c["intercept"], c["rule"]), thr) for r in range(2, 6)]
                rng = np.random.default_rng(SEED); bd, nf = [], {}
                for b in range(B):
                    ci_ = rng.integers(0, 6, 6); hi = rng.integers(0, 4, 4); ti = rng.integers(0, 4, 4)
                    thb, rs, _ = fit([cal[s][A][i] for i in ci_], c["intercept"])
                    if rs:
                        for x in rs: nf[x] = nf.get(x, 0) + 1
                        continue
                    tb = float(np.quantile(np.concatenate([scores(thb, cal[s][A][i], c["intercept"], c["rule"]) for i in ci_]),
                                           c["q"], method="higher"))
                    h = np.mean([far(scores(thb, hold[s][A][i], c["intercept"], c["rule"]), tb) for i in hi])
                    t_ = np.mean([far(scores(thb, block[s][Bm][2 + i], c["intercept"], c["rule"]), tb) for i in ti])
                    bd.append((h, t_, t_ - h, tb))
                bd = np.array(bd) if bd else np.empty((0, 4))
                if nf: boot_fail.append(dict(analysis="pair", config=cname, scenario=s, source=A, target=Bm, failures=nf))
                rows_pairs.append(dict(config=cname, scenario=s, source=A, target=Bm, status="OK",
                                       calibration_far=models[f"{s}|{A}|{cname}"]["calibration_far"],
                                       holdout_far=float(np.mean(hf)), target_far=float(np.mean(tf)),
                                       D=float(np.mean(tf) - np.mean(hf)), holdout_far_per_run=hf, target_far_per_run=tf,
                                       holdout_ci95=ci(bd[:, 0]), target_ci95=ci(bd[:, 1]), D_ci95=ci(bd[:, 2]),
                                       threshold_ci95=ci(bd[:, 3]), boot_success=int(len(bd)), boot_failed=int(B - len(bd)),
                                       D_frac_draws_gt_0=float(np.mean(bd[:, 2] > 0)) if len(bd) else None,
                                       D_frac_draws_lt_0=float(np.mean(bd[:, 2] < 0)) if len(bd) else None))
        log(f"config {cname} done")

    # ---------------- effective units / quantization descriptors (primary)
    def lag1(runs, th, thr):
        xs = [(scores(th, r) > thr).astype(float) for r in runs]
        mu = np.mean(np.concatenate(xs))
        num = sum(np.sum((x[1:] - mu) * (x[:-1] - mu)) for x in xs); den = sum(np.sum((x - mu) ** 2) for x in xs)
        return float(num / den) if den > 0 else None
    eff = []
    for s in SCEN:
        for (A, Bm) in PAIRS:
            mm = M(s, A, "primary")
            if mm is None: continue
            th, thr = mm
            eff.append(dict(scenario=s, source=A, target=Bm, cal_runs=6, holdout_runs=4, target_runs=4,
                            cal_samples=int(sum(len(scores(th, r)) for r in cal[s][A])),
                            holdout_samples=int(sum(len(scores(th, r)) for r in hold[s][A])),
                            target_samples=int(sum(len(scores(th, block[s][Bm][r])) for r in range(2, 6))),
                            lag1_exceed_cal=lag1(cal[s][A], th, thr), lag1_exceed_holdout=lag1(hold[s][A], th, thr),
                            lag1_exceed_target=lag1([block[s][Bm][r] for r in range(2, 6)], th, thr)))
    quant = {}
    for s in SCEN:
        allr = [r for A in ARMS for r in cal[s][A]]
        u = np.concatenate([r["u"] for r in allr]); f = np.concatenate([r["f"] for r in allr])
        quant[s] = dict(u_distinct=int(len(np.unique(u))), u_step=float(np.min(np.diff(np.unique(u)))),
                        u_range=[float(u.min()), float(u.max())], f_step=float(np.min(np.diff(np.unique(f)))),
                        u_quant_noise_std_V=0.1 / np.sqrt(12))
    pd.DataFrame(rows_hold).to_csv(OUT / "holdout_by_controller.csv", index=False)
    pd.DataFrame(rows_pairs).to_csv(OUT / "chain_pairs.csv", index=False)
    pd.DataFrame(rows_time).to_csv(OUT / "time_drift_diagnostic.csv", index=False)
    pd.DataFrame(rows_I).to_csv(OUT / "interleaved_pass_matrix.csv", index=False)
    pd.DataFrame(rows_R).to_csv(OUT / "rotation_matrix.csv", index=False)
    pd.DataFrame(eff).to_csv(OUT / "effective_units.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(dict(point_fit_failures=failures, bootstrap_failures=boot_fail,
                                                      quantization=quant, B=B, seed=SEED), indent=2, default=str) + "\n")
    log(f"analysis complete; files opened in total: {len(set(OPENED))} (expected 88)")
    assert len(set(OPENED)) == 88
    (OUT / "run_log.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
