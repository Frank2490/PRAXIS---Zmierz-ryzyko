"""Wspólna warstwa wejściowa dla API Vercela i serwera lokalnego."""

from __future__ import annotations

from typing import Any

import numpy as np

from symulator_ryzyka import LICZBA_SYMULACJI, symuluj_ryzyko


WYMAGANE_POLA = (
    "inwestycja",
    "pesymistyczny",
    "prawdopodobny",
    "optymistyczny",
    "liczba_ryzyk",
)


def oblicz_symulacje(dane: Any) -> dict[str, float | int | str]:
    """Waliduje dane JSON, uruchamia NumPy i zwraca odpowiedź gotową do serializacji."""

    if not isinstance(dane, dict):
        raise ValueError("Treść żądania musi być obiektem JSON.")

    brakujace = [pole for pole in WYMAGANE_POLA if pole not in dane]
    if brakujace:
        raise ValueError(f"Brak wymaganych pól: {', '.join(brakujace)}.")

    try:
        inwestycja = float(dane["inwestycja"])
        pesymistyczny = float(dane["pesymistyczny"])
        prawdopodobny = float(dane["prawdopodobny"])
        optymistyczny = float(dane["optymistyczny"])
        surowa_liczba_ryzyk = float(dane["liczba_ryzyk"])
    except (TypeError, ValueError) as blad:
        raise ValueError("Wszystkie parametry muszą być liczbami.") from blad

    if not np.isfinite(surowa_liczba_ryzyk) or not surowa_liczba_ryzyk.is_integer():
        raise ValueError("Liczba ryzyk musi być liczbą całkowitą.")
    liczba_ryzyk = int(surowa_liczba_ryzyk)

    wynik = symuluj_ryzyko(
        inwestycja=inwestycja,
        pesymistyczny=pesymistyczny,
        prawdopodobny=prawdopodobny,
        optymistyczny=optymistyczny,
        liczba_ryzyk=liczba_ryzyk,
    )

    return {
        "prawdopodobienstwo_sukcesu": wynik.prawdopodobienstwo_sukcesu,
        "sredni_wynik_netto": wynik.sredni_wynik_netto,
        "bezpieczny_dol": wynik.bezpieczny_dol,
        "realny_sufit": wynik.realny_sufit,
        "koszt_skomplikowania": wynik.koszt_skomplikowania,
        "swiatlo": wynik.swiatlo,
        "liczba_symulacji": LICZBA_SYMULACJI,
    }
