# Upute za pripremu završnog/diplomskog rada za Turnitin

U nastavku teksta su dane upute za pripremu završnog/diplomskog rada za Turnitin. Radi što efikasnije provjere pomoću TurnitIn alata, potrebno je odstraniti sve slike i opise slika, tablice i opise tablica te popis literature.
Usprkos tomu, potrebno je zadržati numeraciju slika, tablica i popisa literature kako bi se omogućila provjera dokumenta.

Priprema dokumenta za Turnitin se vrši u nekoliko koraka:
- kopiranje dokumenta "dokument.tex" u novi dokument "turnitin.tex"
- izmjene u dokumentu "turnitin.tex"
- dodavanje linija kôda u dokument "turnitin.tex"

> NAPOMENA: Prije bilo kakvih izmjena u dokumentu "turnitin.tex" potrebno je napraviti kompiliranje teksta, kao što se radi sa "dokument.tex".

## Kopiranje dokumenta "dokument.tex" u novi dokument "turnitin.tex"

Kopiranje dokumenta "dokument.tex" u novi dokument "turnitin.tex" se vrši na način da se u mapi projekta (gdje se nalazi i datoteka "dokument.tex") kreira nova datoteka pod nazivom "turnitin.tex" te se u nju kopira sav kôd iz datoteke "dokument.tex". U novom dokumentu "turnitin.tex" se vrše sve daljnje izmjene. 

> NAPOMENA: Kompiliranje dokumenta "turnitin.tex" kako bi se kreirale datoteke "turnitin.aux" i "turnitin.bbl".

## Izmjene u dokumentu "turnitin.tex" i dodavanje linija kôda

U liniju kôda prije linije koja započinje s "\begin{document}" se dodaje sljedeći kôd:  

```tex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%%			labels and captions
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\usepackage{environ}

%
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

% --- reuse labels from A.aux ---
\makeatletter
\InputIfFileExists{dokument.aux}{}{}
\makeatother


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%%			bibliography
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
```
Primjer dodanog kôda je dan ispod:

```tex
\documentclass[12pt,onesided]{book}

\input{./struktura.tex}

\onehalfspacing

%%%%%%%%%%%%%%%%%%%% Document code starts here %%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%% Enter the data %%%%%%%%%%%%%%%%%%%%

\newcommand{\autor} {Fredrik Lamb}
\newcommand{\studij} {Preddiplomski sveučilišni}
\newcommand{\smjer} {Pozitivan}
\newcommand{\kolegij} {Filozofija građevinarstva}
\newcommand{\naslov}{Tko pije, a tko plaća na neaktivnom gradilištu?}
\newcommand{\JMBAG} {000111222}
\newcommand{\vrsta}{Završni rad } % ili Diplomski
%----------------------------------------------------------------------------------------
%	PODATCI O PROJEKTU
\newcommand{\projekt}{Naziv projekta}
\newcommand{\voditeljProjekta}{Djuro Matheu}
\newcommand{\sifraProjeka}{123123}
\newcommand{\moneyProjekta}{Sveučilište u Rijeci}
\newcommand{\nadleznostProjeka}{Republika Hrvatska}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%%			labels and captions
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\usepackage{environ}

%
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

% --- reuse labels from A.aux ---
\makeatletter
\InputIfFileExists{dokument.aux}{}{}
\makeatother


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%%			bibliography
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






\begin{document}
... nastavak kôda ...
```
Prvi dio kôda odnosi se na uklanjanje slika i tablica iz dokumenta, a drugi dio kôda odnosi se na uklanjanje popisa literature iz dokumenta.

U dokumentu "turnitin.tex" komentiraju se sve linije kôda koje se odnose na pozive naslovnice, izjave, popisa slika i tablica. Primjer komentiranja linija kôda je dan ispod:

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
Preostale izmjene u dokumentu "turnitin.tex" se odnose na uklanjanje popisa literature uz zadržavanje numeracije u tekstualnom dijelu rada. To se postiže jednostavnim načinom da kreira nova naredba za ime bibliografije i imena reference. Primjer izmjene je dan ispod:

```tex
\renewcommand{\bibname}{} 
\renewcommand{\refname}{}
```

Pritom je nužno komentirati liniju kôda koja definira naslov popisa literature. Primjer komentirane linije kôda je dan ispod:
```tex
%\renewcommand{\bibname}{\uppercase{Literatura}}
%\addcontentsline{toc}{chapter}{\textbf{Literatura}}
```


Krajnji dio kôda u dokumentu "turnitin.tex" treba izgledati na sljedeći način:

```tex
\cleardoublepage\phantomsection

% Remove bibliography title and TOC entry
\renewcommand{\bibname}{}   % no "Literatura"
\renewcommand{\refname}{}   % covers other classes
%\renewcommand{\bibname}{\uppercase{Literatura}}
%\addcontentsline{toc}{chapter}{\textbf{Literatura}}
\bibliographystyle{unsrtnat-GFRI}
\bibliography{bibliography}
\end{document}
```