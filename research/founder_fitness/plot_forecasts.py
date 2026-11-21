"""Render the endpoint forecast comparison from the three published score files."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


HERE = Path(__file__).resolve().parent
INK = '#192F3C'
MUTED = '#4C626E'
GRID = '#DAE3E6'
STYLES = {
    'start': ('Starting share', 'o', '#526676', 'white'),
    'rate': ('Assay rate alone', '^', '#AB560F', '#AB560F'),
    'combined': ('Starting share + assay rate', 's', '#007568', '#007568'),
}


def yeast_row(label, detail, sample):
    hits = sample['hits']
    mae = sample['mean_absolute_share_errors']
    return (label, detail,
            {k: (hits[name], sample['n']) for k, name in
             [('start', 'baseline'), ('rate', 'assay'), ('combined', 'combined')]},
            {'start': 100 * mae['baseline'], 'combined': 100 * mae['combined']})


def load_rows():
    primary = json.loads((HERE / 'results.json').read_text())
    proof = json.loads((HERE / 'proof_assay' / 'proof_native_receipt.json').read_text())
    subset = primary['by_condition']['1']
    assert (subset['n'], subset['hits']['baseline'], subset['hits']['combined']) == (
        proof['wells'], proof['baseline_hits'], proof['main']['combined'])
    assert abs(subset['mean_absolute_share_errors']['baseline'] - proof['baseline_mae']) < 1e-7
    proof_sample = {
        'n': proof['wells'],
        'hits': {'baseline': proof['baseline_hits'], 'assay': proof['proof']['assay'],
                 'combined': proof['proof']['combined']},
        'mean_absolute_share_errors': {'baseline': proof['baseline_mae'],
                                       'combined': proof['proof']['combined_mae']},
    }
    rows = [yeast_row('Full cohort', f"{primary['all']['n']} wells · main assay", primary['all']),
            yeast_row('Standard diploid subset', f"{subset['n']} wells · main assay", subset),
            yeast_row(f"Same {proof['wells']} wells", 'Separate proof-of-concept assay', proof_sample)]
    with (HERE / 'algae' / 'results' / 'algae_validation.csv').open(newline='') as data:
        for r in csv.DictReader(data):
            if r['classifier'] == 'lda':
                rows.append((f"Day {r['day']}", f"{r['n']} competition observations",
                             {'combined': (int(r['correct']), int(r['decisive']))},
                             {'start': 100 * float(r['mae_half']), 'combined': 100 * float(r['mae_rate'])}))
    assert len(rows) == 6
    return rows


def draw_mark(axis, x, y, key, value):
    _, marker, edge, face = STYLES[key]
    axis.plot(x, y, marker=marker, markersize=6.3, markeredgewidth=1.5,
              markeredgecolor=edge, markerfacecolor=face, linestyle='none', zorder=3)
    axis.annotate(value, (x, y), xytext=(7.5, 0), textcoords='offset points',
                  ha='left', va='center', fontsize=8.7, color=edge, fontweight='medium')


def axis_style(ax, ticks, xmax):
    ax.set_ylim(8.02, -0.38)
    ax.set_xlim(-2, xmax)
    ax.set_xticks(ticks)
    ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=8.5, labelcolor=MUTED, length=0, pad=5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color=GRID, linewidth=0.65)
    ax.patch.set_alpha(0)


def main():
    rows = load_rows()
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white',
                         'savefig.facecolor': 'white', 'figure.dpi': 130})
    fig = plt.figure(figsize=(11.0, 7.05))
    left, bottom, height = 0.048, 0.140, 0.62
    direction_left, error_left = 0.344, 0.702
    labels = fig.add_axes([left, bottom, 0.275, height])
    direction = fig.add_axes([direction_left, bottom, 0.31, height])
    error = fig.add_axes([error_left, bottom, 0.26, height])
    labels.set_xlim(0, 1)
    labels.set_ylim(8.02, -0.38)
    labels.set_axis_off()
    axis_style(direction, [0, 25, 50, 75, 100], 111)
    axis_style(error, [0, 10, 20, 30, 40, 50], 55)
    for y, name in [(0.00, 'Yeast  ·  day 25'), (4.48, 'Freshwater green algae')]:
        labels.text(0, y, name, fontsize=12, fontweight='bold', va='center')
    centers = [0.87, 2.10, 3.33, 5.26, 6.45, 7.64]
    for i, ((label, detail, hits, mae), center) in enumerate(zip(rows, centers)):
        labels.text(0, center - 0.10, label, va='center', fontsize=10.8, weight='medium')
        labels.text(0, center + 0.21, detail, va='center', fontsize=8.55, color=MUTED)
        offsets = {'start': -0.27, 'rate': 0, 'combined': 0.27} if i < 3 else {'combined': 0}
        for method, (n_hits, n_decisive) in hits.items():
            draw_mark(direction, 100 * n_hits / n_decisive, center + offsets[method], method,
                      f'{n_hits}/{n_decisive}')
        for method, offset in [('start', -0.16), ('combined', 0.16)]:
            draw_mark(error, mae[method], center + offset, method, f'{mae[method]:.1f}')
    fig.text(left, 0.955, 'Forecasts from starting abundance and measured fitness', va='top',
             fontsize=19.0, weight='bold')
    handles = [Line2D([], [], label=label, linestyle='none', marker=marker, markersize=6.3,
                      markeredgewidth=1.5, markeredgecolor=edge, markerfacecolor=face)
               for label, marker, edge, face in STYLES.values()]
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(left-0.006, 0.904),
               frameon=False, ncol=3, borderaxespad=0, handletextpad=0.35,
               columnspacing=1.45, fontsize=10)
    for x, title, subtitle in [(direction_left, 'Correct final leader', '% of decisive outcomes · higher is better'),
                               (error_left, 'Mean absolute share error', 'Percentage points · lower is better')]:
        fig.text(x, 0.818, title, fontsize=12.6, fontweight='bold', va='baseline')
        fig.text(x, 0.790, subtitle, fontsize=8.75, color=MUTED, va='baseline')
    divider_y = bottom + height * (8.02 - 4.005) / (8.02 + 0.38)
    fig.add_artist(Line2D([left, 0.96], [divider_y, divider_y], transform=fig.transFigure,
                          color='#B9C8CC', linewidth=0.8))
    fig.text(left, 0.076, 'Yeast subset rows use the same endpoint observations. Algal pairs began at equal shares, so only the rate gives a directional forecast.',
             fontsize=8.65, color=MUTED)
    fig.text(left, 0.047, 'Share error includes ties. Algal days are repeated observations and use the original linear discriminant cell classifications.',
             fontsize=8.65, color=MUTED)
    fig.text(left, 0.018, 'Data from Fasanello et al. (2020), PeerJ 8, e10118, and Bestion et al. (2018), Ecology Letters 21, 655–664.',
             fontsize=8.4, color=MUTED)
    fig.savefig(HERE / 'forecast_comparison.png', dpi=240,
                metadata={'Title': 'Forecasts from starting abundance and measured fitness'})
    plt.close(fig)


if __name__ == '__main__':
    main()
