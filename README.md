---
title : GFRI-Template - Predložak za izradu završnih i diplomskih radova Građevinskog fakulteta Sveučilišta u Rijeci
author: Vedran Jagodnik
---

# Uvod

Repozitorij služi za pripremu završnih i diplomskih radova. U nastavku dokumenta ukratko je opisan sadržaj repozitorija i dokumenata, koje podatke je potrebno unesti te na što je potrebno obratiti pažnjnu prilikom uređivanja dokumenta.
Dokument je pripremljen za jednostrano printanje. Ukoliko se ukaže zahtjev za obostranim printanjem, potrebno je izmjeniti dio kôda u dokumentu "struktura.tex", o čemu će biti spomena kasnije u tekstu.

# Sadržaj repozitorija

Repozitorij se sastoji od tri mape i 6 datoteka. 

Mape su nazvane redom:

- Poglavlja
- Slike
- dataset

U mapi pod naslovom "Poglavlja" postavljaju se ".tex" dokumenti sa tekstom vezanim za odogovarjuća poglavlja.
U mapi pod naslovom "Slike" postavljaju se grafički dokumenti (.jpg, .tiff, .png, .pdf i slično).
U mapi pod naslovom "dataset" postavljaju se podatci za grafičku obradu i izradu dijagrama, ukoliko nisu pripremljeni kao slike.

Šest ključnih datoteka su redom:
- biblioography.bib - datoteka koja sadrži bibtex kôd za popis literature,
- izjava.tex - izjava studenta o samostalnoj izradi završnog rada,
- naslovnica.tex - dokument koji kreira naslovnicu završnog/diplomskog rada,
- strutura.tex - dokument koji sadrži većinu potrebnih paketa za uspješno generiranje dokumenta,
- dokument.tex - osnovni dokument za kompiliranje završnog/diplomskog rada.

# Redoslijed 

Student nužno izmjenjuje samo slijedeće dokumente:
- izjava.tex
- dokument.tex

Ukoliko je odlučeno da se završni rad printa kao obostran, potrebno je izmjeniti i "struktura.tex".

## Imjene u dokumentu "izjava.tex"

Student u dokumentu "izjava.tex" odabire odgovarajući rod kandidata i mentora 

```tex
\vrsta izradio/izradila sam samostalno, u suradnji s mentorom/mentoricom i uz poštivanje pozitivnih građevinskih propisa i znanstvenih dostignuća iz područja građevinarstva. Građevinski fakultet u Rijeci je nositelj prava intelektualnog vlasništva u odnosu na ovaj rad.

```

## Imjene u dokumentu "dokument.tex"

Kandidat u dokumentu "dokument.tex" imjenjuje linije kôda 11 - 17 te upisuje odgovarajuće podatke kako je navedeno ispod.

```tex
\newcommand{\autor} {Fredrik Lamb}
\newcommand{\studij} {Preddiplomski sveučilišni}
\newcommand{\smjer} {Pozitivan}
\newcommand{\kolegij} {Filozofija građevinarstva}
\newcommand{\naslov}{Tko pije, a tko plaća na neaktivnom gradilištu?}
\newcommand{\JMBAG} {000111222}
\newcommand{\vrsta}{Završni rad} % ili Diplomski
```

Kandidat po potrebi dodaje nove linije nakon linije 59, na način:

```tex
\cleardoublepage
\input{./Poglavlja/poglavljeNN.tex}
```

Potrebno je imati kreiran dokument "poglavljeNN.tex" mora postojati u mapi "Poglavlja".

## Imjene u dokumentu "struktura.tex"

Ukoliko je odlučeno da se završni rad printa kao obostran izmjenjnuje se linija 153 odnosno 154. 
Aktivna linija 153 omogućava pozicioniranje broja stranice lijevo i desno radi obostranog printanja.
Aktivna linija 154 omogućava pozicioniranje broja stranice desno za jednostrano printanje.

```tex
\pagestyle{fancy} % Turn on the style
\fancypagestyle{plain}{%
	\renewcommand{\headrulewidth}{0pt}%
	\fancyhf{}%
	% \fancyfoot[LE,RO]{\thepage}%   ako je twosided
    \fancyfoot[R]{\thepage}%   ako je onesided
}
```

### Izmjene u dokumentu "struktura.tex" - TrackChange

U sklopu predloška moguće je koristiti tzv. "track changes". Opcija je omogućena pozivom na paket "trackchanges.sty". Dodatne upute možete pronaći na poveznici ![trackchanges]{https://trackchanges.sourceforge.net}.

Izmjene se vrše u linijama 180, 181 i 182 dokumenta "struktura.tex" na način da se omogući korištenje **trackchanges** opcije (linija 180) te da se unesu "editori" ili kao inicijali ili kao puna imena (svakako bez razmaka). 

```tex
\addeditor{VJ}
\addeditor{VF}
```








