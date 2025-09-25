import os
import json
from app.vectorizer import PlaceVectorizer
from app.data_loader import DataLoader

def test_local_json_vectorizing():
    # Путь к тестовомуjson
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'test_attractions.json')
    
    # Загрузка данных
    loader = DataLoader()
    data = loader.load_from_json(json_path)
    assert data, "Не удалось загрузить данные из JSON"
    
    # Создание и индексирование векторной базы
    vectorizer = PlaceVectorizer(persist_dir='./tests/chroma_persist')
    vectorizer.build_and_store_embeddings(data)
    
    # Проверка запроса
    query_text = "фонтан Сочи"
    results = vectorizer.query(query_text, k=3)
    
    print(f"Найдено результатов по запросу '{query_text}': {len(results)}")
    for doc in results:
        print(f" - {doc.metadata.get('name')} (id: {doc.metadata.get('id')})")

if __name__ == "__main__":
    test_local_json_vectorizing()
