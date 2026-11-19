"""Console-based music playlist sorter and manager.

This module contains the full assignment solution for a secure, menu-driven
playlist management system. It uses object-oriented design to keep the code
organised, documented, and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class Song:
    """Represents a single song in a playlist."""

    name: str
    singer: str
    genre: str

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.singer = self.singer.strip()
        self.genre = self.genre.strip()

    @property
    def identity_key(self) -> Tuple[str, str, str]:
        """Return a case-insensitive identity key for duplicate detection."""
        return (self.name.lower(), self.singer.lower(), self.genre.lower())

    def format_for_display(self) -> str:
        """Return a compact string used in the console and export file."""
        return f"{self.name} - {self.singer} ({self.genre})"


@dataclass
class Playlist:
    """Represents a playlist and the songs stored inside it."""

    name: str
    songs: List[Song] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = self.name.strip()

    def add_song(self, song: Song) -> None:
        """Add a song to the playlist."""
        self.songs.append(song)

    def remove_song_by_name(self, song_name: str) -> bool:
        """Remove the first song with a matching name in a case-insensitive way."""
        for index, song in enumerate(self.songs):
            if song.name.lower() == song_name.strip().lower():
                del self.songs[index]
                return True
        return False

    def update_song(self, song_name: str, new_name: str, new_singer: str, new_genre: str) -> bool:
        """Update matching song details in the playlist."""
        for song in self.songs:
            if song.name.lower() == song_name.strip().lower():
                song.name = new_name.strip()
                song.singer = new_singer.strip()
                song.genre = new_genre.strip()
                return True
        return False

    def sort_songs_by_name(self) -> None:
        """Sort playlist songs in ascending order by song name."""
        self.songs.sort(key=lambda song: song.name.lower())

    def shuffle_songs(self) -> None:
        """Randomly shuffle the songs in the playlist."""
        random.shuffle(self.songs)

    def get_song_names(self) -> List[str]:
        """Return all song names in the playlist."""
        return [song.name for song in self.songs]


class PlaylistManager:
    """High-level controller for playlist creation, modification, and export."""

    def __init__(self) -> None:
        self.playlists: Dict[str, Playlist] = {}

    def create_playlist(self, name: str) -> Playlist:
        """Create a new playlist if it does not already exist."""
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Playlist name cannot be empty.")
        if cleaned_name.lower() in {key.lower() for key in self.playlists}:
            raise ValueError(f"Playlist '{cleaned_name}' already exists.")

        playlist = Playlist(cleaned_name)
        self.playlists[cleaned_name] = playlist
        return playlist

    def rename_playlist(self, old_name: str, new_name: str) -> None:
        """Rename an existing playlist."""
        original_name = old_name.strip()
        replacement_name = new_name.strip()

        if not original_name or not replacement_name:
            raise ValueError("Playlist names cannot be empty.")

        if original_name not in self.playlists:
            raise ValueError(f"Playlist '{original_name}' does not exist.")
        if replacement_name.lower() in {key.lower() for key in self.playlists if key.lower() != original_name.lower()}:
            raise ValueError(f"Playlist '{replacement_name}' already exists.")

        playlist = self.playlists.pop(original_name)
        playlist.name = replacement_name
        self.playlists[replacement_name] = playlist

    def remove_playlist(self, name: str) -> bool:
        """Delete a playlist and all the songs it contains."""
        cleaned_name = name.strip()
        if cleaned_name in self.playlists:
            del self.playlists[cleaned_name]
            return True
        return False

    def add_song_to_playlist(self, playlist_name: str, song: Song) -> None:
        """Add a song to an existing playlist."""
        playlist = self.get_playlist(playlist_name)
        playlist.add_song(song)

    def change_song_in_playlist(
        self,
        playlist_name: str,
        song_name: str,
        new_name: str,
        new_singer: str,
        new_genre: str,
    ) -> bool:
        """Update the details for a specific song in a playlist."""
        playlist = self.get_playlist(playlist_name)
        return playlist.update_song(song_name, new_name, new_singer, new_genre)

    def remove_song_from_playlist(self, playlist_name: str, song_name: str) -> bool:
        """Remove a song from the named playlist."""
        playlist = self.get_playlist(playlist_name)
        return playlist.remove_song_by_name(song_name)

    def get_playlist(self, name: str) -> Playlist:
        """Return a playlist object by name."""
        cleaned_name = name.strip()
        for playlist_name, playlist in self.playlists.items():
            if playlist_name.lower() == cleaned_name.lower():
                return playlist
        raise ValueError(f"Playlist '{cleaned_name}' does not exist.")

    def list_playlists_sorted(self) -> List[str]:
        """List playlist names in ascending alphabetical order."""
        return sorted(self.playlists.keys(), key=str.lower)

    def find_duplicate_songs(self) -> Dict[Tuple[str, str, str], List[str]]:
        """Detect songs repeated across one or more playlists.

        The duplicate key is based on the song name, singer and genre. The
        returned dictionary maps that key to a unique list of playlists where the
        same song appears at least twice.
        """
        occurrences: Dict[Tuple[str, str, str], List[str]] = {}

        for playlist_name, playlist in self.playlists.items():
            for song in playlist.songs:
                key = song.identity_key
                occurrences.setdefault(key, []).append(playlist_name)

        duplicates: Dict[Tuple[str, str, str], List[str]] = {}
        for key, playlist_names in occurrences.items():
            if len(playlist_names) > 1:
                duplicates[key] = sorted(set(playlist_names), key=str.lower)

        return duplicates

    def export_playlists(self, file_path: str | Path) -> str:
        """Export all playlist data into a readable text file."""
        export_path = Path(file_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)

        lines: List[str] = []
        for playlist_name in self.list_playlists_sorted():
            playlist = self.playlists[playlist_name]
            lines.append(f"Playlist: {playlist.name}")
            if not playlist.songs:
                lines.append("  No songs in this playlist.")
            else:
                for song in playlist.songs:
                    lines.append(f"  - {song.name} | {song.singer} | {song.genre}")
            lines.append("")

        export_path.write_text("\n".join(lines), encoding="utf-8")
        return str(export_path)

    def import_playlists_from_file(self, file_path: str | Path) -> None:
        """Import playlist data that was exported by export_playlists()."""
        import_path = Path(file_path)
        if not import_path.exists():
            raise FileNotFoundError(f"File '{import_path}' does not exist.")

        current_playlist_name: Optional[str] = None
        for raw_line in import_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("Playlist:"):
                current_playlist_name = line.replace("Playlist:", "", 1).strip()
                if current_playlist_name and current_playlist_name not in self.playlists:
                    self.create_playlist(current_playlist_name)
                continue
            if line.startswith("-"):
                if current_playlist_name is None:
                    continue
                song_part = line[1:].strip()
                parts = [part.strip() for part in song_part.split("|")]
                if len(parts) != 3:
                    continue
                song_name, singer, genre = parts
                self.add_song_to_playlist(current_playlist_name, Song(song_name, singer, genre))


class AuthenticationSystem:
    """Handle login, validation, and temporary lockout behaviour."""

    VALID_USERNAME = "user123"
    VALID_PASSWORD = "Givemetheykey123"
    MAX_FAILED_ATTEMPTS = 3
    LOCKOUT_DURATION = timedelta(minutes=5)

    def __init__(self) -> None:
        self.failed_attempts = 0
        self.locked_until: Optional[datetime] = None

    def is_locked(self, now: Optional[datetime] = None) -> bool:
        """Check whether the user account is currently locked."""
        current_time = now or datetime.now()
        if self.locked_until is not None and current_time < self.locked_until:
            return True
        if self.locked_until is not None and current_time >= self.locked_until:
            self.locked_until = None
            self.failed_attempts = 0
        return False

    def attempt_login(self, username: str, password: str) -> Tuple[bool, str]:
        """Attempt to authenticate the user and return success plus a message."""
        now = datetime.now()
        if self.is_locked(now):
            return False, "Account is locked. Please wait 5 minutes before trying again."

        if username == self.VALID_USERNAME and password == self.VALID_PASSWORD:
            self.failed_attempts = 0
            self.locked_until = None
            return True, "Login successful."

        self.failed_attempts += 1
        if self.failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.locked_until = now + self.LOCKOUT_DURATION
            return False, "Invalid username or password. You have reached 3 failed attempts and your account is now locked for 5 minutes."
        remaining = self.MAX_FAILED_ATTEMPTS - self.failed_attempts
        return False, f"Invalid username or password. {remaining} attempt(s) remaining."


class PlaylistApp:
    """Console-based application to manage playlists and songs."""

    def __init__(self, use_demo_data: bool = False) -> None:
        self.auth_system = AuthenticationSystem()
        self.playlist_manager = PlaylistManager()
        self._demo_data_loaded = False
        if use_demo_data:
            self.load_demo_data()

    def load_demo_data(self) -> None:
        """Populate the application with sample data for demonstration purposes."""
        if self._demo_data_loaded:
            return

        self.playlist_manager.create_playlist("Chill Mix")
        self.playlist_manager.add_song_to_playlist("Chill Mix", Song("Sunset", "Nova Bloom", "Pop"))
        self.playlist_manager.add_song_to_playlist("Chill Mix", Song("Midnight Drive", "Blue Echo", "Jazz"))

        self.playlist_manager.create_playlist("Workout")
        self.playlist_manager.add_song_to_playlist("Workout", Song("Fire", "Apex", "Electronic"))
        self.playlist_manager.add_song_to_playlist("Workout", Song("Run It", "Speed Lane", "Dance"))

        self._demo_data_loaded = True

    def login(self) -> bool:
        """Prompt the user to log in and keep asking until access is granted or locked."""
        print("\n=== Playlist Authentication ===")
        while True:
            if self.auth_system.is_locked():
                print("Your account is locked. Please wait 5 minutes before trying again.")
                return False
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            success, message = self.auth_system.attempt_login(username, password)
            print(message)
            if success:
                print("Access granted. Welcome to the playlist manager.")
                return True

    def display_menu(self) -> None:
        """Print the main menu for the console interface."""
        print("\n=== Playlist Management System ===")
        print("1. Create a playlist")
        print("2. Add a song to a playlist")
        print("3. Change song details")
        print("4. Rename a playlist")
        print("5. Remove a playlist")
        print("6. Remove a song from a playlist")
        print("7. Display all playlists")
        print("8. Find duplicate songs")
        print("9. Sort playlists by name")
        print("10. Sort songs in a playlist by name")
        print("11. Shuffle songs in a playlist")
        print("12. Export playlists to a text file")
        print("13. Load playlists from a file")
        print("14. Quit")

    def _prompt_for_song(self) -> Song:
        """Collect song details from user input."""
        name = input("Song name: ").strip()
        singer = input("Singer name: ").strip()
        genre = input("Genre: ").strip()
        if not name or not singer or not genre:
            raise ValueError("Song name, singer and genre cannot be empty.")
        return Song(name, singer, genre)

    def create_playlist_menu(self) -> None:
        """Create a playlist through the console."""
        name = input("Enter playlist name: ").strip()
        try:
            self.playlist_manager.create_playlist(name)
            print(f"Playlist '{name}' created successfully.")
        except ValueError as exc:
            print(f"Error: {exc}")

    def add_song_menu(self) -> None:
        """Add a song to a playlist."""
        playlist_name = input("Playlist name: ").strip()
        try:
            song = self._prompt_for_song()
            self.playlist_manager.add_song_to_playlist(playlist_name, song)
            print(f"Song '{song.name}' added successfully to '{playlist_name}'.")
        except ValueError as exc:
            print(f"Error: {exc}")

    def change_song_menu(self) -> None:
        """Update song details for an existing playlist."""
        playlist_name = input("Playlist name: ").strip()
        song_name = input("Current song name to change: ").strip()
        new_name = input("New song name: ").strip()
        new_singer = input("New singer name: ").strip()
        new_genre = input("New genre: ").strip()

        try:
            updated = self.playlist_manager.change_song_in_playlist(
                playlist_name,
                song_name,
                new_name,
                new_singer,
                new_genre,
            )
            if updated:
                print(f"Song '{song_name}' updated in '{playlist_name}'.")
            else:
                print(f"Song '{song_name}' was not found in '{playlist_name}'.")
        except ValueError as exc:
            print(f"Error: {exc}")

    def rename_playlist_menu(self) -> None:
        """Rename a playlist from the menu."""
        old_name = input("Current playlist name: ").strip()
        new_name = input("New playlist name: ").strip()
        try:
            self.playlist_manager.rename_playlist(old_name, new_name)
            print(f"Playlist renamed from '{old_name}' to '{new_name}'.")
        except ValueError as exc:
            print(f"Error: {exc}")

    def remove_playlist_menu(self) -> None:
        """Remove a playlist and all its songs."""
        name = input("Playlist name to remove: ").strip()
        removed = self.playlist_manager.remove_playlist(name)
        if removed:
            print(f"Playlist '{name}' removed successfully.")
        else:
            print(f"Playlist '{name}' was not found.")

    def remove_song_menu(self) -> None:
        """Remove a song from a playlist."""
        playlist_name = input("Playlist name: ").strip()
        song_name = input("Song name to remove: ").strip()
        try:
            removed = self.playlist_manager.remove_song_from_playlist(playlist_name, song_name)
            if removed:
                print(f"Song '{song_name}' removed from '{playlist_name}'.")
            else:
                print(f"Song '{song_name}' not found in '{playlist_name}'.")
        except ValueError as exc:
            print(f"Error: {exc}")

    def display_playlists(self) -> None:
        """Display all playlists and song lists in a readable format."""
        if not self.playlist_manager.playlists:
            print("No playlists have been created yet.")
            return

        for playlist_name in self.playlist_manager.list_playlists_sorted():
            playlist = self.playlist_manager.playlists[playlist_name]
            print(f"\nPlaylist: {playlist.name}")
            if not playlist.songs:
                print("  No songs in this playlist.")
                continue
            for index, song in enumerate(playlist.songs, start=1):
                print(f"  {index}. {song.format_for_display()}")

    def duplicate_song_menu(self) -> None:
        """Display playlists that contain duplicate songs."""
        duplicates = self.playlist_manager.find_duplicate_songs()
        if not duplicates:
            print("No duplicate songs were found.")
            return

        print("Duplicate songs found:")
        for key, playlist_names in duplicates.items():
            song_name, singer, genre = key
            print(f"- {song_name.title()} by {singer.title()} ({genre.title()}) in: {', '.join(playlist_names)}")

    def sort_playlists_menu(self) -> None:
        """Sort all playlist names alphabetically and display them."""
        sorted_names = self.playlist_manager.list_playlists_sorted()
        if not sorted_names:
            print("No playlists available to sort.")
            return
        print("Playlist order (ascending):")
        for index, name in enumerate(sorted_names, start=1):
            print(f"  {index}. {name}")

    def sort_songs_menu(self) -> None:
        """Sort songs in a selected playlist by name."""
        playlist_name = input("Playlist name: ").strip()
        try:
            playlist = self.playlist_manager.get_playlist(playlist_name)
            playlist.sort_songs_by_name()
            print(f"Songs in '{playlist_name}' sorted by name.")
            for index, song in enumerate(playlist.songs, start=1):
                print(f"  {index}. {song.format_for_display()}")
        except ValueError as exc:
            print(f"Error: {exc}")

    def shuffle_songs_menu(self) -> None:
        """Shuffle the songs in a selected playlist."""
        playlist_name = input("Playlist name: ").strip()
        try:
            playlist = self.playlist_manager.get_playlist(playlist_name)
            playlist.shuffle_songs()
            print(f"Songs in '{playlist_name}' have been shuffled.")
            for index, song in enumerate(playlist.songs, start=1):
                print(f"  {index}. {song.format_for_display()}")
        except ValueError as exc:
            print(f"Error: {exc}")

    def export_playlists_menu(self) -> None:
        """Export the playlists to a text file."""
        file_name = input("Enter file path to export to: ").strip() or "playlists_export.txt"
        try:
            path = self.playlist_manager.export_playlists(file_name)
            print(f"Playlists exported successfully to '{path}'.")
        except OSError as exc:
            print(f"Error writing export file: {exc}")

    def import_playlists_menu(self) -> None:
        """Import playlists from a text file using the export format."""
        file_name = input("Enter export file path to import: ").strip()
        try:
            self.playlist_manager.import_playlists_from_file(file_name)
            print(f"Playlists imported successfully from '{file_name}'.")
        except (FileNotFoundError, OSError, ValueError) as exc:
            print(f"Error importing playlists: {exc}")

    def run(self) -> None:
        """Run the main application loop."""
        if not self.login():
            print("Application closed because the user did not log in successfully.")
            return

        while True:
            self.display_menu()
            option = input("Select an option: ").strip()

            if option == "1":
                self.create_playlist_menu()
            elif option == "2":
                self.add_song_menu()
            elif option == "3":
                self.change_song_menu()
            elif option == "4":
                self.rename_playlist_menu()
            elif option == "5":
                self.remove_playlist_menu()
            elif option == "6":
                self.remove_song_menu()
            elif option == "7":
                self.display_playlists()
            elif option == "8":
                self.duplicate_song_menu()
            elif option == "9":
                self.sort_playlists_menu()
            elif option == "10":
                self.sort_songs_menu()
            elif option == "11":
                self.shuffle_songs_menu()
            elif option == "12":
                self.export_playlists_menu()
            elif option == "13":
                self.import_playlists_menu()
            elif option == "14":
                print("Goodbye.")
                break
            else:
                print("Invalid option. Please choose a number from the menu.")


def main() -> None:
    """Entry point for the application."""
    import sys

    use_demo_data = "--demo" in sys.argv
    app = PlaylistApp(use_demo_data=use_demo_data)
    app.run()


if __name__ == "__main__":
    main()
