import os
import json
from app.vectorizer import PlaceVectorizerV2
from app.data_loader import DataLoader

def test_local_json_vectorizing():
    # Путь к тестовомуjson
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'data.json')
    
    # Загрузка данных
    loader = DataLoader()
    data = loader.load_from_json(json_path)
    assert data, "Не удалось загрузить данные из JSON"
    
    # Создание и индексирование векторной базы
    vectorizer = PlaceVectorizerV2(
        persist_dir='./tests/v2/sochi_rests_and_piter_chroma_db',
        # embedding_provider_name='huggingface',
        # embedding_model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    )
    vectorizer.build_and_store_embeddings(data)

    # Богатый поиск
    response = vectorizer.generate_rich_response(
        "ресторан с видом на море",
        k=3,
        format="detailed"
    )
    vectorizer.pretty_print_results(response, style="rich")

    # Получение статистики
    stats = vectorizer.get_stats()
    print(f"Всего объектов в базе: {stats['total_entries']}")

if __name__ == "__main__":
    test_local_json_vectorizing()
