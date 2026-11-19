# Console-Based Playlist Manager

This project is a Python console application for managing music playlists.

## Login credentials
- Username: user123
- Password: Givemetheykey123

## How to run
From the project folder:

```bash
python playlist_system.py
```

Optional demo data:

```bash
python playlist_system.py --demo
```

## Features included
- User authentication with 3 failed attempts and 5-minute lockout
- Create playlists
- Add songs
- Update song details
- Rename playlists
- Remove playlists
- Remove songs
- Display all playlists and songs
- Detect duplicate songs across playlists
- Sort playlists by name
- Sort songs within a playlist
- Shuffle songs in a playlist
- Export playlists to a text file
- Import playlists from a previously exported file
- Automated test suite with 7 tests

## Test command
```bash
python -m unittest discover -s tests -q
```
