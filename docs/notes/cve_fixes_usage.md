# CveFixes - how to extract change data from db

## Possibilities

### file_change table

Diff_parsed (diff is ez kb): (sorszám, kód) párokban adja meg a hozzáadott, és kivett sorokat

- pro: könnyen kezelhető sorok
- con: nem használható önmagában (van, ahol csak added line van, ott kell a kontextus)

Code before/after + diff: közös használattal AST-vel megcsinálni

- pro: biztosan megvan a teljes kód, ami kell (azt azért vizsgálni kell valahogy, hogy csak egy fájlban volt-e change)
- con: bőségzavar? (hogyan pakoljuk össze ezeket, és válasszuk szét a szükséges metódust) - ez annyira nem okoz problémát
- ötlet: a fájlhoz tartozó method changek sorindexei alapján azonosítható a függvény
  - ezek után elég azt kiszervezni a code_before és code_afterből
  - viszont a sorok száma változhat a kettő között
  - fun fact: ez sem kell probably

### method_change tábla

code: leírja a teljes függvény működését

before_change: ez a változtatás előtti, vagy utáni állapot

- ha mindkettő megvan, akkor kész is vagyunk az új fájllal
  - és ha nincs? AST?
- arra szűrni kell valahogy, hogy Python kódot használjunk
  - jó eséllyel már a gyűjtésnél meg tudjuk ezt tenni, kis módosítással
- TODO: átnézni ehhez a gyűjtő kódot
  - hátha ki lehet küszöbölni azt is valahogy, hogy ne legyen ott a két method change rekord
  - illetve belerakni, hogy csak Python kódot gyűjtsön
