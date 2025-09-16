# Upute za pripremu završnog/diplomskog rada za Turnitin

U nastavku teksta su dane upute za pripremu završnog/diplomskog rada za Turnitin. Radi što efikasnije provjere pomoću TurnitIn alata, potrebno je odstraniti sve slike i opise slika, tablice i opise tablica te popis literature.
Usprkos tomu, potrebno je zadržati numeraciju slika, tablica i popisa literature kako bi se omogućila provjera dokumenta.

Priprema dokumenta za Turnitin se vrši u nekoliko koraka:
- kopiranje dokumenta "dokument.tex" u novi dokument "turnitin.tex"
- izmjene u dokumentu "turnitin.tex"
- dodavanje linija kôda u dokument "turnitin.tex"

## Kopiranje dokumenta "dokument.tex" u novi dokument "turnitin.tex"

Kopiranje dokumenta "dokument.tex" u novi dokument "turnitin.tex" se vrši na način da se u mapi projekta (gdje se nalazi i datoteka "dokument.tex") kreira nova datoteka pod nazivom "turnitin.tex" te se u nju kopira sav kôd iz datoteke "dokument.tex". U novom dokumentu "turnitin.tex" se vrše sve daljnje izmjene. 


## Izmjene u dokumentu "turnitin.tex" i dodavanje linija kôda

U liniju kôda prije linije koja započinje s "\begin{document}" se dodaje sljedeći kôd:  

```tex
\usepackage{environ}
%
\RenewEnviron{figure}{}
\RenewEnviron{table}{}
%
\long\def\caption#1[#2]#3{}
\long\def\caption#1{}  
%
\renewcommand{\label}[1]{}
```
Primjer dodanog kôda je dan ispod:

```tex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage{environ}

% Remove figures and tables completely
\RenewEnviron{figure}{}  % everything inside figure is ignored
\RenewEnviron{table}{}   % everything inside table is ignored

% Remove captions (works for optional argument too)
\long\def\caption#1[#2]#3{}
\long\def\caption#1{}  

% Remove labels
\renewcommand{\label}[1]{}

\begin{document}
```

Komentiraju se sve linije kôda koje se odnose na pozive naslovnice, izjave, popisa slika i tablica. Primjer komentiranja linija kôda je dan ispod:

```tex
%\input{./naslovnica.tex}
%\input{./izjava.tex}
%\input{./izjava_projekt.tex}
%\pagestyle{empty}
%\input{./Poglavlja/zahvale}
%
%\cleardoublepage
%
%\pagenumbering{roman}
%\setcounter{page}{1}
%
%\input{./Poglavlja/sazetak}
%
%\cleardoublepage
%\setcounter{page}{1}
%
%\tableofcontents
%\cleardoublepage
%
%\listoffigures
%\addcontentsline{toc}{chapter}{\listfigurename}
%
%\cleardoublepage
%\listoftables
%\addcontentsline{toc}{chapter}{\listtablename}
%
%\clearpage

\pagenumbering{arabic}
\pagestyle{plain}
\setcounter{page}{1}

\input{./Poglavlja/poglavlje1.tex}
```
Dakle, zadržavaju se linije koda koje se odnose na sadržaj samog rada počevši od line za definiranje arapskog numeriranja stranica.
Preostale izmjene u dokumentu "turnitin.tex" se odnose na uklanjanje popisa literature uz zadržavanje numeracije u tekstualnom dijelu rada. To se postiže jednostavnim načinom da se poziva "*.bst" datoteka koja sadrži prazan stil citiranja. Stil citiranja koji se koristi u osnovnom dokumentu "dokument.tex" je "unsrtat-GFRI" a on se zamjeni sa stilom "empty". Primjer izmjene je dan ispod:

```tex
\bibliographystyle{empty}
```

Krajnji dio kôda u dokumentu "turnitin.tex" treba izgledati na sljedeći način:

```tex
\cleardoublepage\phantomsection
%
%\printbibliography
\vspace{\baselineskip}
%\label{Bibliography}
\renewcommand{\bibname}{\uppercase{Literatura}}
\addcontentsline{toc}{chapter}{\textbf{Literatura}}
\bibliographystyle{empty}
\bibliography{bibliography}
\end{document}
```