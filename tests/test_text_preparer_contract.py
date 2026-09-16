"""Contract shared by data_backend's normalized records and vectorization."""

import unittest
from unittest.mock import MagicMock

from app.vectorizer.text_preparer import TextPreparer
from app.vectorizer.vector_store_manager import VectorStoreManager


class TextPreparerContractTests(unittest.TestCase):
    def test_normalized_place_keeps_geography_category_and_description(self):
        record = {
            "id": "place-1",
            "external_id": "node/1",
            "source": "osm",
            "name": "Красная площадь",
            "category": "attraction",
            "subcategory": "viewpoint",
            "city": "Москва",
            "region": "Москва",
            "country": "RU",
            "latitude": 55.7539,
            "longitude": 37.6208,
            "description": "Главная площадь Москвы",
            "page_content": "Красная площадь. Главная площадь Москвы",
        }

        text = TextPreparer.prepare_text(record)
        metadata = TextPreparer.create_metadata(record)

        self.assertIn("attraction", text)
        self.assertIn("Главная площадь Москвы", text)
        self.assertEqual(metadata["city"], "Москва")
        self.assertEqual(metadata["state"], "Москва")
        self.assertEqual(metadata["country"], "RU")
        self.assertEqual(metadata["category"], "attraction")
        self.assertEqual(metadata["subtype"], "viewpoint")
        self.assertEqual(metadata["source"], "osm")
        self.assertEqual(metadata["external_id"], "node/1")
        self.assertEqual(metadata["latitude"], 55.7539)
        self.assertEqual(metadata["longitude"], 37.6208)

    def test_legacy_nested_record_remains_compatible(self):
        record = {
            "id": "place-2",
            "name": "Эрмитаж",
            "subcategories": ["culture"],
            "subtype": ["museum"],
            "addressObj": {"city": "Санкт-Петербург", "state": "СПб", "country": "RU"},
        }

        metadata = TextPreparer.create_metadata(record)

        self.assertEqual(metadata["city"], "Санкт-Петербург")
        self.assertEqual(metadata["category"], "culture")
        self.assertEqual(metadata["subtype"], "museum")

    def test_vector_store_uses_stable_ids_for_upsert(self):
        store = MagicMock()
        manager = object.__new__(VectorStoreManager)
        manager.vector_store = store

        manager.add_texts(
            ["Красная площадь"],
            [{"id": "place-1", "city": "Москва", "latitude": None}],
            ["place-1"],
        )

        store.add_texts.assert_called_once_with(
            texts=["Красная площадь"],
            metadatas=[{"id": "place-1", "city": "Москва"}],
            ids=["place-1"],
        )


if __name__ == "__main__":
    unittest.main()
