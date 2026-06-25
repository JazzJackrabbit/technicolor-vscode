use std::collections::HashMap;
use std::fmt;
use std::sync::{Arc, Mutex};

/// Represents a music genre from the 70s era
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Genre {
    Funk,
    Soul,
    Disco,
    Jazz,
    Reggae,
}

impl fmt::Display for Genre {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Genre::Funk => write!(f, "Funk"),
            Genre::Soul => write!(f, "Soul"),
            Genre::Disco => write!(f, "Disco"),
            Genre::Jazz => write!(f, "Jazz"),
            Genre::Reggae => write!(f, "Reggae"),
        }
    }
}

/// A single vinyl record
#[derive(Debug, Clone)]
pub struct Record {
    pub title: String,
    pub artist: String,
    pub year: u16,
    pub genre: Genre,
    pub side_a: Vec<String>,
    pub side_b: Vec<String>,
    pub rating: Option<f32>,
}

impl Record {
    pub fn new(title: &str, artist: &str, year: u16, genre: Genre) -> Self {
        Self {
            title: title.to_string(),
            artist: artist.to_string(),
            year,
            genre,
            side_a: Vec::new(),
            side_b: Vec::new(),
            rating: None,
        }
    }

    pub fn with_tracks(mut self, side_a: Vec<&str>, side_b: Vec<&str>) -> Self {
        self.side_a = side_a.into_iter().map(String::from).collect();
        self.side_b = side_b.into_iter().map(String::from).collect();
        self
    }

    pub fn with_rating(mut self, rating: f32) -> Self {
        self.rating = Some(rating.clamp(0.0, 5.0));
        self
    }

    pub fn total_tracks(&self) -> usize {
        self.side_a.len() + self.side_b.len()
    }

    pub fn is_from_decade(&self, decade_start: u16) -> bool {
        self.year >= decade_start && self.year < decade_start + 10
    }
}

impl fmt::Display for Record {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let rating = self
            .rating
            .map(|r| format!(" [{:.1}/5]", r))
            .unwrap_or_default();
        write!(
            f,
            "{} - {} ({}, {}){}",
            self.artist, self.title, self.year, self.genre, rating
        )
    }
}

/// Errors that can occur in the crate
#[derive(Debug, thiserror::Error)]
pub enum CrateError {
    #[error("collection is full (max {max} records)")]
    CollectionFull { max: usize },

    #[error("record not found: {0}")]
    NotFound(String),

    #[error("invalid rating: {0} (must be 0.0-5.0)")]
    InvalidRating(f32),

    #[error("lock poisoned")]
    LockPoisoned,
}

/// Trait for anything that can be searched
pub trait Searchable {
    fn matches(&self, query: &str) -> bool;
}

impl Searchable for Record {
    fn matches(&self, query: &str) -> bool {
        let q = query.to_lowercase();
        self.title.to_lowercase().contains(&q)
            || self.artist.to_lowercase().contains(&q)
            || self.genre.to_string().to_lowercase().contains(&q)
    }
}

/// Thread-safe vinyl collection
pub struct Collection {
    records: Arc<Mutex<Vec<Record>>>,
    max_size: usize,
}

impl Collection {
    pub fn new(max_size: usize) -> Self {
        Self {
            records: Arc::new(Mutex::new(Vec::with_capacity(max_size))),
            max_size,
        }
    }

    pub fn add(&self, record: Record) -> Result<(), CrateError> {
        let mut records = self.records.lock().map_err(|_| CrateError::LockPoisoned)?;

        if records.len() >= self.max_size {
            return Err(CrateError::CollectionFull { max: self.max_size });
        }

        records.push(record);
        Ok(())
    }

    pub fn find<F>(&self, predicate: F) -> Result<Vec<Record>, CrateError>
    where
        F: Fn(&Record) -> bool,
    {
        let records = self.records.lock().map_err(|_| CrateError::LockPoisoned)?;
        Ok(records.iter().filter(|r| predicate(r)).cloned().collect())
    }

    pub fn search(&self, query: &str) -> Result<Vec<Record>, CrateError> {
        self.find(|r| r.matches(query))
    }

    pub fn by_genre(&self, genre: &Genre) -> Result<Vec<Record>, CrateError> {
        self.find(|r| &r.genre == genre)
    }

    pub fn by_decade(&self, start: u16) -> Result<Vec<Record>, CrateError> {
        self.find(|r| r.is_from_decade(start))
    }

    pub fn stats(&self) -> Result<CollectionStats, CrateError> {
        let records = self.records.lock().map_err(|_| CrateError::LockPoisoned)?;

        let mut by_genre: HashMap<Genre, usize> = HashMap::new();
        let mut total_rating = 0.0_f32;
        let mut rated_count = 0_usize;
        let mut oldest: Option<u16> = None;

        for record in records.iter() {
            *by_genre.entry(record.genre.clone()).or_insert(0) += 1;

            if let Some(rating) = record.rating {
                total_rating += rating;
                rated_count += 1;
            }

            oldest = Some(oldest.map_or(record.year, |o: u16| o.min(record.year)));
        }

        Ok(CollectionStats {
            total: records.len(),
            by_genre,
            avg_rating: if rated_count > 0 {
                Some(total_rating / rated_count as f32)
            } else {
                None
            },
            oldest_year: oldest,
        })
    }
}

impl Clone for Collection {
    fn clone(&self) -> Self {
        Self {
            records: Arc::clone(&self.records),
            max_size: self.max_size,
        }
    }
}

/// Statistics about a collection
#[derive(Debug)]
pub struct CollectionStats {
    pub total: usize,
    pub by_genre: HashMap<Genre, usize>,
    pub avg_rating: Option<f32>,
    pub oldest_year: Option<u16>,
}

impl fmt::Display for CollectionStats {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "Collection: {} records", self.total)?;
        for (genre, count) in &self.by_genre {
            writeln!(f, "  {}: {}", genre, count)?;
        }
        if let Some(avg) = self.avg_rating {
            writeln!(f, "  Avg rating: {:.1}/5", avg)?;
        }
        if let Some(year) = self.oldest_year {
            writeln!(f, "  Oldest: {}", year)?;
        }
        Ok(())
    }
}

/// Macro for quickly creating records
macro_rules! record {
    ($title:expr, $artist:expr, $year:expr, $genre:expr) => {
        Record::new($title, $artist, $year, $genre)
    };
    ($title:expr, $artist:expr, $year:expr, $genre:expr, rating: $r:expr) => {
        Record::new($title, $artist, $year, $genre).with_rating($r)
    };
}

fn main() {
    let collection = Collection::new(1000);

    let seed_records = vec![
        record!("Innervisions", "Stevie Wonder", 1973, Genre::Funk, rating: 4.8),
        record!("Head Hunters", "Herbie Hancock", 1973, Genre::Jazz, rating: 4.5)
            .with_tracks(vec!["Chameleon", "Watermelon Man"], vec!["Sly", "Vein Melter"]),
        record!("Off the Wall", "Michael Jackson", 1979, Genre::Disco, rating: 4.7),
        record!("There's a Riot Goin' On", "Sly & Family Stone", 1971, Genre::Soul),
        record!("Catch a Fire", "Bob Marley & The Wailers", 1973, Genre::Reggae, rating: 4.6),
        record!("Saturday Night Fever", "Bee Gees", 1977, Genre::Disco, rating: 4.2),
    ];

    for record in seed_records {
        if let Err(e) = collection.add(record) {
            eprintln!("Error adding record: {}", e);
        }
    }

    // Print stats
    match collection.stats() {
        Ok(stats) => print!("{}", stats),
        Err(e) => eprintln!("Error: {}", e),
    }

    // Search
    let query = "stevie";
    match collection.search(query) {
        Ok(results) => {
            println!("\nSearch '{}': {} results", query, results.len());
            for r in &results {
                println!("  {}", r);
            }
        }
        Err(e) => eprintln!("Search error: {}", e),
    }

    // By decade
    match collection.by_decade(1970) {
        Ok(seventies) => {
            println!("\n70s records:");
            for r in &seventies {
                println!("  {} ({} tracks)", r, r.total_tracks());
            }
        }
        Err(e) => eprintln!("Error: {}", e),
    }

    // Clone collection (shares Arc)
    let backup = collection.clone();
    let funk = backup.by_genre(&Genre::Funk).unwrap_or_default();
    println!("\nFunk records in backup: {}", funk.len());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_record_creation() {
        let r = Record::new("Test", "Artist", 1975, Genre::Funk);
        assert_eq!(r.title, "Test");
        assert_eq!(r.year, 1975);
        assert!(r.rating.is_none());
    }

    #[test]
    fn test_rating_clamping() {
        let r = Record::new("Test", "Artist", 1975, Genre::Funk).with_rating(10.0);
        assert_eq!(r.rating, Some(5.0));
    }

    #[test]
    fn test_decade_check() {
        let r = Record::new("Test", "Artist", 1975, Genre::Funk);
        assert!(r.is_from_decade(1970));
        assert!(!r.is_from_decade(1980));
    }

    #[test]
    fn test_collection_full() {
        let col = Collection::new(1);
        col.add(Record::new("A", "B", 1970, Genre::Funk)).unwrap();
        let err = col.add(Record::new("C", "D", 1971, Genre::Soul));
        assert!(matches!(err, Err(CrateError::CollectionFull { max: 1 })));
    }

    #[test]
    fn test_search() {
        let col = Collection::new(10);
        col.add(Record::new("Innervisions", "Stevie Wonder", 1973, Genre::Funk))
            .unwrap();
        let results = col.search("stevie").unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].artist, "Stevie Wonder");
    }
}
