import os
import json
from app.vectorizer import PlaceVectorizer
from app.data_loader import DataLoader
import shutil

def test_recreate_vector_db():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'test_attractions.json')
    persist_path = os.path.join(os.path.dirname(__file__), 'chroma_persist')

    # Удаляем старую базу, пересоздаём заново
    if os.path.exists(persist_path):
        shutil.rmtree(persist_path)

    loader = DataLoader()
    data = loader.load_from_json(json_path)
    assert data, "Не удалось загрузить данные из JSON"

    vectorizer = PlaceVectorizer(persist_dir=persist_path)
    vectorizer.build_and_store_embeddings(data)

    # Проверяем, что папка с persisted данными появилась
    assert os.path.exists(persist_path), "Папка с векторной базой не создана"

    print("Тест пересоздания векторной базы прошёл успешно")

if __name__ == "__main__":
    test_recreate_vector_db()
