"""Reproduce public statistical tables and figures from derived research inputs only."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
CHANNELS = ("r_y", "r_u", "joint")
LABELS = {"r_y": "Speed", "r_u": "Effort", "joint": "Joint"}


def rows(name: str) -> list[dict[str, str]]:
    path = DATA / name
    if not path.resolve().is_relative_to(DATA.resolve()):
        raise ValueError("Input escaped the public processed-data directory")
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not values:
        raise ValueError(f"No rows for {path.name}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(values[0]))
        writer.writeheader()
        writer.writerows(values)


def far(r: dict[str, str]) -> float:
    return int(r["exceedance_count"]) / int(r["evaluation_samples"])


def pct(value: float, digits: int = 2) -> str:
    return f"{100 * value:.{digits}f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results",
                        help="Output directory; all inputs still come from this public tree")
    args = parser.parse_args()
    out = args.output.resolve()
    tables = out / "tables"
    figures = out / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    config = json.loads((ROOT / "config/release_analysis.json").read_text(encoding="utf-8"))
    target = float(config["target_false_alarm"])
    assert config["random_seed"] == 33043  # processed stage is deterministic; no random draws here

    controllers = rows("controllers.csv")
    runs = rows("runs.csv")
    ids = [r["controller_id"] for r in controllers]
    assert ids == [f"C{i:02d}" for i in range(1, 10)]
    assert len(runs) == 11
    assert sum(int(r["complete_cycle_count"]) for r in controllers) == 85
    write(tables / "table1_controllers.csv", controllers)

    primary = rows("primary_transfer_counts.csv")
    cross = [r for r in primary if r["validation_type"] == "CROSS_CONTROLLER"]
    table2 = []
    for channel in CHANNELS:
        subset = [far(r) for r in cross if r["channel"] == channel]
        assert len(subset) == 32
        table2.append({"channel": channel, "pair_count": len(subset),
                       "median_far": statistics.median(subset),
                       "q95_far": float(np.percentile(subset, 95)),
                       "maximum_far": max(subset),
                       "maximum_absolute_error": max(abs(x - target) for x in subset)})
    write(tables / "table2_primary_transfer.csv", table2)

    matrices = {}
    for channel in CHANNELS:
        subset = [r for r in primary if r["channel"] == channel]
        source_ids = [f"C{i:02d}" for i in range(1, 5)]
        assert len(subset) == 36
        cells = {(r["calibration_controller"], r["evaluation_controller"]): far(r) for r in subset}
        assert len(cells) == 36
        matrix_rows = [{"calibration_controller": src, **{dst: cells[(src, dst)] for dst in ids}}
                       for src in source_ids]
        write(tables / f"far_matrix_{channel}.csv", matrix_rows)
        matrices[channel] = np.array([[cells[(src, dst)] for dst in ids] for src in source_ids])

    category = rows("run_transfer_counts.csv")
    category_summary = []
    for kind in ("WITHIN_RUN", "SAME_CONTROLLER_CROSS_RUN", "CROSS_CONTROLLER"):
        for channel in CHANNELS:
            subset = [far(r) for r in category if r["category"] == kind and r["channel"] == channel]
            category_summary.append({"category": kind, "channel": channel, "transfer_count": len(subset),
                                     "median_far": statistics.median(subset),
                                     "maximum_far": max(subset),
                                     "median_absolute_calibration_error": statistics.median(abs(x-target) for x in subset)})
    write(tables / "transfer_category_summary.csv", category_summary)
    same = [r for r in category if r["category"] == "SAME_CONTROLLER_CROSS_RUN"]
    assert len(same) == 12
    assert {(r["calibration_run"], r["evaluation_run"]) for r in same} == {
        ("9", "10"), ("10", "9"), ("13", "18"), ("18", "13")}
    table3 = []
    for source, target_run in (("9","10"),("10","9"),("13","18"),("18","13")):
        group = [r for r in same if r["calibration_run"] == source and r["evaluation_run"] == target_run]
        assert len(group) == 3
        base = group[0]
        table3.append({"controller": base["calibration_controller"], "calibration_run": source,
                       "evaluation_run": target_run, "calibration_cycles": base["calibration_cycles"],
                       "evaluation_cycles": base["evaluation_cycles"],
                       **{r["channel"] + "_far": far(r) for r in group}})
    write(tables / "table3_same_controller_runs.csv", table3)
    contrasts = {}
    for channel in CHANNELS:
        lookup = {r["category"]: r for r in category_summary if r["channel"] == channel}
        contrasts[channel] = (float(lookup["CROSS_CONTROLLER"]["median_absolute_calibration_error"]) /
                              float(lookup["SAME_CONTROLLER_CROSS_RUN"]["median_absolute_calibration_error"]))

    pooled = rows("pooled_evaluation_counts.csv")
    methods = ("POOLED_GLOBAL", "BALANCED_GLOBAL", "LOCO_POOLED", "LOCO_BALANCED")
    table4 = [{"method": "SINGLE_CONTROLLER_TRANSFER", **{ch: next(r["maximum_far"] for r in table2
               if r["channel"] == ch) for ch in CHANNELS}}]
    for method in methods:
        table4.append({"method": method,
                       **{ch: max(far(r) for r in pooled if r["method"] == method and r["channel"] == ch)
                          for ch in CHANNELS}})
    write(tables / "table4_calibration_strategies.csv", table4)

    diversity = rows("diversity_cells.csv")
    diversity_summary = []
    for count in range(1, 9):
        for method in ("DURATION_WEIGHTED_ALL_CYCLES", "EQUAL_CONTROLLER_FOUR_CYCLES"):
            for channel in CHANNELS:
                subset = [float(r["unseen_controller_far"]) for r in diversity
                          if int(r["calibration_controller_count"]) == count and
                          r["pooling_method"] == method and r["channel"] == channel]
                assert subset
                diversity_summary.append({"calibration_controller_count": count, "pooling_method": method,
                                          "channel": channel, "subset_target_count": len(subset),
                                          "median_unseen_controller_far": statistics.median(subset),
                                          "q95_unseen_controller_far": float(np.percentile(subset, 95)),
                                          "worst_unseen_controller_far": max(subset)})
    write(tables / "calibration_diversity_summary.csv", diversity_summary)

    simulation = rows("simulation_exceedance_counts.csv")
    sensitivity_summary = []
    for mode in ("A_reduction", "B_increase"):
        for severity in ("0.0", "0.05", "0.1", "0.2", "0.3"):
            for strategy in ("SINGLE_CONTROLLER_HELD_OUT", "DURATION_POOLED_GLOBAL",
                             "CONTROLLER_BALANCED_GLOBAL", "DURATION_POOLED_LOCO"):
                for channel in CHANNELS:
                    subset = [r for r in simulation if r["degradation_mode"] == mode and
                              r["severity_fraction"] == severity and r["strategy"] == strategy and
                              r["channel"] == channel]
                    assert len(subset) == 9
                    sensitivity_summary.append({"degradation_mode": mode, "severity_fraction": severity,
                                                "strategy": strategy, "channel": channel,
                                                "sample_weighted_exceedance_fraction":
                                                sum(int(r["exceedance_count"]) for r in subset) /
                                                sum(int(r["evaluation_samples"]) for r in subset),
                                                "quantity": "observed nominal-operation sample FAR" if severity == "0.0"
                                                else "simulation-based threshold-exceedance sensitivity"})
    write(tables / "simulation_sensitivity_summary.csv", sensitivity_summary)

    reciprocal = rows("reciprocal_score_statistics.csv")
    mechanism = []
    for r in reciprocal:
        mechanism.append({"direction": r["direction"], "channel": r["channel"],
                          "calibration_threshold": r["calibration_threshold"],
                          "mad_ratio_target_over_source": float(r["target_mad"]) / float(r["source_mad"]),
                          "q99_ratio_target_over_source": float(r["target_q99"]) / float(r["source_q99"]),
                          "wasserstein_distance": r["wasserstein_distance"],
                          "ks_statistic_descriptive": r["ks_statistic_descriptive"]})
    write(tables / "reciprocal_score_mechanism.csv", mechanism)
    effort_mechanism = next(r for r in mechanism if r["direction"] == "C04_TO_C01" and r["channel"] == "r_u")
    assert round(effort_mechanism["mad_ratio_target_over_source"],2) == 2.39
    assert round(effort_mechanism["q99_ratio_target_over_source"],2) == 2.42

    ablation = rows("far_target_ablation_counts.csv")
    appendix_c = []
    for nominal in ("0.005","0.01","0.02","0.05"):
        group = {"nominal_target_far": nominal}
        for channel in CHANNELS:
            subset = [far(r) for r in ablation if r["nominal_target_far"] == nominal and
                      r["channel"] == channel]
            assert len(subset) == 32
            group[channel + "_maximum_far"] = max(subset)
        appendix_c.append(group)
    write(tables / "appendix_c_far_target_ablation.csv", appendix_c)

    intervals = rows("archived_cycle_bootstrap_intervals.csv")
    effort_interval = next(r for r in intervals if r["calibration_controller"] == "C04" and
                           r["evaluation_controller"] == "C01" and r["channel"] == "r_u")
    c07_local = next(r for r in simulation if r["degradation_mode"] == "A_reduction" and
                     r["severity_fraction"] == "0.1" and r["strategy"] == "SINGLE_CONTROLLER_HELD_OUT" and
                     r["evaluation_controller"] == "C07" and r["channel"] == "r_u")
    c07_loco = next(r for r in simulation if r["degradation_mode"] == "A_reduction" and
                    r["severity_fraction"] == "0.1" and r["strategy"] == "DURATION_POOLED_LOCO" and
                    r["evaluation_controller"] == "C07" and r["channel"] == "r_u")
    headline = {
        "primary_effort_maximum_far": next(r["maximum_far"] for r in table2 if r["channel"] == "r_u"),
        "primary_effort_maximum_pair": "C04->C01",
        "archived_cycle_bootstrap_95pct_interval": [float(effort_interval["ci_low"]), float(effort_interval["ci_high"])],
        "same_controller_maximum_far": {ch: max(float(r[ch + "_far"]) for r in table3) for ch in CHANNELS},
        "calibration_error_contrast": contrasts,
        "balanced_diversity_worst_effort_one_controller": next(r["worst_unseen_controller_far"] for r in diversity_summary
            if r["calibration_controller_count"] == 1 and r["pooling_method"] == "EQUAL_CONTROLLER_FOUR_CYCLES" and r["channel"] == "r_u"),
        "balanced_diversity_worst_effort_eight_controllers": next(r["worst_unseen_controller_far"] for r in diversity_summary
            if r["calibration_controller_count"] == 8 and r["pooling_method"] == "EQUAL_CONTROLLER_FOUR_CYCLES" and r["channel"] == "r_u"),
        "c07_A_reduction_10pct_effort_local_exceedance": far(c07_local),
        "c07_A_reduction_10pct_effort_duration_LOCO_exceedance": far(c07_loco),
        "c04_to_c01_effort_mad_ratio": effort_mechanism["mad_ratio_target_over_source"],
        "c04_to_c01_effort_q99_ratio": effort_mechanism["q99_ratio_target_over_source"],
    }
    assert abs(headline["primary_effort_maximum_far"] - 0.14072916666666666) < 1e-12
    assert round(100*headline["same_controller_maximum_far"]["r_u"], 2) == 1.39
    assert [round(100*x,2) for x in headline["archived_cycle_bootstrap_95pct_interval"]] == [13.34,14.71]
    assert round(100*headline["balanced_diversity_worst_effort_one_controller"],2) == 45.86
    assert round(100*headline["balanced_diversity_worst_effort_eight_controllers"],2) == 3.76
    assert round(100*headline["c07_A_reduction_10pct_effort_local_exceedance"],2) == 39.10
    assert headline["c07_A_reduction_10pct_effort_duration_LOCO_exceedance"] == 0
    (tables / "headline_results.json").write_text(json.dumps(headline, indent=2) + "\n", encoding="utf-8")

    render_figures(figures, controllers, matrices, category, diversity_summary, sensitivity_summary)
    print("Public Level A reproduction complete")
    print("14.07% C04→C01 effort; same-controller maxima:",
          ", ".join(f"{ch} {pct(value)}" for ch,value in headline["same_controller_maximum_far"].items()))
    print("Calibration-error contrast:", ", ".join(f"{ch} {value:.2f}x" for ch,value in contrasts.items()))
    print("Outputs:", tables, "and", figures)


def render_figures(figures: Path, controllers: list[dict[str, str]], matrices: dict[str, np.ndarray],
                   category: list[dict[str, str]], diversity: list[dict], sensitivity: list[dict]) -> None:
    # Figure 2: archive coverage from derived controller metadata.
    fig, ax = plt.subplots(figsize=(9.5,5.4), layout="constrained")
    ids = [r["controller_id"] for r in controllers]
    counts = [int(r["complete_cycle_count"]) for r in controllers]
    y = np.arange(len(ids))
    bars = ax.barh(y, counts, color=["#21618C" if int(r["independent_run_count"]) > 1 else "#79AFC8"
                                      for r in controllers])
    ax.set_yticks(y, ids); ax.invert_yaxis(); ax.set_xlim(0,max(counts)+12)
    ax.set_xlabel("Complete four-second cycles"); ax.set_title("Recorded nominal-operation cycles by recovered PI controller")
    ax.grid(axis="x", alpha=.22); ax.set_axisbelow(True)
    for bar,r in zip(bars,controllers):
        run_label = ", ".join(f"{int(value):02d}" for value in r["run_ids"].split(";"))
        ax.text(bar.get_width()+.35, bar.get_y()+bar.get_height()/2,
                f"runs {run_label}   ·   ωb={float(r['closed_loop_bandwidth_rad_s']):.1f} rad/s",
                va="center", fontsize=9)
    ax.text(.99,.02,"Dark bars: independent repeated runs",transform=ax.transAxes,ha="right",va="bottom",fontsize=9)
    fig.savefig(figures / "figure2_controller_coverage.png",dpi=220); plt.close(fig)

    # Figure 3: full-range transfer matrix; each channel retains its own colour range.
    fig, axes = plt.subplots(1,3,figsize=(15.5,5.2),layout="constrained")
    for ax,ch in zip(axes,CHANNELS):
        data = 100*matrices[ch]
        im = ax.imshow(data,aspect="auto",cmap="viridis",vmin=0,vmax=float(data.max()))
        ax.set_xticks(range(9),[f"C{i:02d}" for i in range(1,10)],rotation=45,ha="right")
        ax.set_yticks(range(4),[f"C{i:02d}" for i in range(1,5)])
        ax.set_title(LABELS[ch]); ax.set_xlabel("Evaluation controller")
        if ch == "r_y": ax.set_ylabel("Calibration controller")
        for i in range(4):
            for j in range(9):
                ax.text(j,i,f"{data[i,j]:.1f}",ha="center",va="center",fontsize=7,
                        color="white" if data[i,j] < data.max()*.65 else "black")
        fig.colorbar(im,ax=ax,label="Sample FAR (%)",shrink=.85)
    fig.suptitle("Nominal-operation sample FAR at 1% calibration target",fontsize=13)
    fig.savefig(figures / "figure3_far_heatmaps.png",dpi=220); plt.close(fig)

    # Figure 4: archive comparison; the manuscript caption discloses omitted outliers.
    fig, axes = plt.subplots(1,3,figsize=(13,4),sharey=True,layout="constrained")
    kinds=("WITHIN_RUN","SAME_CONTROLLER_CROSS_RUN","CROSS_CONTROLLER")
    names=("Within run","Same controller\ncross run","Cross controller")
    for ax,ch in zip(axes,CHANNELS):
        values=[[100*far(r) for r in category if r["category"]==kind and r["channel"]==ch] for kind in kinds]
        ax.boxplot(values,tick_labels=names,showfliers=False)
        ax.axhline(1,color="black",linestyle="--"); ax.set_title(LABELS[ch]); ax.grid(axis="y",alpha=.25)
    axes[0].set_ylabel("Nominal-operation sample FAR (%)")
    fig.suptitle("Transfer category comparison; outliers omitted (see caption)")
    fig.savefig(figures / "figure4_transfer_categories.png",dpi=220); plt.close(fig)

    # Figure 6: source diversity and pooling weighting.
    fig,axes=plt.subplots(2,3,figsize=(13.5,7.3),sharex=True,layout="constrained")
    for col,ch in enumerate(CHANNELS):
        for row_index,(field,label) in enumerate((("q95_unseen_controller_far","95th percentile"),
                                                   ("worst_unseen_controller_far","Worst"))):
            ax=axes[row_index,col]
            for method,name,color in (("DURATION_WEIGHTED_ALL_CYCLES","Duration pooled","#4C78A8"),
                                      ("EQUAL_CONTROLLER_FOUR_CYCLES","Equal controller","#F58518")):
                series=sorted((r for r in diversity if r["pooling_method"]==method and r["channel"]==ch),
                              key=lambda r:r["calibration_controller_count"])
                ax.plot([r["calibration_controller_count"] for r in series],
                        [100*r[field] for r in series],marker="o",lw=1.9,color=color,label=name)
            ax.axhline(1,color="#555555",ls="--",lw=1); ax.set_title(f"{LABELS[ch]} · {label}")
            ax.grid(alpha=.22); ax.set_xticks(range(1,9))
            if row_index==1: ax.set_xlabel("Distinct calibration controllers")
            if col==0: ax.set_ylabel("Unseen-controller sample FAR (%)")
    axes[0,-1].legend(fontsize=9,loc="upper right")
    fig.suptitle("Calibration diversity: duration pooling and four-cycle controller balancing",fontsize=14)
    fig.savefig(figures / "figure6_diversity_pooling.png",dpi=220); plt.close(fig)

    # Figure 7: simulation-only positive severities; 0% is observed nominal FAR.
    strategies=(("SINGLE_CONTROLLER_HELD_OUT","Local held-out","#4C78A8"),
                ("DURATION_POOLED_GLOBAL","Duration global","#F58518"),
                ("CONTROLLER_BALANCED_GLOBAL","Balanced global","#54A24B"),
                ("DURATION_POOLED_LOCO","Duration LOCO","#B279A2"))
    fig,axes=plt.subplots(2,3,figsize=(13.5,7.2),sharex=True,layout="constrained")
    for row_index,(mode,title) in enumerate((("A_reduction","A reduced"),("B_increase","B increased"))):
        for col,ch in enumerate(CHANNELS):
            ax=axes[row_index,col]
            for method,name,color in strategies:
                series=sorted((r for r in sensitivity if r["degradation_mode"]==mode and
                               r["channel"]==ch and r["strategy"]==method),
                              key=lambda r:float(r["severity_fraction"]))
                ax.plot([100*float(r["severity_fraction"]) for r in series],
                        [100*r["sample_weighted_exceedance_fraction"] for r in series],
                        marker="o",lw=1.8,color=color,label=name)
            ax.set_title(f"{title} · {LABELS[ch]}"); ax.set_xticks([0,5,10,20,30]); ax.grid(alpha=.22)
            if row_index==1: ax.set_xlabel("Single M2 parameter change (%)")
            if col==0: ax.set_ylabel("Sample exceedance (%)")
    axes[0,-1].legend(fontsize=8,loc="upper left")
    fig.suptitle("Simulation sanity check (0%: observed nominal-operation FAR)",fontsize=14)
    fig.savefig(figures / "figure7_simulated_tradeoff.png",dpi=220); plt.close(fig)


if __name__ == "__main__":
    main()
