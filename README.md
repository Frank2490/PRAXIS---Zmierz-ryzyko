# Praxis — kalkulator ryzyka

Internetowy Symulator Ryzyka Decyzyjnego oparty na:

- trzech scenariuszach przychodu,
- rozkładzie trójkątnym,
- symulacji Monte Carlo (10 000 prób),
- koszcie początkowej inwestycji,
- karze za złożoność inspirowanej Brzytwą Ockhama,
- percentylach P5 i P95 oraz świetle decyzyjnym.

Interfejs WWW komunikuje się z endpointem `/api/symulacja`, który uruchamia
silnik Python/NumPy jako funkcję Vercela. Ten sam model jest dostępny w konsoli.

## Uruchomienie

Zainstaluj zależności i uruchom serwer obsługujący stronę oraz lokalne API:

```bash
python3 -m pip install -r requirements.txt
python3 serwer_lokalny.py
```

Następnie wejdź na `http://127.0.0.1:8000`.

Możesz też użyć:

```bash
npm start
```

## Symulator w Pythonie

Zainstaluj zależność i uruchom program:

```bash
python3 -m pip install -r requirements.txt
python3 symulator_ryzyka.py
```

Program poprosi o inwestycję, trzy scenariusze przychodów i liczbę czynników ryzyka,
a następnie pokaże prawdopodobieństwo sukcesu, oczekiwany wynik, percentyle P5/P95,
werdykt Brzytwy Ockhama oraz czerwone, żółte lub zielone światło decyzyjne.

Silnik można również wywołać z innego modułu:

```python
from symulator_ryzyka import symuluj_ryzyko

wynik = symuluj_ryzyko(
    inwestycja=100_000,
    pesymistyczny=70_000,
    prawdopodobny=140_000,
    optymistyczny=240_000,
    liczba_ryzyk=3,
    seed=42,
)
print(wynik)
```

## Wdrożenie

Projekt jest przygotowany do wdrożenia na Vercelu. Pliki interfejsu są statyczne,
a `api/symulacja.py` jest automatycznie wykrywany jako funkcja Python. Zależności
funkcji są instalowane z `requirements.txt`.

## Testy

```bash
npm run check
```

## Ważne ograniczenie

To ogólny model wspierający myślenie scenariuszowe, nie narzędzie walidowane dla konkretnej dziedziny. Nie zastępuje modeli branżowych ani opinii eksperta w decyzjach medycznych, finansowych, inżynieryjnych czy dotyczących bezpieczeństwa.
