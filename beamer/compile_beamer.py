"""Pouzdana kompilacija knjige Eksperimentalna mehanika tla.

Puni ciklus automatski obavlja potreban broj LaTeX prolaza:

    pdflatex -> bibtex -> [makeglossaries] -> pdflatex -> ... do stabilizacije

Uporaba:
    python3 compile.py                 # puni ciklus do stabilizacije
    python3 compile.py --quick         # jedan pdflatex prolaz
    python3 compile.py --check         # analiza postojećeg loga i PDF-a
    python3 compile.py --clean         # ukloni pomoćne datoteke
    python3 compile.py --purge         # ukloni pomoćne datoteke i PDF
    python3 compile.py --strict        # upozorenja o citatima/referencama su greška
    python3 compile.py --report build.json

Skripta se može pokrenuti iz bilo koje mape jer sve putanje određuje u odnosu
na vlastitu lokaciju.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Iterable, Sequence

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)


# ---------------------------------------------------------------------------
# Postavke projekta
# ---------------------------------------------------------------------------

TEX_FILE = "prezentacija.tex"
DEFAULT_EXPECTED_PAGES = 160
DEFAULT_MAX_PASSES = 5
MIN_FULL_PASSES = 3

PROJECT_DIR = Path(__file__).resolve().parent
TEX_PATH = PROJECT_DIR / TEX_FILE
JOB_NAME = TEX_PATH.stem
PDF_PATH = TEX_PATH.with_suffix(".pdf")
LOG_PATH = TEX_PATH.with_suffix(".log")

PDFLATEX_COMMAND = [
    "pdflatex",
    "-synctex=1",
    "-interaction=nonstopmode",
    "-file-line-error",
    "-halt-on-error",
    TEX_FILE,
]

AUX_SUFFIXES = [
    ".aux",
    ".bbl",
    ".blg",
    ".bcf",
    ".fdb_latexmk",
    ".fls",
    ".glg",
    ".glo",
    ".gls",
    ".idx",
    ".ilg",
    ".ind",
    ".ist",
    ".lof",
    ".log",
    ".lot",
    ".out",
    ".run.xml",
    ".synctex.gz",
    ".toc",
]

# Datoteke čija promjena određuje treba li još jedan LaTeX prolaz.
STABILITY_SUFFIXES = [".aux", ".bbl", ".gls", ".ind", ".lof", ".lot", ".out", ".toc"]

PAGE_PATTERN = re.compile(
    r"(?<!\S)\[(?:\d+|[ivxlcdm]+)(?=[\s\]<{])",
    re.IGNORECASE,
)
FINISHED_LOG_PATTERN = re.compile(
    r"Output written on .+? \((\d+) pages?",
    re.IGNORECASE,
)

console = Console()


# ---------------------------------------------------------------------------
# Model rezultata i dijagnostika
# ---------------------------------------------------------------------------


@dataclass
class Diagnostics:
    undefined_citations: list[str] = field(default_factory=list)
    undefined_references: list[str] = field(default_factory=list)
    duplicate_labels: list[str] = field(default_factory=list)
    latex_errors: list[str] = field(default_factory=list)
    latex_warnings: int = 0
    bibtex_warnings: int = 0
    overfull_boxes: int = 0
    underfull_boxes: int = 0
    missing_characters: int = 0
    rerun_requested: bool = False

    @property
    def has_blocking_issue(self) -> bool:
        return bool(
            self.undefined_citations
            or self.undefined_references
            or self.duplicate_labels
            or self.latex_errors
        )


@dataclass
class BuildResult:
    success: bool
    mode: str
    passes: int
    stabilized: bool
    pages: int
    pdf_size_mb: float
    elapsed_seconds: float
    timestamp: str
    diagnostics: Diagnostics


def unique_matches(pattern: str, text: str) -> list[str]:
    return sorted(set(re.findall(pattern, text, flags=re.MULTILINE)))


def analyze_log(log_text: str, bibtex_output: str = "") -> Diagnostics:
    """Pretvara LaTeX/BibTeX izlaz u kratak i strojno čitljiv sažetak."""
    return Diagnostics(
        undefined_citations=unique_matches(
            r"Citation [`']([^`']+)[`'].*undefined", log_text
        ),
        undefined_references=unique_matches(
            r"Reference [`']([^`']+)[`'].*undefined", log_text
        ),
        duplicate_labels=unique_matches(
            r"Label [`']([^`']+)[`'] multiply defined", log_text
        ),
        latex_errors=unique_matches(r"^!\s+(.+)$", log_text),
        latex_warnings=len(re.findall(r"(?:LaTeX|Package \S+) Warning:", log_text)),
        bibtex_warnings=len(re.findall(r"^Warning--", bibtex_output, re.MULTILINE)),
        overfull_boxes=len(re.findall(r"Overfull \\[hv]box", log_text)),
        underfull_boxes=len(re.findall(r"Underfull \\[hv]box", log_text)),
        missing_characters=len(re.findall(r"^Missing character:", log_text, re.MULTILINE)),
        rerun_requested=bool(
            re.search(
                r"Rerun to get (?:cross-references|citations)|Label\(s\) may have changed",
                log_text,
                re.IGNORECASE,
            )
        ),
    )


# ---------------------------------------------------------------------------
# Datoteke, alati i procjena napretka
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def estimate_page_count() -> int:
    matches = FINISHED_LOG_PATTERN.findall(read_text(LOG_PATH))
    return int(matches[-1]) if matches else DEFAULT_EXPECTED_PAGES


def actual_page_count() -> int:
    """Čita potvrđeni broj stranica iz završnog LaTeX loga."""
    matches = FINISHED_LOG_PATTERN.findall(read_text(LOG_PATH))
    return int(matches[-1]) if matches else 0


def file_digest(paths: Iterable[Path]) -> str:
    """Sažetak pomoćnih datoteka za otkrivanje stabilizacije dokumenta."""
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode("utf-8"))
        if path.exists():
            digest.update(path.read_bytes())
        else:
            digest.update(b"<missing>")
    return digest.hexdigest()


def stability_digest() -> str:
    return file_digest(TEX_PATH.with_suffix(suffix) for suffix in STABILITY_SUFFIXES)


def require_tools(names: Sequence[str]) -> None:
    missing = [name for name in names if shutil.which(name) is None]
    if missing:
        console.print(
            "[bold red]✗ Nedostaju potrebni programi:[/bold red] "
            + ", ".join(missing)
        )
        raise SystemExit(2)


def bibliography_is_used() -> bool:
    return "\\bibliography{" in read_text(TEX_PATH) or "\\bibdata" in read_text(
        TEX_PATH.with_suffix(".aux")
    )


def glossary_is_used() -> bool:
    return TEX_PATH.with_suffix(".glo").exists()


def clean_aux(remove_pdf: bool = False) -> None:
    removed: list[str] = []
    for suffix in AUX_SUFFIXES:
        path = TEX_PATH.with_suffix(suffix)
        if path.exists():
            path.unlink()
            removed.append(path.name)

    if remove_pdf and PDF_PATH.exists():
        PDF_PATH.unlink()
        removed.append(PDF_PATH.name)

    if removed:
        console.print(f"[green]✓[/green] Uklonjeno datoteka: {len(removed)}")
        console.print(f"  [dim]{', '.join(removed)}[/dim]")
    else:
        console.print("[dim]Nema datoteka za uklanjanje.[/dim]")


# ---------------------------------------------------------------------------
# Pokretanje LaTeX alata
# ---------------------------------------------------------------------------


def extract_error_lines(output: Sequence[str]) -> list[str]:
    candidates = [
        line.rstrip()
        for line in output
        if line.startswith("!")
        or re.match(r"^.+?\.tex:\d+:", line)
        or "Emergency stop" in line
        or "Fatal error" in line
    ]
    return candidates[:25]


def compile_pass(
    progress: Progress,
    task_id: int,
    pass_number: int,
    max_passes: int,
    expected_pages: int,
    verbose: bool,
) -> tuple[bool, str]:
    """Pokreće jedan pdflatex prolaz i prati stvarno obrađene stranice."""
    started_at = PDF_PATH.stat().st_mtime_ns if PDF_PATH.exists() else 0
    try:
        process = subprocess.Popen(
            PDFLATEX_COMMAND,
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except FileNotFoundError:
        console.print("[bold red]✗ Program pdflatex nije pronađen.[/bold red]")
        return False, ""

    output: list[str] = []
    processed_pages = 0
    assert process.stdout is not None

    for line in process.stdout:
        output.append(line)
        if verbose:
            console.print(line.rstrip(), markup=False, highlight=False)

        processed_pages += len(PAGE_PATTERN.findall(line))
        page_progress = min(processed_pages, expected_pages)
        overall = (pass_number - 1) * expected_pages + page_progress
        progress.update(
            task_id,
            completed=overall,
            description=(
                f"[cyan]pdflatex {pass_number}/{max_passes}"
                f" · str. {processed_pages}"
            ),
        )

    return_code = process.wait()
    full_output = "".join(output)
    pdf_updated = PDF_PATH.exists() and PDF_PATH.stat().st_mtime_ns > started_at
    fatal_output = bool(
        re.search(r"Emergency stop|Fatal error|No pages of output", full_output)
    )
    success = return_code == 0 and pdf_updated and not fatal_output

    if not success:
        progress.stop()
        console.print(
            f"\n[bold red]✗ pdflatex prolaz {pass_number} nije uspio[/bold red]"
        )
        errors = extract_error_lines(output)
        console.print("\n".join(errors or [line.rstrip() for line in output[-60:]]))
        return False, full_output

    progress.update(
        task_id,
        completed=pass_number * expected_pages,
        description=(
            f"[green]✓ pdflatex {pass_number}/{max_passes}"
            f" · {processed_pages} str."
        ),
    )
    return True, full_output


def run_tool(
    progress: Progress,
    description: str,
    command: Sequence[str],
    verbose: bool,
) -> tuple[bool, str]:
    task = progress.add_task(description, total=None)
    try:
        process = subprocess.run(
            command,
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        progress.update(task, description=f"[red]✗ {description} nije pronađen")
        progress.stop_task(task)
        return False, ""

    output = process.stdout or ""
    if verbose and output:
        console.print(output, markup=False, highlight=False)

    if process.returncode == 0:
        progress.update(task, description=f"[green]✓ {description}")
    else:
        progress.update(task, description=f"[red]✗ {description}")
    progress.stop_task(task)
    return process.returncode == 0, output


# ---------------------------------------------------------------------------
# Izvještavanje
# ---------------------------------------------------------------------------


def print_items(label: str, items: Sequence[str], warning_color: str) -> None:
    color = "green" if not items else warning_color
    console.print(f"  [{color}]{label}: {len(items)}[/{color}]")
    for item in items[:10]:
        console.print(f"      [dim]{item}[/dim]")
    if len(items) > 10:
        console.print(f"      [dim]… i još {len(items) - 10}[/dim]")


def print_diagnostics(diagnostics: Diagnostics) -> None:
    console.print("\n[bold]Dijagnostika završnog dokumenta[/bold]")
    print_items("nerazriješeni citati", diagnostics.undefined_citations, "red")
    print_items("nerazriješene reference", diagnostics.undefined_references, "red")
    print_items("dvostruko definirani labeli", diagnostics.duplicate_labels, "yellow")
    print_items("LaTeX pogreške", diagnostics.latex_errors, "red")
    console.print(
        "  [dim]upozorenja: "
        f"LaTeX {diagnostics.latex_warnings}, "
        f"BibTeX {diagnostics.bibtex_warnings}, "
        f"overfull {diagnostics.overfull_boxes}, "
        f"underfull {diagnostics.underfull_boxes}, "
        f"nedostajući znakovi {diagnostics.missing_characters}[/dim]"
    )


def write_report(path: Path, result: BuildResult) -> None:
    path = path if path.is_absolute() else PROJECT_DIR / path
    path.write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    console.print(f"[dim]Strojni izvještaj: {path}[/dim]")


def make_result(
    *,
    success: bool,
    mode: str,
    passes: int,
    stabilized: bool,
    elapsed: float,
    diagnostics: Diagnostics,
) -> BuildResult:
    size_mb = PDF_PATH.stat().st_size / (1024 * 1024) if PDF_PATH.exists() else 0.0
    return BuildResult(
        success=success,
        mode=mode,
        passes=passes,
        stabilized=stabilized,
        pages=actual_page_count(),
        pdf_size_mb=round(size_mb, 2),
        elapsed_seconds=round(elapsed, 2),
        timestamp=datetime.now().astimezone().isoformat(timespec="seconds"),
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# Glavni tok
# ---------------------------------------------------------------------------


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Kompilira book_main.tex, obrađuje literaturu i analizira rezultat."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="samo jedan pdflatex prolaz")
    mode.add_argument("--check", action="store_true", help="samo analiziraj postojeći log i PDF")
    mode.add_argument("--clean", action="store_true", help="ukloni pomoćne datoteke")
    mode.add_argument("--purge", action="store_true", help="ukloni pomoćne datoteke i PDF")
    parser.add_argument(
        "--max-passes",
        type=int,
        default=DEFAULT_MAX_PASSES,
        metavar="N",
        help=f"najviše pdflatex prolaza u punom ciklusu (zadano: {DEFAULT_MAX_PASSES})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="vrati neuspjeh ako postoje nerazriješeni citati/reference ili dvostruki labeli",
    )
    parser.add_argument("--verbose", action="store_true", help="prikaži puni izlaz alata")
    parser.add_argument(
        "--report",
        type=Path,
        metavar="DATOTEKA.json",
        help="spremi rezultat i dijagnostiku kao JSON",
    )
    args = parser.parse_args()
    if args.max_passes < MIN_FULL_PASSES:
        parser.error(f"--max-passes mora biti najmanje {MIN_FULL_PASSES}")
    return args


def run_check(args: argparse.Namespace) -> int:
    if not LOG_PATH.exists() or not PDF_PATH.exists():
        console.print("[bold red]✗ Za provjeru su potrebni postojeći .log i PDF.[/bold red]")
        return 1

    diagnostics = analyze_log(read_text(LOG_PATH), read_text(TEX_PATH.with_suffix(".blg")))
    result = make_result(
        success=not (args.strict and diagnostics.has_blocking_issue),
        mode="check",
        passes=0,
        stabilized=True,
        elapsed=0.0,
        diagnostics=diagnostics,
    )
    print_diagnostics(diagnostics)
    console.print(
        f"\n[green]✓[/green] [bold]{PDF_PATH.name}[/bold]"
        f" [dim]· {result.pages} str. · {result.pdf_size_mb:.1f} MB[/dim]"
    )
    if args.report:
        write_report(args.report, result)
    return 0 if result.success else 1


def run_build(args: argparse.Namespace) -> int:
    require_tools(["pdflatex"] + ([] if args.quick else ["bibtex"]))
    expected_pages = estimate_page_count()
    max_passes = 1 if args.quick else args.max_passes
    total_work = expected_pages * max_passes
    mode_name = "brzi prolaz" if args.quick else "puni ciklus do stabilizacije"

    console.print(
        f"\n[bold]Kompilacija[/bold] [cyan]{TEX_FILE}[/cyan]"
        f" [dim]· {mode_name} · procjena {expected_pages} str.[/dim]\n"
    )

    start = time.perf_counter()
    passes = 0
    stabilized = args.quick
    final_output = ""
    bibtex_output = ""

    with Progress(
        SpinnerColumn(spinner_name="dots", style="cyan", finished_text="[green]✓[/green]"),
        TextColumn("{task.description:<40}"),
        BarColumn(bar_width=34, complete_style="green", finished_style="green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=12,
    ) as progress:
        page_task = progress.add_task("[cyan]priprema", total=total_work)

        ok, final_output = compile_pass(
            progress, page_task, 1, max_passes, expected_pages, args.verbose
        )
        passes = 1
        if not ok:
            return 1

        if not args.quick:
            if bibliography_is_used():
                ok, bibtex_output = run_tool(
                    progress, "bibtex", ["bibtex", JOB_NAME], args.verbose
                )
                bbl_path = TEX_PATH.with_suffix(".bbl")
                if not ok or not bbl_path.exists() or bbl_path.stat().st_size == 0:
                    console.print("[bold red]✗ Bibliografija nije uspješno izrađena.[/bold red]")
                    if bibtex_output:
                        console.print("\n".join(bibtex_output.splitlines()[-30:]), markup=False)
                    return 1

            if glossary_is_used():
                require_tools(["makeglossaries"])
                ok, _ = run_tool(
                    progress,
                    "makeglossaries",
                    ["makeglossaries", JOB_NAME],
                    args.verbose,
                )
                if not ok:
                    return 1

            previous_digest = stability_digest()
            for pass_number in range(2, max_passes + 1):
                ok, final_output = compile_pass(
                    progress,
                    page_task,
                    pass_number,
                    max_passes,
                    expected_pages,
                    args.verbose,
                )
                passes = pass_number
                if not ok:
                    return 1

                current_digest = stability_digest()
                current_diagnostics = analyze_log(final_output, bibtex_output)
                stable_files = current_digest == previous_digest
                if (
                    pass_number >= MIN_FULL_PASSES
                    and stable_files
                    and not current_diagnostics.rerun_requested
                ):
                    stabilized = True
                    break
                previous_digest = current_digest

            progress.update(
                page_task,
                completed=total_work,
                description=(
                    "[green]kompilacija stabilna"
                    if stabilized
                    else "[yellow]dosegnut maksimalan broj prolaza"
                ),
            )

    elapsed = time.perf_counter() - start
    diagnostics = analyze_log(final_output or read_text(LOG_PATH), bibtex_output)
    strict_failure = args.strict and diagnostics.has_blocking_issue
    success = PDF_PATH.exists() and not strict_failure
    result = make_result(
        success=success,
        mode="quick" if args.quick else "full",
        passes=passes,
        stabilized=stabilized,
        elapsed=elapsed,
        diagnostics=diagnostics,
    )

    print_diagnostics(diagnostics)
    status = "[green]✓[/green]" if success else "[red]✗[/red]"
    stability_note = "stabilno" if stabilized else "provjeriti upozorenja"
    console.print(
        f"\n{status} [bold]{PDF_PATH.name}[/bold]"
        f" [dim]· {result.pages} str. · {result.pdf_size_mb:.1f} MB"
        f" · {passes} prolaza · {stability_note} · {elapsed:.1f} s[/dim]\n"
    )
    if args.report:
        write_report(args.report, result)
    return 0 if success else 1


def main() -> int:
    args = parse_arguments()

    if not TEX_PATH.exists():
        console.print(f"[bold red]✗ Datoteka ne postoji:[/bold red] {TEX_PATH}")
        return 1

    if args.clean:
        clean_aux(remove_pdf=False)
        return 0
    if args.purge:
        clean_aux(remove_pdf=True)
        return 0
    if args.check:
        return run_check(args)
    return run_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
