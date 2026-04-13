from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Airport:
    """Representa un aeropuerto dentro del grafo de rutas."""

    code: str
    name: str
    city: str
    country: str
    lat: float
    lon: float

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "city": self.city,
            "country": self.country,
            "lat": self.lat,
            "lon": self.lon,
        }
