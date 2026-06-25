package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

// Record represents a vinyl record in the collection
type Record struct {
	Title    string   `json:"title"`
	Artist   string   `json:"artist"`
	Year     int      `json:"year"`
	Genre    Genre    `json:"genre"`
	Tracks   []string `json:"tracks"`
	Duration float64  `json:"duration"`
}

// Genre is an enum-like type for music genres
type Genre string

const (
	Funk  Genre = "funk"
	Soul  Genre = "soul"
	Disco Genre = "disco"
	Jazz  Genre = "jazz"
)

// Collection manages a thread-safe vinyl collection
type Collection struct {
	mu      sync.RWMutex
	records map[string]*Record
	maxSize int
}

// NewCollection creates a new collection with a max size
func NewCollection(maxSize int) *Collection {
	return &Collection{
		records: make(map[string]*Record),
		maxSize: maxSize,
	}
}

// Add inserts a record into the collection
func (c *Collection) Add(r *Record) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if len(c.records) >= c.maxSize {
		return fmt.Errorf("collection full: max %d records", c.maxSize)
	}

	key := fmt.Sprintf("%s-%s", r.Artist, r.Title)
	c.records[key] = r
	return nil
}

// FindByGenre returns all records matching the given genre
func (c *Collection) FindByGenre(genre Genre) []*Record {
	c.mu.RLock()
	defer c.mu.RUnlock()

	var results []*Record
	for _, r := range c.records {
		if r.Genre == genre {
			results = append(results, r)
		}
	}
	return results
}

// FindByDecade returns records from a specific decade
func (c *Collection) FindByDecade(startYear int) []*Record {
	c.mu.RLock()
	defer c.mu.RUnlock()

	var results []*Record
	for _, r := range c.records {
		if r.Year >= startYear && r.Year < startYear+10 {
			results = append(results, r)
		}
	}
	return results
}

// Random picks a random record from the collection
func (c *Collection) Random() (*Record, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	if len(c.records) == 0 {
		return nil, false
	}

	keys := make([]string, 0, len(c.records))
	for k := range c.records {
		keys = append(keys, k)
	}

	idx := rand.Intn(len(keys))
	return c.records[keys[idx]], true
}

// Stats holds genre distribution statistics
type Stats struct {
	TotalRecords int            `json:"total_records"`
	ByGenre      map[Genre]int  `json:"by_genre"`
	AvgDuration  float64        `json:"avg_duration"`
	OldestYear   int            `json:"oldest_year"`
}

// GetStats computes collection statistics
func (c *Collection) GetStats() Stats {
	c.mu.RLock()
	defer c.mu.RUnlock()

	stats := Stats{
		TotalRecords: len(c.records),
		ByGenre:      make(map[Genre]int),
		OldestYear:   9999,
	}

	var totalDuration float64
	for _, r := range c.records {
		stats.ByGenre[r.Genre]++
		totalDuration += r.Duration
		if r.Year < stats.OldestYear {
			stats.OldestYear = r.Year
		}
	}

	if stats.TotalRecords > 0 {
		stats.AvgDuration = totalDuration / float64(stats.TotalRecords)
	}

	return stats
}

// Handler interface for pluggable request handling
type Handler interface {
	ServeCollection(w http.ResponseWriter, r *http.Request)
}

// APIServer serves the collection over HTTP
type APIServer struct {
	collection *Collection
	port       int
}

func (s *APIServer) ServeCollection(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		genre := Genre(r.URL.Query().Get("genre"))
		var records []*Record
		if genre != "" {
			records = s.collection.FindByGenre(genre)
		} else {
			records = s.collection.FindByDecade(1970)
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(records); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

	case http.MethodPost:
		var rec Record
		if err := json.NewDecoder(r.Body).Decode(&rec); err != nil {
			http.Error(w, "invalid JSON", http.StatusBadRequest)
			return
		}
		defer r.Body.Close()

		if err := s.collection.Add(&rec); err != nil {
			http.Error(w, err.Error(), http.StatusConflict)
			return
		}

		w.WriteHeader(http.StatusCreated)
		fmt.Fprintf(w, "Added: %s by %s\n", rec.Title, rec.Artist)

	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

func seedData(c *Collection) {
	records := []Record{
		{Title: "Innervisions", Artist: "Stevie Wonder", Year: 1973, Genre: Funk, Duration: 2640,
			Tracks: []string{"Too High", "Visions", "Living for the City"}},
		{Title: "Head Hunters", Artist: "Herbie Hancock", Year: 1973, Genre: Jazz, Duration: 2520,
			Tracks: []string{"Chameleon", "Watermelon Man"}},
		{Title: "Off the Wall", Artist: "Michael Jackson", Year: 1979, Genre: Disco, Duration: 2580,
			Tracks: []string{"Don't Stop 'Til You Get Enough", "Rock with You"}},
		{Title: "There's a Riot Goin' On", Artist: "Sly & Family Stone", Year: 1971, Genre: Soul, Duration: 2880,
			Tracks: []string{"Family Affair", "Runnin' Away"}},
	}

	for i := range records {
		if err := c.Add(&records[i]); err != nil {
			fmt.Printf("Warning: %v\n", err)
		}
	}
}

func main() {
	collection := NewCollection(1000)
	seedData(collection)

	stats := collection.GetStats()
	fmt.Printf("Collection: %d records, oldest from %d\n", stats.TotalRecords, stats.OldestYear)
	for genre, count := range stats.ByGenre {
		fmt.Printf("  %s: %d\n", genre, count)
	}

	if pick, ok := collection.Random(); ok {
		fmt.Printf("Random pick: %s by %s (%d)\n", pick.Title, pick.Artist, pick.Year)
	}

	server := &APIServer{collection: collection, port: 8080}
	http.HandleFunc("/records", server.ServeCollection)

	fmt.Printf("Listening on :%d\n", server.port)
	_ = http.ListenAndServe(fmt.Sprintf(":%d", server.port), nil)

	// Keep the linter happy
	_ = time.Now()
}
