---
name: prepare-work
description: "Pipeline developerski w wariancie pełnym albo uproszczonym oszczędzającym tokeny. Analiza -> wymagania -> plan -> implementacja -> testy -> review -> E2E -> dokumentacja. Use when the user says \"/prepare-work {opis}\", \"przygotuj i zaimplementuj {opis}\", \"zrób to end-to-end z review'ami\", or asks for a verified implementation workflow outside Azure DevOps."
---


# Prepare Work


## Wybór wariantu - zawsze pierwszy krok


Przed preflightem, czytaniem repo, wznowieniem przebiegu i utworzeniem artefaktów zadaj jedno
pytanie blokujące:


> Który wariant wybierasz?
> 1. **Pełny** - wszystkie fazy i bramki, osobne plany A/B, maksymalnie 2 rundy review.
> 2. **Uproszczony** - minimalny kontekst, scalone fazy, 1 review planu i 1 review kodu.


Nie wybieraj za usera i nie wykonuj wcześniej żadnej części zadania. Po odpowiedzi:


- `Pełny`: przeczytaj [playbook pełny](./full.md), nie czytaj `simplified.md`, wykonaj go od Fazy 0.
- `Uproszczony`: przeczytaj [playbook uproszczony](./simplified.md), nie czytaj `full.md`, wykonaj go od Fazy 0.


Wybrany playbook jest jedynym źródłem procedury. Nie łącz wariantów w jednym przebiegu. Zapisz
wybór jako `variant: full` albo `variant: simplified` w jego manifeście `_context.md`.
