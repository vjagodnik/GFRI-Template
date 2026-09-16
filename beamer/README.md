# GFRI Beamer predložak

Predložak je namijenjen prezentacijama Građevinskog fakulteta u Rijeci. GF logo
`logo/gflogo.pdf` obvezan je i prikazuje se na naslovnom slajdu, sekcijskim
slajdovima i u podnožju ostalih slajdova. Tema koristi crnu, bijelu i sivu boju.
Tanka traka uz donji rub svakog slajda prikazuje napredak kroz prezentaciju.

Naslov, autor, studij, kolegij i podatci o projektu preuzimaju se iz zajedničke
datoteke `../GFRI-Template/podaci.tex`. Iste podatke koristi i pisani rad, pa ih
je potrebno unositi samo na jednom mjestu. Slajd s pripadnošću projektu nalazi
se neposredno prije završnog slajda.

Pripadnost projektu uključuje se ili isključuje u zajedničkoj datoteci
`../GFRI-Template/podaci.tex`:

```tex
\GFRIprojekttrue   % prikaži projektnu izjavu, projektni slajd i logo
\GFRIprojektfalse  % sakrij projektnu izjavu i projektni slajd
```

Logotipi se spremaju u mapu `logo`, a fotografije, dijagrami i ostale slike u
mapu `slike`. Predložak već pretražuje obje mape pri umetanju grafike.

## Dodatni logotipi

Na početku datoteke `prezentacija.tex` postavite datoteke za najviše dva dodatna
logotipa:

```tex
\GFRIsetpartnerlogoA{logo/logo-partnera-a.pdf}
\GFRIsetpartnerlogoB{logo/logo-partnera-b.png}
```

Svaki se logotip uključuje ili isključuje zasebno:

```tex
\GFRIpartnerAtrue   % prikaz prvog dodatnog logotipa
\GFRIpartnerAfalse  % skrivanje prvog dodatnog logotipa

\GFRIpartnerBtrue   % prikaz drugog dodatnog logotipa
\GFRIpartnerBfalse  % skrivanje drugog dodatnog logotipa
```

Datoteka `logo/logoipsum-434.png` služi samo kao privremeni primjer. Zamijenite
je stvarnim partnerskim logotipima prije izrade završne prezentacije.
Kada je `\GFRIprojekttrue`, svi uključeni partnerski logotipi prikazuju se i na
slajdu „Pripadnost projektu”.

## Veličine fontova

Veličine fontova mijenjaju se u datoteci `beamerthemeGFRI.sty`, u bloku naredbi
koje počinju s `\setbeamerfont`. Svaka naredba upravlja jednim dijelom
prezentacije:

| Naredba | Dio prezentacije |
| --- | --- |
| `title` | glavni naslov na naslovnom slajdu |
| `subtitle` | vrsta rada i naziv kolegija |
| `author` | ime i prezime autora |
| `institute` | studij, smjer i fakultet |
| `date` | mjesto i godina |
| `frametitle` | naslov običnog slajda |
| `framesubtitle` | podnaslov običnog slajda |
| `section title` | naslov sekcijskog slajda |
| `footline` | podatci u podnožju slajda |

Trenutačne postavke naslovnog slajda izgledaju ovako:

```tex
\setbeamerfont{title}{size=\fontsize{25}{29}\selectfont,series=\bfseries}
\setbeamerfont{subtitle}{size=\fontsize{10}{16}\selectfont}
\setbeamerfont{author}{size=\normalsize,series=\bfseries}
\setbeamerfont{institute}{size=\footnotesize}
\setbeamerfont{date}{size=\footnotesize}
```

U izrazu `\fontsize{25}{29}` prvi broj određuje veličinu slova, a drugi razmak
između redaka, oba u tipografskim točkama. Naredba `\selectfont` mora ostati na
kraju izraza. Preporučuje se mijenjati veličinu u koracima od 1 do 2 točke, a
razmak između redaka zadržati približno 3 do 5 točaka većim od veličine slova.

Za standardne LaTeX veličine mogu se koristiti, od manje prema većoj,
`\scriptsize`, `\footnotesize`, `\small`, `\normalsize`, `\large` i `\Large`.
Opcija `series=\bfseries` uključuje podebljani rez, dok je
`series=\mdseries` obični rez.

## Slike

Slike spremite u mapu `slike`. Zbog postavljene naredbe `\graphicspath`, mogu se
umetnuti bez navođenja cijele putanje:

```tex
\includegraphics[width=0.75\textwidth]{naziv-slike.png}
```

## Kompiliranje

Predložak podržava `pdfLaTeX` i `LuaLaTeX`.

### pdfLaTeX

Za osnovnu verziju predloška i najveću kompatibilnost upotrijebite `pdfLaTeX`:

```sh
latexmk -pdf prezentacija.tex
```

Za ručno kompiliranje:

```sh
pdflatex prezentacija.tex
pdflatex prezentacija.tex
```

### LuaLaTeX

Ako želite koristiti moderne OpenType ili sistemske fontove, upotrijebite
`LuaLaTeX`:

```sh
latexmk -lualatex prezentacija.tex
```

Za ručno kompiliranje:

```sh
lualatex prezentacija.tex
lualatex prezentacija.tex
```

Kod ručnog kompiliranja drugo je pokretanje potrebno kako bi se ažurirali sadržaj
i ukupan broj slajdova.

## Datoteke

- `prezentacija.tex` - primjer prezentacije i mjesto za unos sadržaja
- `beamerthemeGFRI.sty` - izgled slajdova i upravljanje logotipima
- `logo/gflogo.pdf` - obvezni GF logo
- `logo/logoipsum-434.png` - privremeni partnerski logo
- `slike/` - fotografije, dijagrami i ostale slike prezentacije
- `slike/primjer-slike.jpg` - probna slika korištena u oglednoj prezentaciji
