"""A golden-hour radio station that schedules vinyl playlists."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Callable, Iterator

MAX_ROTATION = 40
SIGN_OFF = time(hour=23, minute=59)


class Genre(Enum):
    FUNK = "funk"
    SOUL = "soul"
    DISCO = "disco"
    JAZZ = "jazz"


@dataclass(frozen=True)
class Track:
    title: str
    artist: str
    year: int
    genre: Genre
    duration: float

    @property
    def is_vintage(self) -> bool:
        return self.year < 1975

    def __str__(self) -> str:
        minutes, seconds = divmod(int(self.duration), 60)
        return f"{self.artist} — {self.title} ({minutes}:{seconds:02d})"


@dataclass
class Playlist:
    name: str
    tracks: list[Track] = field(default_factory=list)

    def add(self, track: Track) -> None:
        if len(self.tracks) >= MAX_ROTATION:
            raise OverflowError(f"{self.name} is fully booked")
        self.tracks.append(track)

    def runtime(self) -> float:
        return sum(track.duration for track in self.tracks)

    def by_genre(self, genre: Genre) -> Iterator[Track]:
        return (track for track in self.tracks if track.genre == genre)


def on_air(handler: Callable[..., Track]) -> Callable[..., Track]:
    """Log every track as it goes out over the airwaves."""

    def wrapper(*args, **kwargs) -> Track:
        track = handler(*args, **kwargs)
        print(f"[ON AIR] {track}")
        return track

    return wrapper


class Station:
    def __init__(self, call_sign: str, frequency: float) -> None:
        self.call_sign = call_sign
        self.frequency = frequency
        self.playlists: dict[str, Playlist] = {}
        self._listeners = 0

    @on_air
    def spin(self, playlist_name: str) -> Track:
        playlist = self.playlists[playlist_name]
        if not playlist.tracks:
            raise LookupError("nothing on the platter")
        return random.choice(playlist.tracks)

    def schedule(self, playlist: Playlist) -> None:
        self.playlists[playlist.name] = playlist

    def sign_on(self) -> str:
        slots = ", ".join(self.playlists)
        return f"{self.call_sign} {self.frequency} FM — now playing: {slots}"


def build_evening_rotation() -> Playlist:
    rotation = Playlist("Golden Hour")
    for track in (
        Track("Move On Up", "Curtis Mayfield", 1970, Genre.SOUL, 528.0),
        Track("Cissy Strut", "The Meters", 1969, Genre.FUNK, 183.0),
        Track("Le Freak", "Chic", 1978, Genre.DISCO, 327.0),
        Track("Feeling Good", "Nina Simone", 1965, Genre.JAZZ, 177.0),
    ):
        rotation.add(track)
    return rotation


if __name__ == "__main__":
    station = Station("KGLD", 94.7)
    station.schedule(build_evening_rotation())
    print(station.sign_on())
    for _ in range(3):
        station.spin("Golden Hour")
