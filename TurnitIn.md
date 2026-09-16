# Upute za pripremu završnog/diplomskog rada za Turnitin

U nastavku su dane upute za pripremu završnog/diplomskog rada za provjeru pomoću sustava Turnitin.

Radi što učinkovitije provjere potrebno je iz dokumenta ukloniti:

- slike i opise slika,
- tablice i opise tablica,
- popis literature.

Pritom je potrebno **zadržati numeraciju slika, tablica i bibliografskih navoda u tekstu** kako bi struktura i upućivanja u radu ostali ispravni.

Priprema dokumenta za Turnitin može se napraviti na **dva načina**:

1. **ručno**, kopiranjem datoteke `dokument.tex` u `turnitin.tex` i izmjenom prema uputama u nastavku;
2. **automatski**, korištenjem Python skripte `turnitin.py`.

Obje metode daju istu vrstu izlaznog dokumenta. Ručna metoda ne zahtijeva Python i prikladna je za korisnike koji rade isključivo u LaTeX okruženju.

> **NAPOMENA:** Prije izrade Turnitin verzije potrebno je barem jednom potpuno kompajlirati `dokument.tex`, uključujući BibTeX i sve potrebne LaTeX prolaze. Time se stvaraju datoteke, posebno `dokument.aux`, koje se koriste za očuvanje numeracije i referenci.

---

# 1. Ručna priprema dokumenta

## 1.1. Kopiranje `dokument.tex` u `turnitin.tex`

U mapi projekta, gdje se nalazi i datoteka `dokument.tex`, potrebno je kreirati novu datoteku:

```text
turnitin.tex
```

U nju se kopira **cijeli sadržaj** datoteke:

```text
dokument.tex
```

Sve daljnje izmjene rade se isključivo u `turnitin.tex`.

> **NAPOMENA:** Preporučuje se jednom kompajlirati i `turnitin.tex` kako bi se kreirale pomoćne datoteke kao što su `turnitin.aux` i `turnitin.bbl`.

---

## 1.2. Uklanjanje slika i tablica uz zadržavanje numeracije

Neposredno prije linije:

```tex
\begin{document}
```

potrebno je dodati sljedeći kôd:

```tex
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
```

Ovaj dio kôda uklanja prikaz slika i tablica, ali zadržava njihove brojeve i reference u tekstu.

---

## 1.3. Uklanjanje popisa literature uz zadržavanje bibliografskih navoda

Ispod prethodnog bloka, također prije:

```tex
\begin{document}
```

dodaje se:

```tex
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
{\original@thebibliography{#1}%
    \setbox0\vbox\bgroup%
}
{\egroup%
    \original@endthebibliography%
}

\makeatother
```

Time se bibliografija i dalje tehnički obrađuje, pa bibliografski navodi u tekstu ostaju ispravno numerirani, ali se sam popis literature ne prikazuje.

---

## 1.4. Uklanjanje uvodnih dijelova rada

U `turnitin.tex` potrebno je komentirati sve dijelove koji prethode glavnom tekstu rada.

To obično uključuje:

```tex
%\input{./naslovnica.tex}
%\input{./izjava.tex}
%\input{./izjava_projekt.tex}
%\pagestyle{empty}
%\input{./Poglavlja/zahvale}

%\cleardoublepage

%\pagenumbering{roman}
%\setcounter{page}{1}

%\input{./Poglavlja/sazetak}

%\cleardoublepage
%\setcounter{page}{1}

%\tableofcontents
%\cleardoublepage

%\listoffigures
%\addcontentsline{toc}{chapter}{\listfigurename}

%\cleardoublepage
%\listoftables
%\addcontentsline{toc}{chapter}{\listtablename}

%\clearpage
```

Potrebno je zadržati dio od:

```tex
\pagenumbering{arabic}
\pagestyle{plain}
\setcounter{page}{1}
```

nadalje, odnosno glavni tekst rada, primjerice:

```tex
\input{./Poglavlja/poglavlje1.tex}
```

Dakle, u Turnitin verziji dokumenta ostaje samo stvarni sadržaj rada koji se želi provjeravati.

---

## 1.5. Uklanjanje naslova popisa literature

Na kraju dokumenta potrebno je ukloniti naslov *Literatura* i njegov unos u sadržaj.

Ako originalni `dokument.tex` sadrži:

```tex
\renewcommand{\bibname}{\uppercase{Literatura}}
\addcontentsline{toc}{chapter}{\textbf{Literatura}}
```

te se linije u `turnitin.tex` komentiraju:

```tex
%\renewcommand{\bibname}{\uppercase{Literatura}}
%\addcontentsline{toc}{chapter}{\textbf{Literatura}}
```

Ispred bibliografije dodaju se:

```tex
\renewcommand{\bibname}{}
\renewcommand{\refname}{}
```

Krajnji dio dokumenta treba izgledati približno ovako:

```tex
\cleardoublepage\phantomsection

% Remove bibliography title and TOC entry
\renewcommand{\bibname}{}
\renewcommand{\refname}{}

%\renewcommand{\bibname}{\uppercase{Literatura}}
%\addcontentsline{toc}{chapter}{\textbf{Literatura}}

\bibliographystyle{unsrtnat-GFRI}
\bibliography{bibliography}

\end{document}
```

---

## 1.6. Kompiliranje Turnitin dokumenta

Nakon svih izmjena potrebno je potpuno kompajlirati:

```text
turnitin.tex
```

odnosno napraviti potreban slijed LaTeX/BibTeX prolaza dok se citati i reference ne stabiliziraju.

Rezultat je:

```text
turnitin.pdf
```

koji se može koristiti za provjeru u sustavu Turnitin.

---

# 2. Automatska priprema pomoću Python skripte

Ako je na računalu instaliran Python, cijeli prethodno opisani postupak može se automatizirati pomoću skripte:

```text
turnitin.py
```

Skripta se postavlja u istu mapu u kojoj se nalaze:

```text
dokument.tex
compile.py
turnitin.py
bibliography.bib
struktura.tex
Poglavlja/
...
```

Pokreće se naredbom:

```bash
python3 turnitin.py
```

Skripta automatski:

1. kompajlira `dokument.tex` pomoću postojećeg `compile.py`;
2. iz aktualnog `dokument.tex` izrađuje novi `turnitin.tex`;
3. dodaje kôd za uklanjanje slika i tablica uz zadržavanje njihove numeracije;
4. učitava `dokument.aux` kako bi se sačuvale reference;
5. uklanja uvodne dijelove dokumenta prije početka arapskog numeriranja;
6. uklanja prikaz popisa literature, ali zadržava bibliografske navode i njihovu numeraciju;
7. kompajlira `turnitin.tex`;
8. izrađuje završni:

```text
turnitin.pdf
```

> **VAŽNO:** Kada se koristi Python metoda, `turnitin.tex` je automatski generirana datoteka. Ne treba je ručno uređivati jer će se pri sljedećem pokretanju skripte ponovno izraditi iz aktualnog `dokument.tex`.

---

# 3. Koju metodu koristiti?

Ako korisnik nema Python ili ne želi koristiti dodatne skripte, koristi se:

```text
1. Ručna priprema dokumenta
```

Ako je Python instaliran i u projektu se nalazi `turnitin.py`, preporučuje se:

```text
2. Automatska priprema pomoću Python skripte
```

Automatska metoda posebno je praktična tijekom izrade rada jer se `turnitin.tex` i `turnitin.pdf` mogu ponovno generirati nakon svake veće izmjene `dokument.tex`, bez ponavljanja ručnih koraka.

U oba slučaja krajnji cilj je isti: dobiti Turnitin verziju rada koja sadrži glavni tekst, ali ne prikazuje slike, tablice i popis literature, uz očuvanu numeraciju i reference.
