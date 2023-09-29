import dataclasses
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

plt.rcParams['font.sans-serif'] = ['Times New Roman']


@dataclasses.dataclass
class Metric:
    bitrate: list[float] = dataclasses.field(default_factory=list)
    psnr: list[float] = dataclasses.field(default_factory=list)


Path("figs").mkdir(0o755, parents=True, exist_ok=True)


def read_metrics(fp: Path):
    metrics: dict[str, Metric] = {}
    name = None
    with fp.open('r') as f:
        for row in f.readlines():
            row = row.rstrip('\n')
            if not row:
                continue
            name, bitrate, psnr, *_ = row.split()
            name, _ = name.rsplit('_', 1)
            bitrate = float(bitrate)
            psnr = float(psnr)

            metric = metrics.setdefault(name, Metric())
            metric.bitrate.append(bitrate)
            metric.psnr.append(psnr)
    return metrics


metrics = read_metrics(Path("metrics.txt"))
metrics_ref = read_metrics(Path("metrics_ref.txt"))

for name, metric in metrics.items():
    metric_ref = metrics_ref[name]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax: Axes = ax
    ax.set_xlabel("Total bitrate (Kbps)")
    ax.set_ylabel("PSNR (dB)")
    ax.set_title(name)
    ax.plot(metric.bitrate, metric.psnr, color='blue', marker='o', label="W Preprocess")
    ax.plot(metric_ref.bitrate, metric_ref.psnr, color='orange', marker='o', label="W/O preprocess")
    ax.legend()
    fig.savefig(f"figs/{name}.png")
    fig.savefig(f"figs/{name}.svg")
