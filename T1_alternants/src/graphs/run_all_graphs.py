#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Sequence

os.environ.setdefault("MPLBACKEND", "Agg")

GRAPHS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GRAPHS_DIR.parents[1]
CLEANED_DATA = PROJECT_ROOT / "cleaned_data" / "merged_tracks.csv"
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"


@dataclass(frozen=True)
class RunContext:
    project_root: Path
    cleaned_csv: Path
    outputs_root: Path
    graphs_dir: Path


@dataclass(frozen=True)
class GraphTask:
    key: str
    runner: Callable[[RunContext], Sequence[Path]]


def load_module(name: str, file_path: Path) -> ModuleType:
    """Charge dynamiquement un module depuis un chemin arbitraire."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module at {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def snapshot_files(directory: Path) -> Dict[Path, float]:
    """Construit une photographie des fichiers présents avec leur mtime."""
    if not directory.exists():
        return {}
    return {
        path: path.stat().st_mtime
        for path in directory.rglob("*")
        if path.is_file()
    }


def capture_outputs(directory: Path, callable_obj: Callable[[], None]) -> List[Path]:
    """Exécute une fonction et retourne les fichiers ajoutés ou modifiés."""
    directory.mkdir(parents=True, exist_ok=True)
    before = snapshot_files(directory)
    callable_obj()
    after = snapshot_files(directory)
    changed = [
        path
        for path, mtime in after.items()
        if path not in before or before[path] != mtime
    ]
    if changed:
        return sorted(changed)
    return sorted(after.keys())


def run_afc(context: RunContext) -> Sequence[Path]:
    module = load_module(
        "graphs_afc_main", context.graphs_dir / "afc" / "main.py"
    )
    output_dir = context.outputs_root / "afc"

    module.CSV_PATH = str(context.cleaned_csv)
    module.OUTPUT_PATH = output_dir.as_posix() + "/"

    return capture_outputs(output_dir, module.main)


def run_area_chart(context: RunContext) -> Sequence[Path]:
    module = load_module(
        "graphs_area_chart", context.graphs_dir / "area_chart" / "area_chart.py"
    )
    output_dir = context.outputs_root / "area_chart"

    def _run() -> None:
        module.generate_area_chart(
            csv_path=str(context.cleaned_csv),
            output_filename=str(output_dir / "area_chart_artists.png"),
        )

    return capture_outputs(output_dir, _run)


def run_bar_chart(context: RunContext) -> Sequence[Path]:
    module = load_module(
        "graphs_bar_chart", context.graphs_dir / "bar_chart" / "bar_chart.py"
    )
    output_dir = context.outputs_root / "bar_chart"

    def _run() -> None:
        df = module.load_data(str(context.cleaned_csv))
        energy = module.compute_energy_by_genre(df)
        module.plot_energy_by_genre(
            energy_by_genre=energy,
            output_path=str(output_dir / "energy_by_genre.png"),
        )

    return capture_outputs(output_dir, _run)


def run_bubble_chart(context: RunContext) -> Sequence[Path]:
    module = load_module(
        "graphs_bubble_chart", context.graphs_dir / "bubble_chart_albums" / "bubbleChart.py"
    )
    output_dir = context.outputs_root / "bubble_chart_albums"

    def _run() -> None:
        module.generate_bubble_chart(
            csv_path=str(context.cleaned_csv),
            output_filename=str(output_dir / "bubble_chart_albums.png"),
        )

    return capture_outputs(output_dir, _run)


def run_heatmap(context: RunContext) -> Sequence[Path]:
    module = load_module(
        "graphs_heatmap", context.graphs_dir / "heatmap_tracks_vs_albums" / "heatMap.py"
    )
    output_dir = context.outputs_root / "heatmap_tracks_vs_albums"

    def _run() -> None:
        module.generate_correlation_heatmap(
            csv_path=str(context.cleaned_csv),
            output_filename=str(output_dir / "heatmap_track_vs_album_correlation.png"),
        )

    return capture_outputs(output_dir, _run)


def run_pca(context: RunContext) -> Sequence[Path]:
    module = load_module("graphs_pca", context.graphs_dir / "pca" / "main.py")
    output_dir = context.outputs_root / "pca"

    module.ROOT = context.project_root
    module.CSV_PATH = context.cleaned_csv
    module.OUT_DIR = output_dir

    return capture_outputs(output_dir, module.run)


def run_pie(context: RunContext) -> Sequence[Path]:
    module = load_module("graphs_pie", context.graphs_dir / "pie" / "main.py")
    output_dir = context.outputs_root / "pie"

    data_path = context.cleaned_csv

    def _resolve_paths() -> tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        return data_path, output_dir

    module.resolve_paths = _resolve_paths

    return capture_outputs(output_dir, module.main)


def run_radar(context: RunContext) -> Sequence[Path]:
    module = load_module("graphs_radar", context.graphs_dir / "radar" / "main.py")
    output_dir = context.outputs_root / "radar"

    data_path = context.cleaned_csv

    def _resolve_paths() -> tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        return data_path, output_dir

    module.resolve_paths = _resolve_paths

    return capture_outputs(output_dir, module.main)


def run_scatter_plot(context: RunContext) -> Sequence[Path]:
    module = load_module("graphs_scatter", context.graphs_dir / "scatter_plot" / "scatter.py")
    output_dir = context.outputs_root / "scatter_plot"

    def _run() -> None:
        df = module.load_data(str(context.cleaned_csv))
        filtered = module.keep_first_n_tracks_per_album(df, n=50)
        avg = module.compute_average_listens(filtered)
        module.plot_average_listens(
            avg_listens=avg,
            output_path=str(output_dir / "scatter.png"),
            max_track=50,
        )

    return capture_outputs(output_dir, _run)


def run_scatter_genre_years(context: RunContext) -> Sequence[Path]:
    module = load_module(
        "graphs_scatter_genre_years",
        context.graphs_dir / "scatter_plot_genre_years" / "scatter_plot_genre_years.py",
    )
    output_dir = context.outputs_root / "scatter_plot_genre_years"

    def _run() -> None:
        module.plot_genre_popularity_by_year(
            csv_path=str(context.cleaned_csv),
            output=str(output_dir / "genre_popularity_by_year.png"),
        )

    return capture_outputs(output_dir, _run)


def ensure_cleaned_csv_exists(path: Path) -> None:
    """Vérifie que le fichier consolidé est disponible."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset at {path}. Run the cleaning pipeline beforehand."
        )


def build_tasks() -> Sequence[GraphTask]:
    return [
        GraphTask("afc", run_afc),
        GraphTask("area_chart", run_area_chart),
        GraphTask("bar_chart", run_bar_chart),
        GraphTask("bubble_chart_albums", run_bubble_chart),
        GraphTask("heatmap_tracks_vs_albums", run_heatmap),
        GraphTask("pca", run_pca),
        GraphTask("pie", run_pie),
        GraphTask("radar", run_radar),
        GraphTask("scatter_plot", run_scatter_plot),
        GraphTask("scatter_plot_genre_years", run_scatter_genre_years),
    ]


def main() -> int:
    ensure_cleaned_csv_exists(CLEANED_DATA)
    OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)

    context = RunContext(
        project_root=PROJECT_ROOT,
        cleaned_csv=CLEANED_DATA.resolve(),
        outputs_root=OUTPUTS_ROOT,
        graphs_dir=GRAPHS_DIR,
    )

    tasks = build_tasks()
    successes: list[tuple[str, Sequence[Path]]] = []
    failures: list[tuple[str, Exception]] = []

    for task in tasks:
        print(f"\n=== Running {task.key} ===")
        try:
            outputs = task.runner(context)
        except Exception as exc:  # noqa: BLE001
            failures.append((task.key, exc))
            print(f"[ERROR] {task.key} failed: {exc}")
            continue
        successes.append((task.key, outputs))
        if outputs:
            for path in outputs:
                print(f"[OK] {task.key} -> {path.relative_to(context.outputs_root)}")
        else:
            print(f"[OK] {task.key} -> no files reported")

    print("\n=== Summary ===")
    for key, outputs in successes:
        human = ", ".join(str(path.relative_to(context.outputs_root)) for path in outputs) or "no files"
        print(f"- {key}: {human}")

    if failures:
        print("\nSome graph tasks failed:")
        for key, error in failures:
            print(f"- {key}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
