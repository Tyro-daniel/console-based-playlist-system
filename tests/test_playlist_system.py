import tempfile
import unittest
from pathlib import Path

from playlist_system import AuthenticationSystem, PlaylistManager, Song


class AuthenticationSystemTests(unittest.TestCase):
    def test_valid_login_succeeds(self):
        auth = AuthenticationSystem()
        result, message = auth.attempt_login("user123", "Givemetheykey123")
        self.assertTrue(result)
        self.assertIn("Login successful", message)

    def test_invalid_login_reduces_attempts_and_locks_after_three_failures(self):
        auth = AuthenticationSystem()

        for _ in range(2):
            result, _ = auth.attempt_login("wrong", "wrong")
            self.assertFalse(result)

        result, message = auth.attempt_login("wrong", "wrong")
        self.assertFalse(result)
        self.assertIn("locked", message.lower())
        self.assertTrue(auth.is_locked())


class PlaylistManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = PlaylistManager()
        self.manager.create_playlist("Chill")
        self.manager.add_song_to_playlist("Chill", Song("Sunset", "Nova Bloom", "Pop"))
        self.manager.add_song_to_playlist("Chill", Song("Midnight Drive", "Blue Echo", "Jazz"))

    def test_add_song_to_playlist(self):
        self.manager.add_song_to_playlist("Chill", Song("Dreams", "Nova Bloom", "Indie"))
        self.assertEqual(len(self.manager.playlists["Chill"].songs), 3)

    def test_change_song_details_updates_existing_song(self):
        result = self.manager.change_song_in_playlist("Chill", "Sunset", "Golden Hour", "Nova Bloom", "Synth")
        self.assertTrue(result)
        updated_song = self.manager.get_playlist("Chill").songs[0]
        self.assertEqual(updated_song.name, "Golden Hour")
        self.assertEqual(updated_song.genre, "Synth")

    def test_remove_playlist_removes_related_songs(self):
        self.manager.create_playlist("Workout")
        self.manager.add_song_to_playlist("Workout", Song("Run", "Luca", "Electronic"))
        self.manager.remove_playlist("Workout")
        self.assertNotIn("Workout", self.manager.playlists)

    def test_find_duplicate_songs_reports_playlists_with_repeated_song(self):
        self.manager.create_playlist("Road Trip")
        self.manager.add_song_to_playlist("Road Trip", Song("Sunset", "Nova Bloom", "Pop"))
        duplicates = self.manager.find_duplicate_songs()
        self.assertIn(("sunset", "nova bloom", "pop"), duplicates)
        self.assertIn("Chill", duplicates[("sunset", "nova bloom", "pop")])
        self.assertIn("Road Trip", duplicates[("sunset", "nova bloom", "pop")])

    def test_export_playlists_creates_export_file(self):
        temp_dir = tempfile.TemporaryDirectory()
        export_path = Path(temp_dir.name) / "playlist_export.txt"
        self.manager.export_playlists(export_path)

        self.assertTrue(export_path.exists())
        content = export_path.read_text(encoding="utf-8")
        self.assertIn("Playlist: Chill", content)
        self.assertIn("Sunset", content)
        temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
