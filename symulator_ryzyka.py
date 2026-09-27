"""Konsolowy Symulator Ryzyka Decyzyjnego.

Łączy symulację Monte Carlo z prostą karą za złożoność inspirowaną
Brzytwą Ockhama. Program ma charakter analityczny i nie stanowi porady
finansowej ani gwarancji osiągnięcia określonego wyniku.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

import numpy as np


LICZBA_SYMULACJI = 10_000
KARA_ZA_RYZYKO = 0.05


@dataclass(frozen=True)
class WynikSymulacji:
    """Uporządkowany wynik, który można wykorzystać także poza konsolą."""

    prawdopodobienstwo_sukcesu: float
    sredni_wynik_netto: float
    bezpieczny_dol: float
    realny_sufit: float
    koszt_skomplikowania: float
    swiatlo: str


# Warstwa wejściowa pilnuje jakości danych. Błędne założenia wejściowe
# prowadzą do mylących prognoz, dlatego użytkownik jest proszony o korektę.
def _wczytaj_float(komunikat: str, *, minimum: float | None = None) -> float:
    while True:
        try:
            surowa_wartosc = input(komunikat).strip().replace(" ", "").replace(",", ".")
            wartosc = float(surowa_wartosc)
            if not np.isfinite(wartosc):
                raise ValueError
            if minimum is not None and wartosc < minimum:
                print(f"  Wartość nie może być mniejsza niż {minimum:g}.")
                continue
            return wartosc
        except ValueError:
            print("  Podaj poprawną liczbę, np. 125000 lub 125000,50.")


def _wczytaj_int(komunikat: str, *, minimum: int = 0) -> int:
    while True:
        try:
            wartosc = int(input(komunikat).strip())
            if wartosc < minimum:
                print(f"  Wartość nie może być mniejsza niż {minimum}.")
                continue
            return wartosc
        except ValueError:
            print("  Podaj liczbę całkowitą, np. 3.")


def _sprawdz_zalozenia(
    inwestycja: float,
    pesymistyczny: float,
    prawdopodobny: float,
    optymistyczny: float,
    liczba_ryzyk: int,
) -> None:
    """Odrzuca wartości, których rozkład trójkątny nie potrafi opisać."""

    wartosci = (inwestycja, pesymistyczny, prawdopodobny, optymistyczny)
    if not all(np.isfinite(wartosc) for wartosc in wartosci):
        raise ValueError("Wszystkie wartości finansowe muszą być skończonymi liczbami.")
    if inwestycja < 0:
        raise ValueError("Inwestycja nie może być ujemna.")
    if liczba_ryzyk < 0:
        raise ValueError("Liczba ryzyk nie może być ujemna.")
    if not pesymistyczny <= prawdopodobny <= optymistyczny:
        raise ValueError(
            "Scenariusze muszą spełniać warunek: pesymistyczny ≤ prawdopodobny ≤ optymistyczny."
        )


# Polskie formatowanie kwot ułatwia szybkie czytanie raportu biznesowego.
def _formatuj_kwote(wartosc: float) -> str:
    tekst = f"{wartosc:,.2f}"
    return tekst.replace(",", "_").replace(".", ",").replace("_", " ") + " zł"


def _kolor(tekst: str, kod_ansi: str) -> str:
    """Koloruje werdykt tylko wtedy, gdy terminal obsługuje kolory."""

    if not sys.stdout.isatty():
        return tekst
    return f"\033[{kod_ansi}m{tekst}\033[0m"


# Ta funkcja stanowi matematyczny rdzeń rozwiązania. Osobne API pozwala
# później podłączyć ten sam model do strony WWW, API albo raportu cyklicznego.
def symuluj_ryzyko(
    inwestycja: float,
    pesymistyczny: float,
    prawdopodobny: float,
    optymistyczny: float,
    liczba_ryzyk: int,
    *,
    liczba_symulacji: int = LICZBA_SYMULACJI,
    seed: int | None = None,
) -> WynikSymulacji:
    """Przeprowadza symulację i zwraca zagregowane mierniki decyzyjne."""

    _sprawdz_zalozenia(
        inwestycja, pesymistyczny, prawdopodobny, optymistyczny, liczba_ryzyk
    )
    if liczba_symulacji <= 0:
        raise ValueError("Liczba symulacji musi być większa od zera.")

    # Rozkład trójkątny wykorzystuje trzy zrozumiałe dla biznesu scenariusze.
    # Generator NumPy wykonuje wszystkie próby wektorowo, bez wolnej pętli Python.
    generator = np.random.default_rng(seed)
    if pesymistyczny == optymistyczny:
        symulowane_przychody = np.full(liczba_symulacji, pesymistyczny, dtype=float)
    else:
        symulowane_przychody = generator.triangular(
            pesymistyczny,
            prawdopodobny,
            optymistyczny,
            size=liczba_symulacji,
        )

    # Zysk bazowy pokazuje wynik finansowy po odzyskaniu początkowej inwestycji.
    zyski_przed_kara = symulowane_przychody - inwestycja

    # Filtr Ockhama traktuje każdą zależność jako ukryty koszt równy 5% inwestycji.
    # Kara jest identyczna w każdej próbie, więc przesuwa cały rozkład wyników w dół.
    koszt_skomplikowania = liczba_ryzyk * (inwestycja * KARA_ZA_RYZYKO)
    zyski_po_korekcie = zyski_przed_kara - koszt_skomplikowania

    # Agregaty odpowiadają na cztery pytania: jak często zarabiamy, ile średnio,
    # jak wygląda ostrożny dół oraz gdzie znajduje się realistyczny górny wynik.
    prawdopodobienstwo_sukcesu = float(np.mean(zyski_po_korekcie > 0) * 100)
    sredni_wynik_netto = float(np.mean(zyski_po_korekcie))
    bezpieczny_dol, realny_sufit = np.percentile(zyski_po_korekcie, [5, 95])

    # Światło przekłada wynik statystyczny na prosty komunikat zarządczy.
    if prawdopodobienstwo_sukcesu > 75:
        swiatlo = "ZIELONE"
    elif prawdopodobienstwo_sukcesu >= 50:
        swiatlo = "ŻÓŁTE"
    else:
        swiatlo = "CZERWONE"

    return WynikSymulacji(
        prawdopodobienstwo_sukcesu=prawdopodobienstwo_sukcesu,
        sredni_wynik_netto=sredni_wynik_netto,
        bezpieczny_dol=float(bezpieczny_dol),
        realny_sufit=float(realny_sufit),
        koszt_skomplikowania=koszt_skomplikowania,
        swiatlo=swiatlo,
    )


# Interfejs konsolowy zbiera założenia, uruchamia model i zamienia liczby
# w raport, który może być użyty podczas rozmowy decyzyjnej.
def uruchom_symulator_ryzyka(
    inwestycja: float | None = None,
    pesymistyczny: float | None = None,
    prawdopodobny: float | None = None,
    optymistyczny: float | None = None,
    liczba_ryzyk: int | None = None,
    *,
    seed: int | None = None,
) -> WynikSymulacji:
    """Uruchamia interaktywny symulator lub przyjmuje wartości programowo."""

    print("\n" + "═" * 66)
    print("  SYMULATOR RYZYKA DECYZYJNEGO — MONTE CARLO + BRZYTWA OCKHAMA")
    print("═" * 66)

    if inwestycja is None:
        inwestycja = _wczytaj_float("\nPoczątkowa inwestycja: ", minimum=0)

    # Scenariusze są wczytywane razem, ponieważ ich kolejność ma znaczenie
    # dla rozkładu. W trybie interaktywnym błąd można od razu poprawić.
    while True:
        if pesymistyczny is None:
            pesymistyczny = _wczytaj_float("Przychód — scenariusz pesymistyczny: ")
        if prawdopodobny is None:
            prawdopodobny = _wczytaj_float("Przychód — scenariusz prawdopodobny: ")
        if optymistyczny is None:
            optymistyczny = _wczytaj_float("Przychód — scenariusz optymistyczny: ")

        if pesymistyczny <= prawdopodobny <= optymistyczny:
            break
        if not sys.stdin.isatty():
            raise ValueError(
                "Scenariusze muszą spełniać warunek: pesymistyczny ≤ prawdopodobny ≤ optymistyczny."
            )
        print("\n  Scenariusze muszą rosnąć: pesymistyczny ≤ prawdopodobny ≤ optymistyczny.")
        pesymistyczny = prawdopodobny = optymistyczny = None

    if liczba_ryzyk is None:
        liczba_ryzyk = _wczytaj_int("Liczba zewnętrznych czynników ryzyka: ", minimum=0)

    wynik = symuluj_ryzyko(
        inwestycja,
        pesymistyczny,
        prawdopodobny,
        optymistyczny,
        liczba_ryzyk,
        seed=seed,
    )

    print("\n" + "─" * 66)
    print("  RAPORT Z 10 000 SYMULACJI")
    print("─" * 66)
    print(f"  Prawdopodobieństwo sukcesu : {wynik.prawdopodobienstwo_sukcesu:6.2f}%")
    print(f"  Średni wynik netto          : {_formatuj_kwote(wynik.sredni_wynik_netto)}")
    print(f"  Bezpieczny dół (P5)         : {_formatuj_kwote(wynik.bezpieczny_dol)}")
    print(f"  Realny sufit (P95)          : {_formatuj_kwote(wynik.realny_sufit)}")

    print("\n  WERDYKT BRZYTWY OCKHAMA")
    if liczba_ryzyk > 3:
        print("  ⚠ Plan jest zbyt skomplikowany — ma więcej niż 3 zależności.")
        print(
            "  Algorytm obniżył każdy prognozowany wynik o "
            f"{_formatuj_kwote(wynik.koszt_skomplikowania)}."
        )
    else:
        print("  ✓ Plan zachowuje prostotę i ma nie więcej niż 3 zależności.")
        print(
            "  Uwzględniony koszt istniejących ryzyk: "
            f"{_formatuj_kwote(wynik.koszt_skomplikowania)}."
        )

    kolory = {"ZIELONE": "1;32", "ŻÓŁTE": "1;33", "CZERWONE": "1;31"}
    print("\n  REKOMENDACJA KOŃCOWA")
    print(f"  Światło: {_kolor(wynik.swiatlo, kolory[wynik.swiatlo])}")
    print("═" * 66 + "\n")

    return wynik


# Przykładowe wywołanie: po kliknięciu „Run” program od razu zapyta
# o pięć wymaganych wartości i wyświetli kompletny raport.
if __name__ == "__main__":
    uruchom_symulator_ryzyka()
