# Tématerv - Gál József

## Személyes adatok

**Név:** Gál József

**Neptun:** BSRKB5

**E-mail:** <h260710@stud.u-szeged.hu>

**Szak:** programtervező informatikus BSc nappali

**Végzés várható ideje:** 2025. nyár

## A szakdolgozat tárgya

Az alkalmazás egy APR tool lesz, amely képes felismerni CPAT-ket egy adott projektben. Ezen belül is sérülékenységek javítását tanítanánk be neki. Ezután automatikusan kijavítja azokat az inputként kapott projektben. Ezután (szintén automatikusan) egy (vagy több) másik tool segítségével kiértékeli, hogy az APR mennyire volt sikeres. Utóbbi működéséhez tesztek is szükségesek, mivel az egyik tool arra figyel oda, hogy a generált kód biztosan ne legyen test-overfitted.

Az alkalmazás Python projekteket céloz meg, ezzel is segítve többek között a mesterséges intelligencia területét, amely a leggyorsabban feljődő kutatási terület az informatikában. A tervek szerint az alkalmazás egy multiplatform CLI-app lenne, Pythonban írva (lehetséges, hogy egyes használt toolok nem abban voltak megírva eredetileg - remélem, nem lesz ilyen -, de a futtatás Pythonban történik majd).

## Használni kívánt technológiák

- Python 3.12
- pipx
- typer
- PyEvolve
  - open-source CPAT miner tool
    - nem csak bányászik, alkalmazza is ezeket adott projekten
    - csak sérülékenységet bányászatunk vele
- sérülékenységeket tartalmazó adatbázis
- egy vulnerability fix kiértékelő tool
  - ki kéne értékelni valamivel, hogy valid-e a fix
        - security-related tesztek használata
        - ezeket talán generáltatni kell valamivel
    - a PyEvolve nem nézi, hogy biztonságos-e a megoldás, amit használ
      - de alapvetően ilyeneket tanítunk be neki
- Invalidator
  - APR kiértékelő tool
    - tesztekre támaszkodik
- egyéb kiértékelő, enhancer toolok (opcionális)

## Tervezett ütemezés

- **2024. szeptember:** hiányzó tool(ok) keresése
- **2024. október:** ismerkedés a toolokkal, azok használata egymás után egy projekten
- **2024. november:** hogyan kell meghívni az appokat más sourceból (ami a mi alkalmazásunk lesz), CLI app kezdete
- **2024. december:** CLI app, tesztelés kezdete
- **2025. január:** CLI app - hibajavítás, tesztelés
- **2025. február:** esetleges új funkciók, kiértékelés, hibajavítás
- **2025. március:** hibajavítás, szakdolgozat írás
- **2025. április:** szakdolgozat írás
