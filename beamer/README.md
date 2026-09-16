# GFRI Beamer predložak

Predložak je namijenjen prezentacijama Građevinskog fakulteta u Rijeci. GF logo
`logo/gflogo.pdf` obvezan je i prikazuje se na naslovnom slajdu, sekcijskim
slajdovima i u podnožju ostalih slajdova. Tema koristi crnu, bijelu i sivu boju.
Tanka traka uz donji rub svakog slajda prikazuje napredak kroz prezentaciju.

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
