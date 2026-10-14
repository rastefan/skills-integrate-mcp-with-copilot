import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException

import app


class ActivityPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.original_database_path = app.DATABASE_PATH
        self.temp_directory = tempfile.TemporaryDirectory()
        app.DATABASE_PATH = Path(self.temp_directory.name) / "activities.sqlite"
        app.initialize_database()

    def tearDown(self):
        app.DATABASE_PATH = self.original_database_path
        self.temp_directory.cleanup()

    def test_signup_survives_database_reinitialization(self):
        email = "new.student@mergington.edu"
        app.signup_for_activity("Chess Club", email)

        app.initialize_database()

        self.assertIn(email, app.get_activities()["Chess Club"]["participants"])

    def test_unregister_survives_database_reinitialization(self):
        email = "michael@mergington.edu"
        app.unregister_from_activity("Chess Club", email)

        app.initialize_database()

        self.assertNotIn(email, app.get_activities()["Chess Club"]["participants"])

    def test_duplicate_signup_and_unknown_activity_keep_existing_errors(self):
        with self.assertRaises(HTTPException) as duplicate:
            app.signup_for_activity("Chess Club", "michael@mergington.edu")
        self.assertEqual(duplicate.exception.status_code, 400)
        self.assertEqual(duplicate.exception.detail, "Student is already signed up")

        with self.assertRaises(HTTPException) as unknown:
            app.signup_for_activity("Unknown Activity", "student@mergington.edu")
        self.assertEqual(unknown.exception.status_code, 404)
        self.assertEqual(unknown.exception.detail, "Activity not found")


if __name__ == "__main__":
    unittest.main()
