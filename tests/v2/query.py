import os
from app.vectorizer import PlaceVectorizerV2

def test_query_existing_vector_db():
    persist_path = os.path.join(os.path.dirname(__file__), 'sochi_piter_chroma_db')

    vectorizer = PlaceVectorizerV2(
        persist_dir=persist_path,
        # embedding_provider_name='huggingface',
        # embedding_model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    )
    vectorizer.load_vector_store()

    docs = vectorizer.vector_store.get()
    texts = docs.get('documents') or docs.get('texts')  # ключ зависит от версии
    metadatas = docs.get('metadatas')

    # Выводим первые 15 документов
    # from pprint import pprint
    # for i, (text, meta) in enumerate(zip(texts[:15], metadatas[:15])):
    #     print(f"Док {i} — Текст:")
    #     pprint(text)
    #     print("Метаданные:")
    #     pprint(meta)
    #     print('-' * 40)

    # Тест с параметром distance_threshold
    # for i in range(1, 10):
    #     print(f"\nТест c параметром distance_threshold = {0.1*i*3}\n")
    #     response = vectorizer.query(
    #         "пицца",
    #         k=5,
    #         distance_threshold=0.1*i*3
    #     )
    #     vectorizer.pretty_print_results(response, style="minimal")


    optimal_distance_threshold = 1.5

    # Тест 
    response = vectorizer.query(
        "Найти места для активного отдыха у моря, включая пляжи, лодочные туры и зоопарки.",
        k=15,
        distance_threshold=optimal_distance_threshold
    )
    vectorizer.pretty_print_results(response, style="minimal")

    # Тест c параметром metadata_filter
    response = vectorizer.query(
        "Сочи",
        k=5,
        distance_threshold=optimal_distance_threshold,
        metadata_filter={"category": "Природа и парки"}
    )
    vectorizer.pretty_print_results(response, style="minimal")

    response = vectorizer.query(
        "Санкт-Петербург",
        k=5,
        distance_threshold=optimal_distance_threshold,
        metadata_filter={"category": "Природа и парки"}
    )
    vectorizer.pretty_print_results(response, style="minimal")


    # Тест с несколькими запросами
    test_queries = [
        "фонтан музыкальный",
        "музей сочи",
        "музей санкт-петербург",
        "памятник сочи",
        "памятник петербург",
    ]

    for query in test_queries:
        results = vectorizer.query(query, k=5, distance_threshold=optimal_distance_threshold)
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.get('name')} {result.get('description')} (score: {result.get('relevance_score', 0):.3f})")
            # print(f"      Категория: {result.get('category')}")
        print()


    # Получение статистики
    stats = vectorizer.get_stats()
    print(f"Всего объектов в базе: {stats['total_entries']}")

if __name__ == "__main__":
    test_query_existing_vector_db()
