<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";

  interface Track {
    id: number;
    title: string;
    artist: string;
    year: number;
    genre: string;
    coverUrl: string;
  }

  export let tracks: Track[] = [];
  export let autoplay: boolean = false;

  const dispatch = createEventDispatcher<{
    select: Track;
    play: Track;
    error: string;
  }>();

  let currentTrack: Track | null = null;
  let isPlaying = false;
  let searchQuery = "";
  let volume = 75;
  let elapsed = 0;
  let intervalId: ReturnType<typeof setInterval> | null = null;

  $: filteredTracks = tracks.filter(
    (t) =>
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.artist.toLowerCase().includes(searchQuery.toLowerCase())
  );

  $: progressPercent = currentTrack ? Math.min((elapsed / 240) * 100, 100) : 0;

  $: genreCounts = tracks.reduce<Record<string, number>>((acc, t) => {
    acc[t.genre] = (acc[t.genre] ?? 0) + 1;
    return acc;
  }, {});

  function selectTrack(track: Track): void {
    currentTrack = track;
    elapsed = 0;
    dispatch("select", track);

    if (autoplay) {
      play();
    }
  }

  function play(): void {
    if (!currentTrack) return;

    isPlaying = true;
    dispatch("play", currentTrack);

    intervalId = setInterval(() => {
      elapsed += 1;
      if (elapsed >= 240) {
        stop();
        next();
      }
    }, 1000);
  }

  function stop(): void {
    isPlaying = false;
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  }

  function next(): void {
    if (!currentTrack) return;
    const idx = tracks.findIndex((t) => t.id === currentTrack!.id);
    if (idx < tracks.length - 1) {
      selectTrack(tracks[idx + 1]);
    }
  }

  function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  onMount(() => {
    console.log(`Jukebox loaded with ${tracks.length} tracks`);
    return () => stop();
  });
</script>

<div class="jukebox" class:playing={isPlaying}>
  <header class="jukebox-header">
    <h1>Technicolor Jukebox</h1>
    <span class="track-count">{filteredTracks.length} tracks</span>
  </header>

  <div class="search-bar">
    <input
      type="text"
      bind:value={searchQuery}
      placeholder="Search tracks..."
      aria-label="Search tracks"
    />
  </div>

  {#if currentTrack}
    <div class="now-playing">
      <img src={currentTrack.coverUrl} alt={currentTrack.title} class="cover" />
      <div class="track-info">
        <h2>{currentTrack.title}</h2>
        <p>{currentTrack.artist} &middot; {currentTrack.year}</p>
        <div class="progress-bar">
          <div class="progress-fill" style="width: {progressPercent}%"></div>
        </div>
        <span class="time">{formatTime(elapsed)} / 4:00</span>
      </div>
      <div class="controls">
        {#if isPlaying}
          <button on:click={stop} aria-label="Pause">⏸</button>
        {:else}
          <button on:click={play} aria-label="Play">▶</button>
        {/if}
        <button on:click={next} aria-label="Next">⏭</button>
        <input
          type="range"
          min="0"
          max="100"
          bind:value={volume}
          aria-label="Volume"
        />
      </div>
    </div>
  {/if}

  <div class="genre-tags">
    {#each Object.entries(genreCounts) as [genre, count]}
      <span class="tag">{genre} ({count})</span>
    {/each}
  </div>

  <ul class="track-list">
    {#each filteredTracks as track (track.id)}
      <!-- svelte-ignore a11y-no-noninteractive-element-to-interactive-role -->
      <li
        class:active={currentTrack?.id === track.id}
        onclick={() => selectTrack(track)}
        onkeydown={(e) => e.key === "Enter" && selectTrack(track)}
        role="button"
        tabindex="0"
      >
        <span class="track-title">{track.title}</span>
        <span class="track-artist">{track.artist}</span>
        <span class="track-year">{track.year}</span>
      </li>
    {:else}
      <li class="empty">No tracks found</li>
    {/each}
  </ul>
</div>

<style>
  .jukebox {
    --accent: #e87800;
    --bg: #1a1a1a;
    --surface: #252525;
    --text: #c8b88a;
    --muted: #666;

    background: var(--bg);
    color: var(--text);
    font-family: "JetBrains Mono", monospace;
    max-width: 640px;
    margin: 0 auto;
    border-radius: 12px;
    overflow: hidden;
  }

  .jukebox-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    background: linear-gradient(135deg, #1a1a1a, #252525);
    border-bottom: 2px solid var(--accent);
  }

  .jukebox-header h1 {
    font-size: 1.5rem;
    color: var(--accent);
    margin: 0;
  }

  .track-count {
    color: var(--muted);
    font-size: 0.85rem;
  }

  .search-bar {
    padding: 1rem 2rem;
  }

  .search-bar input {
    width: 100%;
    padding: 0.6rem 1rem;
    background: var(--surface);
    border: 1px solid #333;
    border-radius: 6px;
    color: var(--text);
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
  }

  .search-bar input:focus {
    border-color: var(--accent);
  }

  .now-playing {
    display: grid;
    grid-template-columns: 80px 1fr auto;
    gap: 1rem;
    padding: 1rem 2rem;
    background: var(--surface);
    align-items: center;
  }

  .cover {
    width: 80px;
    height: 80px;
    border-radius: 8px;
    object-fit: cover;
  }

  .track-info h2 {
    margin: 0;
    font-size: 1.1rem;
    color: #e87800;
  }

  .track-info p {
    margin: 0.25rem 0;
    color: var(--muted);
    font-size: 0.85rem;
  }

  .progress-bar {
    height: 4px;
    background: #333;
    border-radius: 2px;
    margin-top: 0.5rem;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent);
    transition: width 1s linear;
  }

  .controls {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: center;
  }

  .controls button {
    background: none;
    border: 1px solid var(--accent);
    color: var(--accent);
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .controls button:hover {
    background: var(--accent);
    color: var(--bg);
  }

  .genre-tags {
    display: flex;
    gap: 0.5rem;
    padding: 0.5rem 2rem;
    flex-wrap: wrap;
  }

  .tag {
    background: #333;
    color: var(--text);
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
  }

  .track-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .track-list li {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 1rem;
    padding: 0.8rem 2rem;
    cursor: pointer;
    transition: background 0.15s;
    border-bottom: 1px solid #222;
  }

  .track-list li:hover {
    background: var(--surface);
  }

  .track-list li.active {
    background: var(--surface);
    border-left: 3px solid var(--accent);
  }

  .track-artist {
    color: var(--muted);
  }

  .track-year {
    color: var(--muted);
    font-size: 0.85rem;
  }

  .empty {
    text-align: center;
    color: var(--muted);
    padding: 2rem;
  }

  .jukebox.playing .jukebox-header {
    border-bottom-color: #a2c44c;
  }
</style>
