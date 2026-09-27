# Praxis — kalkulator ryzyka

Interaktywny kalkulator prawdopodobieństwa powodzenia oparty na:

- częstości bazowej,
- modelu logarytmu szans,
- niezawodności zależności,
- regule wielu niezależnych prób,
- symulacji Monte Carlo (10 000 przebiegów),
- analizie wrażliwości czynników.

Repozytorium zawiera także konsolowy **Symulator Ryzyka Decyzyjnego** w Pythonie,
który łączy 10 000 prób Monte Carlo z karą za złożoność inspirowaną Brzytwą Ockhama.

## Uruchomienie

Otwórz `index.html` w przeglądarce albo uruchom lokalny serwer:

```bash
python3 -m http.server 8000
```

Następnie wejdź na `http://localhost:8000`.

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

Projekt jest statyczny i nie wymaga procesu budowania. Katalog główny można wdrożyć bezpośrednio:

- GitHub Pages — źródło: gałąź `main`, katalog `/ (root)`,
- Netlify — publish directory: `.`, bez build command,
- Vercel — framework preset: `Other`, output directory: `.`.

Plik `.nojekyll` zapewnia bezpośrednie publikowanie zasobów na GitHub Pages.

## Ważne ograniczenie

To ogólny model wspierający myślenie scenariuszowe, nie narzędzie walidowane dla konkretnej dziedziny. Nie zastępuje modeli branżowych ani opinii eksperta w decyzjach medycznych, finansowych, inżynieryjnych czy dotyczących bezpieczeństwa.
