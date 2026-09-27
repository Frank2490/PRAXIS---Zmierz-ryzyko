import unittest

from silnik_api import oblicz_symulacje
from symulator_ryzyka import symuluj_ryzyko


class TestSymulatorRyzyka(unittest.TestCase):
    def test_staly_scenariusz_daje_dokladny_wynik(self):
        wynik = symuluj_ryzyko(100, 120, 120, 120, 2, seed=1)

        self.assertEqual(wynik.prawdopodobienstwo_sukcesu, 100.0)
        self.assertEqual(wynik.sredni_wynik_netto, 10.0)
        self.assertEqual(wynik.bezpieczny_dol, 10.0)
        self.assertEqual(wynik.realny_sufit, 10.0)
        self.assertEqual(wynik.koszt_skomplikowania, 10.0)

    def test_api_zwraca_wymagane_metryki(self):
        wynik = oblicz_symulacje(
            {
                "inwestycja": 100_000,
                "pesymistyczny": 70_000,
                "prawdopodobny": 140_000,
                "optymistyczny": 240_000,
                "liczba_ryzyk": 3,
            }
        )

        self.assertEqual(wynik["liczba_symulacji"], 10_000)
        self.assertIn(wynik["swiatlo"], {"ZIELONE", "ŻÓŁTE", "CZERWONE"})
        self.assertGreaterEqual(wynik["prawdopodobienstwo_sukcesu"], 0)
        self.assertLessEqual(wynik["prawdopodobienstwo_sukcesu"], 100)
        self.assertLessEqual(wynik["bezpieczny_dol"], wynik["sredni_wynik_netto"])
        self.assertLessEqual(wynik["sredni_wynik_netto"], wynik["realny_sufit"])

    def test_api_odrzuca_nieprawidlowa_kolejnosc_scenariuszy(self):
        with self.assertRaises(ValueError):
            oblicz_symulacje(
                {
                    "inwestycja": 100,
                    "pesymistyczny": 200,
                    "prawdopodobny": 100,
                    "optymistyczny": 300,
                    "liczba_ryzyk": 1,
                }
            )

    def test_api_odrzuca_ulamkowa_liczbe_ryzyk(self):
        with self.assertRaises(ValueError):
            oblicz_symulacje(
                {
                    "inwestycja": 100,
                    "pesymistyczny": 50,
                    "prawdopodobny": 100,
                    "optymistyczny": 150,
                    "liczba_ryzyk": 1.5,
                }
            )


if __name__ == "__main__":
    unittest.main()
