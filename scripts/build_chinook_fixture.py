from pathlib import Path
import sqlite3

OUT = Path(__file__).resolve().parents[1] / "data" / "public" / "chinook" / "chinook_fixture.sqlite"
OUT.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE Artist(ArtistId INTEGER PRIMARY KEY, Name TEXT);
CREATE TABLE Album(AlbumId INTEGER PRIMARY KEY, Title TEXT, ArtistId INTEGER NOT NULL,
    FOREIGN KEY(ArtistId) REFERENCES Artist(ArtistId));
CREATE TABLE Genre(GenreId INTEGER PRIMARY KEY, Name TEXT);
CREATE TABLE MediaType(MediaTypeId INTEGER PRIMARY KEY, Name TEXT);
CREATE TABLE Track(TrackId INTEGER PRIMARY KEY, Name TEXT, AlbumId INTEGER, MediaTypeId INTEGER,
    GenreId INTEGER, Composer TEXT, Milliseconds INTEGER, Bytes INTEGER, UnitPrice REAL,
    FOREIGN KEY(AlbumId) REFERENCES Album(AlbumId),
    FOREIGN KEY(MediaTypeId) REFERENCES MediaType(MediaTypeId),
    FOREIGN KEY(GenreId) REFERENCES Genre(GenreId));
CREATE TABLE Customer(CustomerId INTEGER PRIMARY KEY, FirstName TEXT, LastName TEXT, Country TEXT);
CREATE TABLE Invoice(InvoiceId INTEGER PRIMARY KEY, CustomerId INTEGER, InvoiceDate TEXT, Total REAL,
    FOREIGN KEY(CustomerId) REFERENCES Customer(CustomerId));
CREATE TABLE InvoiceLine(InvoiceLineId INTEGER PRIMARY KEY, InvoiceId INTEGER, TrackId INTEGER, UnitPrice REAL, Quantity INTEGER,
    FOREIGN KEY(InvoiceId) REFERENCES Invoice(InvoiceId), FOREIGN KEY(TrackId) REFERENCES Track(TrackId));
CREATE TABLE Playlist(PlaylistId INTEGER PRIMARY KEY, Name TEXT);
CREATE TABLE PlaylistTrack(PlaylistId INTEGER, TrackId INTEGER,
    PRIMARY KEY(PlaylistId, TrackId),
    FOREIGN KEY(PlaylistId) REFERENCES Playlist(PlaylistId),
    FOREIGN KEY(TrackId) REFERENCES Track(TrackId));
CREATE TABLE Employee(EmployeeId INTEGER PRIMARY KEY, FirstName TEXT, LastName TEXT, Title TEXT);
"""

ARTISTS = [(1,"AC/DC"),(2,"Accept"),(3,"Aerosmith"),(4,"Alanis Morissette"),(5,"Audioslave"),(6,"Black Sabbath")]
ALBUMS = [(1,"For Those About To Rock",1),(2,"Balls to the Wall",2),(3,"Restless and Wild",2),(4,"Big Ones",3),(5,"Audioslave",5),(6,"Paranoid",6)]
GENRES = [(1,"Rock"),(2,"Metal"),(3,"Alternative & Punk"),(4,"Jazz")]
MEDIAS = [(1,"MPEG audio file"),(2,"Protected AAC audio file")]
TRACKS = [
    (1,"For Those About To Rock",1,1,1,"Angus Young",343719,11170334,0.99),
    (2,"Put The Finger On You",1,1,1,"Angus Young",205662,6713451,0.99),
    (3,"Balls to the Wall",2,1,2,"Accept",342562,5510427,0.99),
    (4,"Fast As a Shark",3,1,2,"Accept",230619,3990994,0.99),
    (5,"Love In An Elevator",4,1,1,"Aerosmith",321227,5322782,0.99),
    (6,"Walk On Water",4,2,3,"Aerosmith",280000,4500000,1.29),
    (7,"Cochise",5,1,3,"Chris Cornell",222380,3800000,0.99),
    (8,"Like a Stone",5,1,3,"Chris Cornell",294320,5100000,0.99),
    (9,"Paranoid",6,1,2,"Tony Iommi",168000,3000000,0.99),
    (10,"War Pigs",6,1,2,"Black Sabbath",446000,7800000,0.99),
]
CUSTOMERS = [
    (1,"Ada","Lovelace","Canada"),(2,"Alan","Turing","United Kingdom"),(3,"Grace","Hopper","USA"),
    (4,"Linus","Torvalds","Finland"),(5,"Margaret","Hamilton","USA"),(6,"Tim","Berners-Lee","United Kingdom"),
]
INVOICES = [(1,1,"2024-01-05",10.00),(2,1,"2024-02-07",6.00),(3,2,"2024-02-20",12.00),(4,3,"2024-03-11",8.00),(5,5,"2024-04-02",18.00),(6,6,"2024-05-08",5.00)]
INVOICE_LINES = [(1,1,1,0.99,1),(2,1,3,0.99,2),(3,2,5,0.99,2),(4,3,8,0.99,3),(5,4,9,0.99,1),(6,5,10,0.99,4),(7,6,2,0.99,1)]
PLAYLISTS = [(1,"Rock Classics"),(2,"Metal Essentials"),(3,"Alternative Mix")]
PLAYLIST_TRACKS = [(1,1),(1,2),(1,5),(2,3),(2,4),(2,9),(2,10),(3,6),(3,7),(3,8)]
EMPLOYEES = [(1,"Andrew","Adams","General Manager"),(2,"Nancy","Edwards","Sales Support Agent")]

if OUT.exists():
    OUT.unlink()
conn = sqlite3.connect(OUT)
conn.executescript(SCHEMA)
for table, rows in {
    "Artist": ARTISTS, "Album": ALBUMS, "Genre": GENRES, "MediaType": MEDIAS,
    "Track": TRACKS, "Customer": CUSTOMERS, "Invoice": INVOICES,
    "InvoiceLine": INVOICE_LINES, "Playlist": PLAYLISTS, "PlaylistTrack": PLAYLIST_TRACKS,
    "Employee": EMPLOYEES,
}.items():
    placeholders = ",".join(["?"] * len(rows[0]))
    conn.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
conn.commit()
conn.close()
print(OUT)
