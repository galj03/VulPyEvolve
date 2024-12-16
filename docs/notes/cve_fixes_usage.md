# CveFixes - how to extract change data from db

## file_change table

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

## method_change tábla

code: leírja a teljes függvény működését

before_change: ez a változtatás előtti, vagy utáni állapot

- ha mindkettő megvan, akkor kész is vagyunk az új fájllal
  - és ha nincs? AST?
- arra szűrni kell valahogy, hogy Python kódot használjunk
  - jó eséllyel már a gyűjtésnél meg tudjuk ezt tenni, kis módosítással
- TODO: átnézni ehhez a gyűjtő kódot
  - hátha ki lehet küszöbölni azt is valahogy, hogy ne legyen ott a két method change rekord
  - illetve belerakni, hogy csak Python kódot gyűjtsön

### method_change record analysis

7568 rekord tartozik a method_change táblához, ami egy Pythonos file_changehez köthető.
Python file_changeből 2753 van.

795 olyan file_change van, amelyhez pontosan kettő method_change tartozik (21%-a a python method_changeknek).
Tehát feltételezhető, hogy ezen esetekben egy metódus módosult, és ezen metódus régi és új verzióit tárolja az alkalmazás.
Ebben az esetben könnyen kinyerhető a tesztadatbázis szükséges formátuma, amivel a PyEvolve dolgozni tud.

Ha azokat a rekordokat vesszük, ahol egy file_changehez pontosan 2 method_change tartozik, akkor a 2*795=1590 rekordból ~262+73=335 nem használható a metódusnevek és az is_before_change érték alapján.

Megjegyzés: az utóbbi szám kézi vizsgálat eredénye, így tartalmazhat minimális hibát.

Tehát várhatóan nagyjából 1590-335=1255 rekorddal (627 metódussal) tudunk dolgozni, ahol valóban egy metódusban történt változás, és megtalálható a régi és az új kód is.

#### Queryk

  select count(*) from file_change where programming_language='Python'
  
  **Result**: 2753

  select count(*) from file_change join method_change on file_change.file_change_id=method_change.file_change_id

  **Result**: 7568

  "select file_change.file_change_id, count(*) from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id" > test.txt

  **Explanation**: melyik file_changehez hány method_change tartozik (előfeltétel: csak Python file_changek vannak az adatbázisban. Ha ez nem teljesül, be kell rakni egy where feltételt)

  "select asd, count(*) from (select file_change.file_change_id, count(*) as change_count from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id) group by change_count" > test2.txt

  **Explanation**: melyik method_change számból mennyi van. Az előző lekérdezés adataival dolgozunk tovább, hogy kiderítsük, hogyan oszlanak meg a method_change rekordok számosságai fájlok szerint.

  "select * from (select file_change.file_change_id as id, count(*) as change_count from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id) where change_count=2" > test3.txt

  **Explanation**: Kilistázza azokat a file_changeket, amelyekhez pontosan 2 db method_change tartozik

  "select signature, before_change from method_change where file_change_id in (select file_change.file_change_id as id from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id having count(*)=2) order by signature" > test4.txt

  Updated version:

  "select signature, before_change, file_change_id from method_change where file_change_id in (select file_change.file_change_id as id from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id having count(*)=2) order by file_change_id" > test4.txt

  **Explanation**: kiszedi a metódus neveket (a 2 method_changes fileokra) és azt, hogy ez a korábbi vagy a későbbi. Ez alapján ellenőrizhető, hogy tényleg összefüggőek-e a rekordok.

### Egy CVE-re jutó fixek száma

Ha a fixes, commits, file_change táblákat összekapcsoljuk INNER JOIN-nal,
akkor 3109 rekordot kapunk, a 2753 file_change rekordhoz képest.

Hipotézis: van olyan commit, amely több CVE-t is fixál, ez okozza a különbséget.

A hipotézis igaz valója nem befolyásolja a mostani feladatot, de érdemes lehet a harmadik fázisban,
a kiértékelés kezdetén megvizsgálni ezt.

#### Queryk

  select count(file_change_id) from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash
  
  **Result**: 3109

  select count(distinct file_change_id) from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash

  **Result**: 2753

  sqlite3 CVEfixes_108.db "select cve_id, count(distinct file_change_id) from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash group by cve_id" > test_cve_count_1.txt

  **Explanation**: összegyűjti, hány különböző file change jut egy CVE-re.

  select count(*) from (select cve_id, count(distinct file_change_id) from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash group by cve_id)

  **Result**: 1089 - ennyi CVE-hez tartozik valamennyi fix
  (minden file change egyszer számolva)

  select count(*) from (select cve_id, count(distinct file_change_id) from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash group by cve_id)

  **Result**: 1089 - ennyi CVE-hez tartozik valamennyi fix
  (minden file change annyiszor számolva, ahányszor előfordul)

  sqlite3 CVEfixes_108.db "select cve_id, count(file_change_id) from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash where file_change_id in (select id from (select file_change.file_change_id as id, count(*) as change_count from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id) where change_count=2) group by cve_id" > test_cve_count_2.txt

  **Explanation**: itt csak azokat a fixeket számoltuk,
  amelyben a file changehez 2 method_change tartozik (használható)

  select sum(fix_count) from (select cve_id, count(file_change_id) as fix_count from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash where file_change_id in (select id from (select file_change.file_change_id as id, count(*) as change_count from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id) where change_count=2) group by cve_id)

  **Result**: 914 - összesen ennyi használható CVE fixünk van

  select sum(fix_count) from (select cve_id, count(file_change_id) as fix_count from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url join file_change on commits.hash=file_change.hash where file_change_id in (select id from (select file_change.file_change_id as id, count(*) as change_count from file_change join method_change on file_change.file_change_id=method_change.file_change_id group by file_change.file_change_id) where change_count=2) group by cve_id having count(file_change_id)>1)

  **Result**: 585 - ennyi használható CVE fixünk van, ahol egy CVE-hez több fix is tartozik

  TODO: az utolsó két queryt felül kell vizsgálni, mert feltételezhető,
  hogy a fáradtság befolyásolta az eredményeket egy-egy kisebb elírás formájában
  