---
id: <unikalny-slug>
status: current
type: <fact|decision|reference|mixed>
scope: <np. backend/telemetry>
last_reviewed: <YYYY-MM-DD>
# applies_to tylko dla L2 (kontrakty) - włącza wykrywanie rozjazdu doc<->kod.
# Usuń, jeśli dokument nie opisuje konkretnego fragmentu kodu (L3, L4).
applies_to:
  - <glob/kodu/**>
---

<!--
Jeden szablon dla trzech warstw operacyjnych — L2 (kontrakty), L3 (pamięć
robocza), L4 (dowody). Nie jest to skrót jakości: różnią się wymaganymi
polami front-matter (patrz komentarze wyżej i METADATA.md) i tym, na co
kładziesz nacisk w treści — nie strukturą pliku.

Cztery szablony, które MAJĄ własną, odrębną formę i zostają osobno:
PRODUCT, CONTEXT, adr, KNOWLEDGE-MAP. Wszystko inne — opis modułu, kontrakt
API, runbook, specyfikacja zadania, notatka z badania, eksperyment — zaczyna
się od tego pliku. Jeśli po kilku użyciach ten sam kształt sekcji powtarza się
w kółko dla jednego typu dokumentu, to jest sygnał, żeby wydzielić dla niego
osobny szablon — nie zanim to się stanie.

Test kontrolny tytułu: to PYTANIE, na które dokument odpowiada, nie temat.
„Jak działa provisioning urządzenia?" zamiast „Provisioning".
-->

# <Tytuł>

<!-- Jedno-dwa zdania: po co ten dokument istnieje i kto go potrzebuje. -->

## Kontekst

<!--
Skąd się to wzięło. Dla L2: jaki problem rozwiązuje ten fragment systemu.
Dla L3: co wywołało to zadanie. Dla L4: co skłoniło do tego badania.
Fakty i ograniczenia z linkiem do źródła — nie uzasadnienie wyboru (to niżej).
-->

## <Właściwa treść — nazwij sekcję pytaniem, na które odpowiada>

<!--
To jest serce dokumentu i jedyna część, którą naprawdę projektujesz sam.
Podpowiedzi wg warstwy — wybierz to, co pasuje, zignoruj resztę:

L2 (kontrakt / moduł / interfejs):
  • Co to gwarantuje, czego NIE gwarantuje
  • Niezmienniki — warunki, które muszą być prawdą, a kod ich nie wymusza
  • Publiczny interfejs z linkiem do kodu: [`plik.py#L42`](../../src/plik.py#L42)
  • Dlaczego tak, a nie prościej — z linkiem do ADR, jeśli istnieje

L3 (specyfikacja zadania / plan / brief):
  • W zakresie / poza zakresem — obie listy, nie tylko pierwsza
  • Decyzje już podjęte, o które wykonawca nie pyta
  • Definicja ukończenia — warunki sprawdzalne, nie „działa poprawnie"

L4 (badanie / dowód / analiza):
  • Ustalenia, każde z przypisem do źródła i datą źródła
  • Luki i niepewności — czego nie wiadomo i dlaczego
  • Wnioski WYRAŹNIE oddzielone od ustaleń, z jawnym „co dalej"
    (ADR / kolejne badanie / świadome odłożenie)
-->

## Otwarte punkty / znane ograniczenia

<!--
Co jest niedokończone albo niepewne w chwili `last_reviewed`. Pusta sekcja jest
podejrzana — zwykle znaczy, że nikt nie szukał.
-->

## Powiązania

<!-- Linki do dokumentów, kodu, ADR. Nie kopiuj treści — tylko odsyłacz. -->
