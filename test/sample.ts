import { EventEmitter } from "events";

// A retro jukebox that manages a playlist of vinyl records
interface Track {
  title: string;
  artist: string;
  year: number;
  duration: number;
  genre: "funk" | "soul" | "disco" | "jazz";
}

type PlaybackState = "playing" | "paused" | "stopped";

enum Decade {
  Sixties = 1960,
  Seventies = 1970,
  Eighties = 1980,
}

const MAX_QUEUE_SIZE = 50;
const DEFAULT_VOLUME = 0.7;

class Jukebox extends EventEmitter {
  on(arg0: string, arg1: (track: Track) => void) {
    throw new Error("Method not implemented.");
  }
  private playlist: Track[] = [];
  private currentIndex: number = -1;
  private state: PlaybackState = "stopped";
  private _volume: number = DEFAULT_VOLUME;

  constructor(private readonly name: string) {
    super();
  }

  get volume(): number {
    return this._volume;
  }

  set volume(val: number) {
    this._volume = Math.max(0, Math.min(1, val));
  }

  get currentTrack(): Track | undefined {
    return this.playlist[this.currentIndex];
  }

  async addTrack(track: Track): Promise<void> {
    if (this.playlist.length >= MAX_QUEUE_SIZE) {
      throw new Error(`Queue full: max ${MAX_QUEUE_SIZE} tracks`);
    }
    this.playlist.push(track);
    this.emit("trackAdded", track);
  }
  emit(arg0: string, track: Track | undefined) {
    throw new Error("Method not implemented.");
  }

  play(): void {
    if (this.playlist.length === 0) return;

    if (this.currentIndex < 0) {
      this.currentIndex = 0;
    }

    this.state = "playing";
    const track = this.currentTrack!;
    console.log(
      `♪ Now playing: ${track.title} by ${track.artist} (${track.year})`,
    );
    this.emit("play", track);
  }

  pause(): void {
    if (this.state !== "playing") return;
    this.state = "paused";
    if (this.currentTrack) {
      this.emit("pause", this.currentTrack);
    }
  }

  skip(): void {
    if (this.currentIndex < this.playlist.length - 1) {
      this.currentIndex++;
      this.play();
    } else {
      this.state = "stopped";
      this.emit("queueEnd", undefined);
    }
  }

  filterByDecade(decade: Decade): Track[] {
    return this.playlist.filter(
      (t) => t.year >= decade && t.year < decade + 10,
    );
  }

  shuffle(): void {
    for (let i = this.playlist.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.playlist[i], this.playlist[j]] = [
        this.playlist[j],
        this.playlist[i],
      ];
    }
    this.currentIndex = 0;
  }

  getStats(): Record<string, number> {
    const stats: Record<string, number> = {};
    for (const track of this.playlist) {
      stats[track.genre] = (stats[track.genre] ?? 0) + 1;
    }
    return stats;
  }

  toString(): string {
    return `Jukebox<${this.name}>[${this.playlist.length} tracks, ${this.state}]`;
  }
}

// Generic helper
function groupBy<T, K extends string>(
  items: T[],
  keyFn: (item: T) => K,
): Record<K, T[]> {
  const result = {} as Record<K, T[]>;
  for (const item of items) {
    const key = keyFn(item);
    (result[key] ??= []).push(item);
  }
  return result;
}

// Decorator-style higher-order function
function withLogging<T extends (...args: unknown[]) => unknown>(
  fn: T,
  label: string,
): T {
  return ((...args: unknown[]) => {
    console.log(`[${label}] called with`, args);
    const result = fn(...args);
    console.log(`[${label}] returned`, result);
    return result;
  }) as T;
}

// Usage
async function main() {
  const jukebox = new Jukebox("Studio 54");

  await jukebox.addTrack({
    title: "Superstition",
    artist: "Stevie Wonder",
    year: 1972,
    duration: 245,
    genre: "funk",
  });

  await jukebox.addTrack({
    title: "A Love Supreme",
    artist: "John Coltrane",
    year: 1965,
    duration: 1980,
    genre: "jazz",
  });

  jukebox.on("play", (track: Track) => {
    console.log(`Event: playing ${track.title}`);
  });

  jukebox.play();

  const seventies = jukebox.filterByDecade(Decade.Seventies);
  const grouped = groupBy(seventies, (t) => t.genre);
  console.log("70s tracks by genre:", grouped);

  try {
    for (let i = 0; i < 100; i++) {
      await jukebox.addTrack({
        title: `Track ${i}`,
        artist: "Unknown",
        year: 1975,
        duration: 180,
        genre: "disco",
      });
    }
  } catch (err) {
    if (err instanceof Error) {
      console.error("Caught:", err.message);
    }
  }
}

main();
