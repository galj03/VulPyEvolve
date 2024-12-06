# Meeting - Discord, 2024.11.11

## Témakör

- Korábbi haladás
- Workflow diagram részletei

## Megjegyzések

- evalutaionhöz megnézni a CveFixes citationjeit (mivel értékeltek ki mások?)
- method_change és file_change tábla nézegetése, hogyan lehet kiszedni a régi és javított kódot
  - AST-s megoldás maybe?
- Rule generálás + használat:
  1. CveFixes db instanceből kiszedni a kódot (l+r)
  2. InferRules futtatása -> MainAdaptor.java -> infer command
  3. PyEvolve phase 3+4 futtatása -> MainAdaptor.java -> transform command

## Nyitott kérdések, ami még hátra van OVR

- Mivel értékeljünk ki?
  - statikus toolok nem olyan jók, nagyon alap dolgokat érzékelnek csak probably
- RQ-k?
- Konfiguráció megtervezése
- Hogyan használjuk a db-t?
