import os
from app.vectorizer import PlaceVectorizer

def test_query_existing_vector_db():
    persist_path = os.path.join(os.path.dirname(__file__), 'chroma_persist')

    vectorizer = PlaceVectorizer(persist_dir=persist_path)
    vectorizer.load_vector_store()

    query_text = "ресторан с свежими устрицами и видом на море"
    # query_text = "пляж с ресторанами и кафе"
    # query_text = "торговый центр с развлечениями для детей"
    query_text = "мне нужны рестораны возле моря, акварпарк, торговый центр с детской площадкой и зоопарки"
    query_text = "рестораны винные"
    results = vectorizer.query(query_text, k=20)

    assert results, "По запросу не найдено результатов"
    print(f"По запросу '{query_text}' найдено {len(results)} результатов")
    for doc in results:
        print(f" - {doc.metadata.get('name')}")

if __name__ == "__main__":
    test_query_existing_vector_db()
