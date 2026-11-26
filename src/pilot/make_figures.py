"""Paper figures. Run from the repo root after controls_test5.py (BM25 and --dense): python3 -B src/pilot/make_figures.py
Every plotted number is read from reports/pilot_controls_test5_{bm25,dense}.json.
Visual conventions follow ChenLiu-1996/figures4papers (blue for our method, reds for baselines, green for positive variants,
black bar edges, no top/right spines, frameless legend, values on bars); the code here is written for this project.
Figures are drawn at final print size (ACL column 3.25 in, text width 6.75 in) so font sizes are the sizes on the page."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update({"font.family": ["Arial", "Helvetica", "DejaVu Sans"], "font.size": 7.5, "axes.linewidth": 1.0,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "xtick.major.width": 1.0, "ytick.major.width": 1.0, "hatch.linewidth": 0.6,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})
BLUE, BLUE2, GREEN, RED, PINK, ROSE, GREY, DGREY = "#0F4D92", "#3775BA", "#8BCF8B", "#B64342", "#E9A6A1", "#F6CFCB", "#CFCECE", "#4D4D4D"
R = {k: json.load(open(f"reports/pilot_controls_test5_{k}.json")) for k in ("bm25", "dense")}
OUT = "paper/figures"

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(f"{OUT}/{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

# ---------------------------------------------------------------- Figure 1: the two clocks (dates verified in data/pilot/corpus.json)
def timeline():
    import datetime as dt, matplotlib.dates as md
    D = dt.date
    fig, ax = plt.subplots(figsize=(3.25, 2.0))
    q, end = D(2019, 11, 1), D(2020, 4, 1)
    for y, name, p, e, stop, col in [(1.0, "2018-18209", D(2018, 8, 27), D(2019, 1, 1), D(2020, 1, 1), BLUE),
                                     (0.0, "2019-16300", D(2019, 8, 1), D(2020, 1, 1), end, RED)]:
        ax.plot([p, e], [y, y], ls=(0, (2, 1.5)), lw=1.4, color=col)
        ax.add_patch(plt.Rectangle((md.date2num(e), y - 0.13), md.date2num(stop) - md.date2num(e), 0.26, fc=col, ec="black", lw=0.8))
        ax.plot(p, y, "o", ms=5, color=col, mec="black", mew=0.8)
        ax.text(p if y else p + dt.timedelta(days=20), y + 0.24, f"{name}\npublished", ha="left" if y else "right", va="bottom", fontsize=6.5, linespacing=1.0)
    ax.plot([q, q], [-0.6, 1.95], color=DGREY, lw=1.0, ls=":")
    ax.text(q, 1.98, "query: 1 Nov 2019", ha="center", va="bottom", fontsize=7)
    ax.text(D(2019, 5, 1), 1.0, "in force", color="white", ha="center", va="center", fontsize=6.5, fontweight="bold")
    ax.text(q - dt.timedelta(days=8), -0.2, "announced,\nnot in force", color=RED, ha="right", va="top", fontsize=6.5, linespacing=1.0)
    ax.text(D(2018, 8, 27), -1.18, "valid-at answer: 2018-18209", color=BLUE, fontsize=7, fontweight="bold")
    ax.text(D(2018, 8, 27), -1.48, "known-at answer: 2019-16300", color=RED, fontsize=7, fontweight="bold")
    ax.set_xlim(D(2018, 8, 1), end); ax.set_ylim(-1.55, 2.0)
    ax.xaxis.set_major_locator(md.MonthLocator(bymonth=(1, 7))); ax.xaxis.set_major_formatter(md.DateFormatter("%b %Y"))
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_position(("data", -0.6)); ax.tick_params(axis="x", labelsize=6.5, pad=1)
    save(fig, "fig_timeline")

# ---------------------------------------------------------------- Figure 2: overall comparison
METHODS = [  # (key, legend label, colour, hatch)
    ("B0 ungated", "B0 retrieval only", GREY, ""),
    ("B2 ungated", "B2 publication cutoff", ROSE, ""), ("B2 gated", "B2 + gate", ROSE, "////"),
    ("B3 ungated", "B3 validity filter", PINK, ""), ("B3 gated", "B3 + gate", PINK, "////"),
    ("B6 ungated", "B6 soft distance", RED, ""), ("B6 gated", "B6 + gate", RED, "////"),
    ("require both clocks, no router", "both clocks, no router", GREEN, "////"),
    ("v1", "routed v1 (weighted)", BLUE2, ""), ("v2", "routed v2 (gated)", BLUE, "////")]
XPOS = [0, 1.4, 2.4, 3.8, 4.8, 6.2, 7.2, 8.6, 10.0, 11.0]

def overall():
    fig, axes = plt.subplots(1, 4, figsize=(6.75, 2.05), gridspec_kw={"width_ratios": [1, 1, 1, 0.62]})
    for ax, (res, metric, title) in zip(axes, [("bm25", "top1", "Top-1, BM25"), ("dense", "top1", "Top-1, dense"), ("bm25", "inadmissible", "Inadmissible top result, BM25")]):
        for x, (key, label, col, hatch) in zip(XPOS, METHODS):
            v = R[res]["methods"][key][metric]
            ax.bar(x, v, width=0.95, color=col, edgecolor="black", linewidth=0.8, hatch=hatch, label=label)
            ax.text(x, v + 0.015, f"{v:.2f}".lstrip("0") if v < 1 else "1.0", ha="center", va="bottom", fontsize=5.8, rotation=90,
                    bbox=dict(fc="white", ec="none", pad=0.2))
        if metric == "top1":
            a = R[res]["abstain_always"]
            ax.axhline(a, color=DGREY, lw=0.9, ls="--", zorder=0)
        ax.set_title(title, fontsize=7.5, pad=3)
        ax.set_ylim(0, 0.95); ax.set_yticks([0, .2, .4, .6, .8]); ax.set_xticks([]); ax.set_xlim(-0.7, 11.7)
    handles, labels = axes[0].get_legend_handles_labels()
    handles.append(plt.Line2D([], [], color=DGREY, lw=0.9, ls="--")); labels.append("always abstain")
    axes[3].set_axis_off()
    axes[3].legend(handles, labels, loc="center left", bbox_to_anchor=(-0.18, 0.5), fontsize=6.5, handlelength=1.5, handleheight=1.0, labelspacing=0.45)
    fig.tight_layout(pad=0.3, w_pad=0.8)
    save(fig, "fig_overall")

# ---------------------------------------------------------------- Figure 3: where each clock fails
def by_intent():
    rows = [("B2 gated", "B2 publication cutoff + gate", ROSE), ("B3 gated", "B3 validity filter + gate", PINK),
            ("require both clocks, no router", "both clocks, no router", GREEN), ("v2", "routed v2", BLUE)]
    intents = [("current", "current"), ("valid_at", "valid-at"), ("known_at", "known-at"), ("valid_known", "valid-known")]
    fig, axes = plt.subplots(1, 2, figsize=(6.75, 1.85), sharey=True)
    for ax, (res, title) in zip(axes, [("bm25", "BM25"), ("dense", "dense")]):
        for j, (key, label, col) in enumerate(rows):
            for i, (it, _) in enumerate(intents):
                v = R[res]["methods"][key][it]; x = i + (j - 1.5) * 0.21
                ax.bar(x, v, width=0.2, color=col, edgecolor="black", linewidth=0.8, label=label if i == 0 else None)
                ax.text(x, v + 0.02, f"{v:.2f}".lstrip("0"), ha="center", va="bottom", fontsize=5.5, rotation=90)
        ax.set_xticks(range(len(intents))); ax.set_xticklabels([n for _, n in intents]); ax.tick_params(axis="x", length=0)
        ax.set_title(title, fontsize=7.5, pad=3); ax.set_ylim(0, 1.08); ax.set_yticks([0, .25, .5, .75, 1.0])
    axes[0].set_ylabel("top-1")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=6.5, bbox_to_anchor=(0.5, -0.13), handlelength=1.5)
    fig.tight_layout(pad=0.3, w_pad=1.0)
    save(fig, "fig_by_intent")

# ---------------------------------------------------------------- Figure 4: ablation and diagnostics
def ablation():
    rows = [("v2", "full routed v2", BLUE), ("no semantic gate", "no semantic gate", BLUE2),
            ("fixed valid_at", "always valid-at", GREEN), ("fixed valid_known", "always valid-known", GREEN), ("fixed known_at", "always known-at", GREEN),
            ("no eligibility", "no eligibility", RED), ("no eligibility, absolute gap", "no eligibility, abs. gap", PINK), None,
            ("v2, oracle family", "gold family given", GREY), ("v2, oracle intent and dates (case metadata)", "oracle intent and dates", GREY),
            ("v2, title cut to 4 words", "title cut to 4 words", GREY)]
    fig, ax = plt.subplots(figsize=(3.25, 2.55))
    y, ticks, names = 0.0, [], []
    for row in rows:
        if row is None:
            ax.axhline(y - 0.25, color=DGREY, lw=0.7, ls=":"); ax.text(1.12, y + 0.12, "diagnostics", ha="right", va="center", fontsize=6.5, color=DGREY)
            y += 1.0; continue
        key, label, col = row; m = R["bm25"]["methods"][key]
        ax.barh(y, m["top1"], height=0.8, color=col, edgecolor="black", linewidth=0.8)
        ax.text(m["top1"] + 0.015, y, f"{m['top1']:.2f}".lstrip("0"), va="center", fontsize=6.5)
        ticks.append(y); names.append(label); y += 1.0
    ax.set_yticks(ticks); ax.set_yticklabels(names, fontsize=6.8); ax.tick_params(axis="y", length=0)
    ax.invert_yaxis(); ax.set_xlim(0, 1.12); ax.set_xticks([0, .25, .5, .75, 1.0]); ax.set_xlabel("top-1 (BM25)", labelpad=1)
    save(fig, "fig_ablation")

timeline(); overall(); by_intent(); ablation()
print("figures written to", OUT)
