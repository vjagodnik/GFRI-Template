#!/usr/bin/env python3
r"""Automatska priprema PDF-a za Turnitin prema GFRI uputama.

Tok rada:
    1. potpuno kompajlira dokument.tex pomoću postojećeg compile.py
    2. iz aktualnog dokument.tex generira turnitin.tex
    3. uklanja prikaz slika, tablica i popisa literature, ali zadržava numeraciju
    4. izostavlja uvodni dio rada prije \pagenumbering{arabic}
    5. kompajlira turnitin.tex -> turnitin.pdf

Pokretanje:
    python3 turnitin.py

Skripta, compile.py i dokument.tex trebaju biti u istoj mapi projekta.
turnitin.tex je generirana datoteka i pri svakom pokretanju se prepisuje.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys


# ---------------------------------------------------------------------------
# Postavke
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENT_TEX = PROJECT_DIR / "dokument.tex"
COMPILE_PY = PROJECT_DIR / "compile.py"
TURNITIN_TEX = PROJECT_DIR / "turnitin.tex"
TURNITIN_PDF = PROJECT_DIR / "turnitin.pdf"

MAX_TURNITIN_PASSES = 5

PDFLATEX = [
    "pdflatex",
    "-interaction=nonstopmode",
    "-file-line-error",
    "-halt-on-error",
]

# Blok je preuzet iz TurnitIn.md. Slike i tablice se ne prikazuju,
# ali \caption i dalje povećava brojač; dokument.aux se učitava radi labela.
TURNITIN_PREAMBLE_BLOCK = r"""

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%%          labels and captions
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepackage{environ}

\makeatletter
\newcommand{\DiscardFloat}[1]{%
    \RenewEnviron{#1}{%
        \begingroup
        \renewcommand{\caption}[2][]{\refstepcounter{#1}}%
        \setbox0=\vbox{\BODY}%
        \endgroup
    }%
}
\DiscardFloat{figure}
\DiscardFloat{table}
\makeatother

% --- reuse labels from dokument.aux ---
\makeatletter
\InputIfFileExists{dokument.aux}{}{}
\makeatother

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%%          bibliography
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\makeatletter
% Save the original commands
\let\original@thebibliography\thebibliography
\let\original@endthebibliography\endthebibliography

% Redefine the bibliography environment to be completely empty
\renewenvironment{thebibliography}[1]
{\original@thebibliography{#1}% Start the environment
    \setbox0\vbox\bgroup% Begin capturing content (but discard it)
}
{\egroup% End capturing
    \original@endthebibliography% Properly end the environment
}
\makeatother
"""

BIBLIOGRAPHY_HIDE_BLOCK = r"""
% Remove bibliography title and TOC entry
\renewcommand{\bibname}{}   % no "Literatura"
\renewcommand{\refname}{}   % covers other classes
"""


# ---------------------------------------------------------------------------
# Pomoćne funkcije
# ---------------------------------------------------------------------------


def fail(message: str, code: int = 1) -> "NoReturn":
    print(f"\n✗ {message}")
    raise SystemExit(code)


def require_file(path: Path) -> None:
    if not path.exists():
        fail(f"Nedostaje datoteka: {path.name}")


def require_program(name: str) -> None:
    if shutil.which(name) is None:
        fail(f"Program '{name}' nije pronađen u PATH-u.")


def run(command: list[str], description: str, *, stream: bool = False) -> str:
    """Pokreće naredbu i na grešci prikazuje koristan završetak izlaza."""
    print(f"→ {description}")

    if stream:
        process = subprocess.run(command, cwd=PROJECT_DIR)
        if process.returncode != 0:
            fail(f"Neuspjeh: {description}", process.returncode or 1)
        print(f"  ✓ {description}")
        return ""

    process = subprocess.run(
        command,
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = process.stdout or ""

    if process.returncode != 0:
        print("\n".join(output.splitlines()[-60:]))
        fail(f"Neuspjeh: {description}", process.returncode or 1)

    print(f"  ✓ {description}")
    return output


def is_active_line(line: str) -> bool:
    """True ako LaTeX linija nije komentirana znakom %."""
    return not line.lstrip().startswith("%")


def comment_lines(text: str) -> str:
    """Komentira svaku aktivnu liniju, uz očuvanje postojećih komentara."""
    result: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("%"):
            result.append(line)
        elif line.endswith("\n"):
            result.append("%" + line[:-1] + "\n")
        else:
            result.append("%" + line)
    return "".join(result)


def comment_matching_lines(text: str) -> str:
    """Komentira originalni naslov i TOC zapis bibliografije."""
    result: list[str] = []

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        active = is_active_line(line)

        is_bibname = bool(re.match(r"\\renewcommand\s*\{\\bibname\}", stripped))
        is_refname = bool(re.match(r"\\renewcommand\s*\{\\refname\}", stripped))
        is_literature_toc = (
            stripped.startswith(r"\addcontentsline")
            and ("Literatura" in stripped or r"\bibname" in stripped)
        )

        if active and (is_bibname or is_refname or is_literature_toc):
            result.append("%" + line)
        else:
            result.append(line)

    return "".join(result)


def digest(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in paths:
        h.update(path.name.encode("utf-8"))
        if path.exists():
            h.update(path.read_bytes())
        else:
            h.update(b"<missing>")
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Generiranje turnitin.tex
# ---------------------------------------------------------------------------


def generate_turnitin_tex() -> None:
    source = DOCUMENT_TEX.read_text(encoding="utf-8", errors="replace")

    begin_match = re.search(
        r"(?m)^[ \t]*\\begin\{document\}[ \t]*(?:%.*)?$",
        source,
    )
    if not begin_match:
        fail(r"U dokument.tex nije pronađen aktivni \begin{document}.")

    arabic_match = re.search(
        r"(?m)^[ \t]*\\pagenumbering\s*\{\s*arabic\s*\}.*$",
        source[begin_match.end() :],
    )
    if not arabic_match:
        fail(
            r"U dokument.tex nije pronađen aktivni \pagenumbering{arabic}. "
            "Prema TurnitIn.md to je početak sadržaja koji se zadržava."
        )

    # Apsolutna pozicija početka arapskog numeriranja u izvornom dokumentu.
    arabic_start = begin_match.end() + arabic_match.start()

    preamble = source[: begin_match.start()]
    begin_document = source[begin_match.start() : begin_match.end()]
    front_matter = source[begin_match.end() : arabic_start]
    main_and_back_matter = source[arabic_start:]

    # Regex za \begin{document} završava prije prijelaza u novi red.
    # Taj prvi prijelaz ostavljamo izvan komentara kako rezultat ne bi bio
    # "\begin{document}%" nego čitljiv "\begin{document}\n%...".
    if front_matter.startswith("\r\n"):
        front_matter = front_matter[2:]
    elif front_matter.startswith("\n"):
        front_matter = front_matter[1:]

    # Prema uputama izostavlja se sve prije arapskog numeriranja stranica.
    front_matter = comment_lines(front_matter)

    # Originalne definicije naslova bibliografije/TOC zapisa komentiramo.
    main_and_back_matter = comment_matching_lines(main_and_back_matter)

    # Nova prazna imena bibliografije ubacuju se neposredno prije bibliografije.
    bibliography_match = re.search(
        r"(?m)^[ \t]*\\bibliographystyle\s*\{|^[ \t]*\\bibliography\s*\{",
        main_and_back_matter,
    )
    if not bibliography_match:
        fail(
            r"U dokument.tex nije pronađen \bibliographystyle{...} ni "
            r"\bibliography{...}."
        )

    main_and_back_matter = (
        main_and_back_matter[: bibliography_match.start()]
        + BIBLIOGRAPHY_HIDE_BLOCK
        + "\n"
        + main_and_back_matter[bibliography_match.start() :]
    )

    generated = (
        preamble.rstrip()
        + TURNITIN_PREAMBLE_BLOCK
        + "\n\n"
        + begin_document
        + "\n"
        + front_matter
        + main_and_back_matter
    )

    TURNITIN_TEX.write_text(generated, encoding="utf-8")
    print(f"  ✓ Generiran {TURNITIN_TEX.name} iz {DOCUMENT_TEX.name}")


# ---------------------------------------------------------------------------
# Kompiliranje
# ---------------------------------------------------------------------------


def compile_document() -> None:
    """Prvo potpuno kompajlira dokument.tex postojećim compile.py."""
    run(
        [sys.executable, str(COMPILE_PY)],
        "kompilacija dokument.tex preko compile.py",
        stream=True,
    )

    aux = PROJECT_DIR / "dokument.aux"
    if not aux.exists() or aux.stat().st_size == 0:
        fail("compile.py je završio, ali dokument.aux nije izrađen.")


def compile_turnitin() -> None:
    """Kompajlira turnitin.tex do stabilizacije referenci/citata."""
    job = TURNITIN_TEX.stem
    aux = PROJECT_DIR / f"{job}.aux"
    bbl = PROJECT_DIR / f"{job}.bbl"
    log = PROJECT_DIR / f"{job}.log"
    out = PROJECT_DIR / f"{job}.out"

    run(PDFLATEX + [TURNITIN_TEX.name], "turnitin.tex — prvi pdflatex prolaz")

    if not aux.exists() or aux.stat().st_size == 0:
        fail("Nije izrađen turnitin.aux.")

    run(["bibtex", job], "BibTeX za turnitin")
    if not bbl.exists() or bbl.stat().st_size == 0:
        fail("BibTeX nije izradio valjani turnitin.bbl.")

    watched = [aux, bbl, out]
    previous = digest(watched)
    stabilized = False

    # Nakon BibTeX-a trebaju najmanje dva pdflatex prolaza.
    for pass_number in range(2, MAX_TURNITIN_PASSES + 1):
        output = run(
            PDFLATEX + [TURNITIN_TEX.name],
            f"turnitin.tex — pdflatex prolaz {pass_number}",
        )
        current = digest(watched)
        rerun_requested = bool(
            re.search(
                r"Rerun to get (?:cross-references|citations)|"
                r"Label\(s\) may have changed|There were undefined references",
                output,
                re.IGNORECASE,
            )
        )

        if pass_number >= 3 and current == previous and not rerun_requested:
            stabilized = True
            break
        previous = current

    if not TURNITIN_PDF.exists() or TURNITIN_PDF.stat().st_size == 0:
        fail("Kompilacija je završila bez valjanog turnitin.pdf.")

    # Provjera ključnih problema u završnom logu.
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    undefined_citations = re.findall(
        r"Citation [`']([^`']+)[`'].*undefined", log_text, flags=re.IGNORECASE
    )
    undefined_references = re.findall(
        r"Reference [`']([^`']+)[`'].*undefined", log_text, flags=re.IGNORECASE
    )

    size_mb = TURNITIN_PDF.stat().st_size / (1024 * 1024)
    print("\n────────────────────────────────────────")
    print(f"✓ Gotovo: {TURNITIN_PDF.name} ({size_mb:.1f} MB)")
    print(f"  turnitin.tex: automatski generiran iz {DOCUMENT_TEX.name}")
    print(f"  stabilizacija: {'da' if stabilized else 'dosegnut maksimalan broj prolaza'}")

    if undefined_citations:
        print(f"  ⚠ nerazriješeni citati: {len(set(undefined_citations))}")
    if undefined_references:
        print(f"  ⚠ nerazriješene reference: {len(set(undefined_references))}")
    if not undefined_citations and not undefined_references:
        print("  ✓ citati i reference bez nerazriješenih oznaka")


# ---------------------------------------------------------------------------
# Glavni program
# ---------------------------------------------------------------------------


def main() -> int:
    print("\nPriprema dokumenta za Turnitin")
    print("────────────────────────────────────────")

    require_file(DOCUMENT_TEX)
    require_file(COMPILE_PY)
    require_program("pdflatex")
    require_program("bibtex")

    # TurnitIn.md izričito traži kompilaciju dokumenta prije izrade turnitin.tex.
    compile_document()

    print("→ generiranje turnitin.tex")
    generate_turnitin_tex()

    compile_turnitin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
