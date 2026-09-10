# GFRI Beamer predložak

Predložak je namijenjen prezentacijama Građevinskog fakulteta u Rijeci. GF logo
`gflogo.pdf` obvezan je i prikazuje se na naslovnom slajdu, sekcijskim slajdovima
i u podnožju ostalih slajdova. Tema koristi crnu, bijelu i sivu boju. Tanka traka
uz donji rub svakog slajda prikazuje napredak kroz prezentaciju.

## Dodatni logotipi

Na početku datoteke `prezentacija.tex` postavite datoteke za najviše dva dodatna
logotipa:

```tex
\GFRIsetpartnerlogoA{logo-partnera-a.pdf}
\GFRIsetpartnerlogoB{logo-partnera-b.png}
```

Svaki se logotip uključuje ili isključuje zasebno:

```tex
\GFRIpartnerAtrue   % prikaz prvog dodatnog logotipa
\GFRIpartnerAfalse  % skrivanje prvog dodatnog logotipa

\GFRIpartnerBtrue   % prikaz drugog dodatnog logotipa
\GFRIpartnerBfalse  % skrivanje drugog dodatnog logotipa
```

Datoteka `logoipsum-434.png` služi samo kao privremeni primjer. Zamijenite je
stvarnim partnerskim logotipima prije izrade završne prezentacije.

## Kompiliranje

Predložak se kompilira LuaLaTeXom:

```sh
latexmk -lualatex prezentacija.tex
```

Za ručno kompiliranje može se upotrijebiti i:

```sh
lualatex prezentacija.tex
lualatex prezentacija.tex
```

Drugo pokretanje potrebno je kako bi se ažurirali sadržaj i ukupan broj slajdova.

## Datoteke

- `prezentacija.tex` - primjer prezentacije i mjesto za unos sadržaja
- `beamerthemeGFRI.sty` - izgled slajdova i upravljanje logotipima
- `gflogo.pdf` - obvezni GF logo
- `logoipsum-434.png` - privremeni partnerski logo
