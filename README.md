# Praxis — kalkulator ryzyka

Interaktywny kalkulator prawdopodobieństwa powodzenia oparty na:

- częstości bazowej,
- modelu logarytmu szans,
- niezawodności zależności,
- regule wielu niezależnych prób,
- symulacji Monte Carlo (10 000 przebiegów),
- analizie wrażliwości czynników.

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

## Wdrożenie

Projekt jest statyczny i nie wymaga procesu budowania. Katalog główny można wdrożyć bezpośrednio:

- GitHub Pages — źródło: gałąź `main`, katalog `/ (root)`,
- Netlify — publish directory: `.`, bez build command,
- Vercel — framework preset: `Other`, output directory: `.`.

Plik `.nojekyll` zapewnia bezpośrednie publikowanie zasobów na GitHub Pages.

## Ważne ograniczenie

To ogólny model wspierający myślenie scenariuszowe, nie narzędzie walidowane dla konkretnej dziedziny. Nie zastępuje modeli branżowych ani opinii eksperta w decyzjach medycznych, finansowych, inżynieryjnych czy dotyczących bezpieczeństwa.
