"""Funkcja Vercel udostępniająca silnik Monte Carlo przez HTTP."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from typing import Any

from silnik_api import oblicz_symulacje


class handler(BaseHTTPRequestHandler):
    """Obsługuje produkcyjne żądania POST pod adresem /api/symulacja."""

    def _wyslij_json(self, status: int, dane: dict[str, Any]) -> None:
        odpowiedz = json.dumps(dane, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(odpowiedz)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(odpowiedz)

    def do_GET(self) -> None:
        self._wyslij_json(200, {"status": "ok", "silnik": "Python + NumPy"})

    def do_POST(self) -> None:
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
