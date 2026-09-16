import os
import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException

from app.security import require_import_admin
from app.utils.data_loader import DataLoader


class ImportSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_dir = os.environ.get("VECTORIZATION_IMPORT_DIR")
        self.previous_hosts = os.environ.get("VECTORIZATION_IMPORT_URL_ALLOWLIST")
        os.environ["VECTORIZATION_IMPORT_DIR"] = self.temp_dir.name
        os.environ["VECTORIZATION_IMPORT_URL_ALLOWLIST"] = "datasets.example.org"

    def tearDown(self):
        if self.previous_dir is None:
            os.environ.pop("VECTORIZATION_IMPORT_DIR", None)
        else:
            os.environ["VECTORIZATION_IMPORT_DIR"] = self.previous_dir
        if self.previous_hosts is None:
            os.environ.pop("VECTORIZATION_IMPORT_URL_ALLOWLIST", None)
        else:
            os.environ["VECTORIZATION_IMPORT_URL_ALLOWLIST"] = self.previous_hosts
        self.temp_dir.cleanup()

    def test_json_import_accepts_only_filename_in_allowlisted_directory(self):
        allowed = Path(self.temp_dir.name) / "places.json"
        allowed.write_text("[]", encoding="utf-8")

        self.assertEqual(DataLoader().load_from_json("places.json"), [])
        with self.assertRaises(ValueError):
            DataLoader().load_from_json("../secrets.json")

    def test_api_import_rejects_unallowlisted_hosts_before_a_request(self):
        with self.assertRaises(ValueError):
            DataLoader().load_from_api("https://localhost/private.json")
        with self.assertRaises(ValueError):
            DataLoader().load_from_api("http://datasets.example.org/places.json")

    def test_import_auth_is_disabled_without_an_admin_token(self):
        previous_token = os.environ.pop("VECTORIZATION_ADMIN_TOKEN", None)
        try:
            with self.assertRaises(HTTPException) as exc:
                require_import_admin(None)
        finally:
            if previous_token is not None:
                os.environ["VECTORIZATION_ADMIN_TOKEN"] = previous_token
        self.assertEqual(exc.exception.status_code, 503)
