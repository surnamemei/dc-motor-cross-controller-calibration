#!/usr/bin/env python3
"""Run inventory for Candidate A (DrLizarraga, Closed-Loop Learning-Based PID Tuning).

Reads every experiment_*.mat (one physical closed-loop step experiment each) and
writes manifests/candidate_A_runs.csv with acquisition parameters, recovered
signals summary, integrity flags and a firmware-replay check of the logged
command. No monitor, threshold or false-alarm statistic is computed.

Firmware replay (firmware/TunePID_L298N, C.ino + Policy): float32 PID
  e = r - y; P = Kp e; D = Kd (e - e_prev)/Ts; I_new = I + Ki Ts e
  u = sat(P + I_new + D); accept I_new if unsaturated or saturated with e
  pushing back; u = round(sat(P + I + D)); e_prev = e
  Policy: if |e| < deadband -> I = 0, e_prev = 0, motor stopped (logged u is
  still the C() output). Sample 0 is logged with u = 0 before C() runs.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

import numpy as np
import scipy.io as sio

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "raw" / "candidate_A_github"
OUT = ROOT / "manifests" / "candidate_A_runs.csv"


def f32(x):
    return np.float32(x)


def replay(r, y, Kp, Ki, Kd, Ts_ms, deadband, umin=-255.0, umax=255.0):
    Kp, Ki, Kd = f32(Kp), f32(Ki), f32(Kd)
    Ts = f32(Ts_ms) / f32(1000.0)
    umin, umax, db = f32(umin), f32(umax), f32(deadband)
    I = f32(0.0)
    ei = f32(0.0)
    out = np.zeros(len(r))
    for k in range(len(r)):
        if k == 0:
            out[k] = 0
            continue
        e = f32(r[k]) - f32(y[k])
        P = Kp * e
        D = Kd * (e - ei) / Ts
        In = I + Ki * Ts * e
        u = P + In + D
        us = min(max(u, umin), umax)
        if u == us or (u > umax and e < 0) or (u < umin and e > 0):
            I = In
        u = P + I + D
        u = min(max(u, umin), umax)
        ei = e
        out[k] = np.round(u)          # roundf: half away from zero; np.round is half-even
        if abs(np.float32(u) - np.trunc(u)) == 0.5:
            out[k] = np.trunc(u) + np.sign(u)
        if abs(e) < db:
            I = f32(0.0)
            ei = f32(0.0)
    return out


def s(x):
    if isinstance(x, np.ndarray):
        return "" if x.size == 0 else str(x.tolist())
    return str(x)


def main() -> int:
    files = sorted(REPO.glob("data/**/experiment_*.mat"))
    rows = []
    for f in files:
        rel = f.relative_to(REPO).as_posix()
        parts = rel.split("/")
        campaign, sub = parts[1], parts[2]
        row = {"file": rel, "campaign": campaign, "subfolder": sub,
               "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
        try:
            E = sio.loadmat(f, squeeze_me=True, struct_as_record=False)["E"]
        except Exception as e:  # noqa: BLE001
            row["load_error"] = str(e)
            rows.append(row)
            continue
        m, rq, ap, d, cmd = E.meta, E.request, E.applied, E.data, E.command
        row.update({
            "created_at": s(m.created_at), "stored_file_path": s(m.file_path), "tag": s(m.tag),
            "port": s(m.portName),
            "A_requested_deg": s(rq.A), "Kp_requested": s(rq.Kp), "Ki_requested": s(rq.Ki),
            "Kd_requested": s(rq.Kd),
        })
        ack_ok = isinstance(cmd.ackLine, str) and cmd.ackLine.startswith("ACK")
        end_ok = isinstance(cmd.endLine, str) and cmd.endLine.startswith("END")
        err = s(cmd.errLine)
        row.update({"ack_received": ack_ok, "end_received": end_ok, "err_line": err})
        if ack_ok:
            row.update({"A_applied_deg": s(ap.A_applied), "Kp": s(ap.Kp), "Ki": s(ap.Ki), "Kd": s(ap.Kd),
                        "t_step_ms": s(ap.t_step_ms), "Tf_ms": s(ap.Tf_ms), "Ts_ms": s(ap.Ts_ms),
                        "CPR": s(ap.CPR), "deadband_deg": s(ap.e_deadband), "u_min": s(ap.u_min),
                        "u_max": s(ap.u_max), "dir": s(ap.dir)})
        t = np.atleast_1d(np.asarray(d.t_ms, dtype=float))
        r = np.atleast_1d(np.asarray(d.r, dtype=float))
        y = np.atleast_1d(np.asarray(d.y, dtype=float))
        u = np.atleast_1d(np.asarray(d.u, dtype=float))
        n = len(t)
        row["n_samples"] = n
        if n >= 2 and ack_ok:
            Ts = float(ap.Ts_ms)
            expected = int(round(float(ap.Tf_ms) / Ts)) + 1
            dt = np.diff(t)
            A = float(ap.A_applied)
            post = t >= float(ap.t_step_ms)
            umax = float(ap.u_max)
            row.update({
                "expected_samples": expected,
                "t_first_ms": t[0], "t_last_ms": t[-1],
                "dt_unique_ms": ";".join(str(int(v)) for v in np.unique(dt)),
                "n_nonfinite": int(np.sum(~np.isfinite(np.r_[r, y, u]))),
                "ref_levels": ";".join(f"{v:g}" for v in np.unique(r)),
                "step_index": int(np.argmax(np.abs(r) > 0)) if np.any(np.abs(r) > 0) else -1,
                "y_final_deg": y[-1], "y_max_abs_deg": np.max(np.abs(y)),
                "final_abs_error_deg": abs(A - y[-1]),
                "overshoot_pct": (100 * (np.max(np.sign(A) * y) - abs(A)) / abs(A)) if A != 0 else np.nan,
                "frac_u_saturated": float(np.mean(np.abs(u) >= umax)),
                "frac_u_saturated_post_step": float(np.mean(np.abs(u[post]) >= umax)) if post.any() else np.nan,
                "frac_in_deadband_post_step": float(np.mean(np.abs(r[post] - y[post]) < float(ap.e_deadband))) if post.any() else np.nan,
                "y_moved": bool(np.max(np.abs(y)) > 2 * float(ap.DPP)),
            })
            ur = replay(r, y, float(ap.Kp), float(ap.Ki), float(ap.Kd), Ts, float(ap.e_deadband),
                        float(ap.u_min), umax)
            row["replay_max_abs_err"] = float(np.max(np.abs(ur - u)))
            row["replay_n_mismatch"] = int(np.sum(ur != u))
        flags = []
        if not ack_ok:
            flags.append("no_ACK")
        if not end_ok:
            flags.append("no_END")
        if err:
            flags.append("ERR")
        if "expected_samples" in row and n != row["expected_samples"]:
            flags.append("sample_count")
        if row.get("dt_unique_ms") and row["dt_unique_ms"] != str(int(float(ap.Ts_ms))):
            flags.append("irregular_time")
        if row.get("n_nonfinite"):
            flags.append("nonfinite")
        if row.get("frac_u_saturated_post_step", 0) and row["frac_u_saturated_post_step"] > 0.10:
            flags.append("saturation_gt10pct")
        if row.get("y_moved") is False:
            flags.append("no_motion")
        A = float(ap.A_applied) if ack_ok else np.nan
        if ack_ok and row.get("y_max_abs_deg", 0) > 1.5 * abs(A):
            flags.append("divergence_|y|>1.5A")
        if ack_ok and row.get("final_abs_error_deg", 0) > 2.0:
            flags.append("final_error_gt2deg")
        if row.get("replay_n_mismatch", 0):
            flags.append("replay_mismatch")
        row["flags"] = ";".join(flags)
        rows.append(row)
    keys = []
    for r_ in rows:
        for k in r_:
            if k not in keys:
                keys.append(k)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} experiment files -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
