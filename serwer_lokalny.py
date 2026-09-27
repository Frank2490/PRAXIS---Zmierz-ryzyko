"""Lokalny serwer statycznej aplikacji oraz endpointu /api/symulacja."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from silnik_api import oblicz_symulacje


class LokalnyHandler(SimpleHTTPRequestHandler):
    def _wyslij_json(self, status: int, dane: dict) -> None:
        odpowiedz = json.dumps(dane, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(odpowiedz)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(odpowiedz)

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/api/symulacja":
            self._wyslij_json(200, {"status": "ok", "silnik": "Python + NumPy"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/api/symulacja":
            self._wyslij_json(404, {"error": "Nie znaleziono endpointu."})
            return
        try:
            rozmiar = int(self.headers.get("Content-Length", "0"))
            if rozmiar <= 0 or rozmiar > 16_384:
                raise ValueError("Nieprawidłowy rozmiar żądania.")
            dane = json.loads(self.rfile.read(rozmiar).decode("utf-8"))
            self._wyslij_json(200, oblicz_symulacje(dane))
        except (ValueError, json.JSONDecodeError) as blad:
            self._wyslij_json(400, {"error": str(blad)})
        except Exception:
            self._wyslij_json(500, {"error": "Wewnętrzny błąd silnika symulacji."})


def uruchom() -> None:
    adres = ("127.0.0.1", 8000)
    print("Praxis działa pod adresem http://127.0.0.1:8000")
    print("Zatrzymaj serwer skrótem Ctrl+C.")
    ThreadingHTTPServer(adres, LokalnyHandler).serve_forever()


if __name__ == "__main__":
    uruchom()
