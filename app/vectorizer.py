import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from rich.console import Console
from langchain_chroma import Chroma
from app.embedding_provider import EmbeddingProvider
from app.result_renderer import ResultRenderer
from app.utils import get_logger

logger = get_logger(__name__)

class PlaceVectorizer:
    def __init__(self, persist_dir: str = './chroma_persist', embedding_provider_name: str = None, embedding_model_name: str = None):
        self.embedding_provider = EmbeddingProvider(
            provider_name=embedding_provider_name,
            model_name=embedding_model_name
        )
        self.persist_dir = persist_dir
        self.vector_store = None
        logger.info(f"Создан PlaceVectorizer с провайдером {self.embedding_provider.provider_name} и моделью {self.embedding_provider.model_name}")

    def _prepare_text(self, attraction: Dict[str, Any]) -> str:
        id = attraction.get('id', '')
        name = attraction.get('name', '')
        category = ', '.join(attraction.get('subcategories', []))
        description = attraction.get('description') or ''
        subtypes = ', '.join(attraction.get('subtypes', []))
        address = attraction.get('address', '')
        rating = attraction.get('rating', '')
        review_count = attraction.get('numberOfReviews', '')

        # Улучшенный текст с более структурированной информацией
        text_parts = [
            f"ID: {id}",
            f"Название: {name}",
            f"Категории: {category}",
            f"Адрес: {address}",
            f"Рейтинг: {rating} из 5 на основе {review_count} отзывов",
        ]
        if description:
            text_parts.append(f"Описание: {description}")
        if subtypes:
            text_parts.append(f"Типы: {subtypes}")

        return ". ".join(text_parts)

    def build_and_store_embeddings(self, attractions: List[Dict[str, Any]], batch_size=100):
        logger.info(f"Начинается создание индекса из {len(attractions)} записей")
        try:
            texts = [self._prepare_text(attr) for attr in attractions]
            metadatas = [{'id': attr.get('id'), 'name': attr.get('name')} for attr in attractions]

            # Создаем Chroma с persist_directory - данные автоматически сохраняются
            self.vector_store = Chroma(
                embedding_function=self.embedding_provider.model,
                persist_directory=self.persist_dir
            )

            # Добавляем данные батчами
            for i in tqdm(range(0, len(texts), batch_size), desc="Индексация батчей"):
                batch_texts = texts[i : i + batch_size]
                batch_metadatas = metadatas[i : i + batch_size]
                self.vector_store.add_texts(texts=batch_texts, metadatas=batch_metadatas)

            logger.info("Индекс успешно создан и сохранён")
        except Exception as e:
            logger.error(f"Ошибка при создании индекса: {e}")
            raise

    def load_vector_store(self):
        logger.info(f"Загрузка существующего векторного хранилища из {self.persist_dir}")
        try:
            self.vector_store = Chroma(
                embedding_function=self.embedding_provider.model,
                persist_directory=self.persist_dir
            )
            logger.info("Векторное хранилище успешно загружено")
        except Exception as e:
            logger.error(f"Ошибка при загрузке векторного хранилища: {e}")
            raise

    def add_new_data(self, new_attractions: List[Dict[str, Any]]):
        logger.info(f"Добавление {len(new_attractions)} новых записей в индекс")
        try:
            if not self.vector_store:
                self.load_vector_store()
            new_texts = [self._prepare_text(attr) for attr in new_attractions]
            new_metadatas = [{'id': attr.get('id'), 'name': attr.get('name')} for attr in new_attractions]
            self.vector_store.add_texts(texts=new_texts, metadatas=new_metadatas)

            logger.info("Новые записи успешно добавлены и сохранены")
        except Exception as e:
            logger.error(f"Ошибка при добавлении новых данных: {e}")
            raise

    def query(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"Выполняется поиск по запросу: '{query_text}' (top {k})")
        try:
            if not self.vector_store:
                self.load_vector_store()
            
            # Нормализация запроса
            normalized_query = query_text.lower().strip()
            
            results = self.vector_store.similarity_search(normalized_query, k=k)
            logger.info(f"Найдено результатов: {len(results)}")
            
            # Дополнительная фильтрация по релевантности
            filtered_results = []
            for doc in results:
                # Можно добавить дополнительную логику фильтрации
                filtered_results.append(doc)
                
            return filtered_results
        
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            raise


class PlaceVectorizerV2:
    def __init__(self, persist_dir: str = './chroma_persist', 
                 embedding_provider_name: str = None, 
                 embedding_model_name: str = None):
        self.embedding_provider = EmbeddingProvider(
            provider_name=embedding_provider_name,
            model_name=embedding_model_name
        )
        self.persist_dir = persist_dir
        self.vector_store = None
        logger.info(f"Создан PlaceVectorizer с провайдером {self.embedding_provider.provider_name} и моделью {self.embedding_provider.model_name}")

    def _prepare_text(self, attraction: Dict[str, Any]) -> str:
        """Улучшенная подготовка текста с обработкой None значений"""
        
        def safe_get(data, key, default=''):
            value = data.get(key, default)
            return str(value) if value is not None else default
        
        parts = [
            f"Название: {safe_get(attraction, 'name')}",
            f"Категории: {'; '.join(attraction.get('subcategories', []))}",
            # f"Адрес: {safe_get(attraction, 'address')}",
            # f"Местоположение: {safe_get(attraction, 'locationString')}",
        ]
        
        # Добавляем рейтинг и отзывы, если есть
        if rating := attraction.get('rating'):
            parts.append(f"Рейтинг: {rating} из 5 звезд")
        if reviews := attraction.get('numberOfReviews'):
            parts.append(f"Отзывов: {reviews}")

        # Добавляем описание если есть
        if description := attraction.get('description'):
            parts.append(f"Описание: {str(description)}")

        # Добавляем особенности из subtype
        if subtypes := attraction.get('subtype', []):
            parts.append(f"Особенности: {'; '.join(subtypes)}")

        # Дополнительно можно добавить популярные услуги, если есть
        if features := attraction.get('features', []):
            parts.append(f"Услуги и сервисы: {'; '.join(features)}")

        return ". ".join(parts)


    def _create_metadata(self, attraction: Dict[str, Any]) -> Dict[str, Any]:
        """Создание более структурированных и полных метаданных с безопасной обработкой"""
        
        description = attraction.get('description') or ''
        if len(description) > 300:
            description = description[:297] + "..."
        
        latitude = attraction.get('latitude')
        longitude = attraction.get('longitude')
        try:
            latitude = float(latitude) if latitude is not None else None
        except (TypeError, ValueError):
            latitude = None
        try:
            longitude = float(longitude) if longitude is not None else None
        except (TypeError, ValueError):
            longitude = None
        
        rating = attraction.get('rating')
        try:
            rating = float(rating) if rating is not None else None
        except (TypeError, ValueError):
            rating = None

        review_count = attraction.get('numberOfReviews')
        try:
            review_count = int(review_count) if review_count is not None else None
        except (TypeError, ValueError):
            review_count = None
        
        # Разбор адресной информации для лучшей фильтрации
        address_obj = attraction.get('addressObj', {})
        city = address_obj.get('city', '')
        state = address_obj.get('state', '')
        country = address_obj.get('country', '')
        postalcode = address_obj.get('postalcode', '') or ''

        # Можно извлечь дополнительную локационную информацию из ancestorLocations
        # regions = []
        # for loc in attraction.get('ancestorLocations', []):
        #     if loc.get('subcategory') in ('Регион', 'Провинция', 'Район/дистрикт'):
        #         name = loc.get('name')
        #         if name:
        #             regions.append(name)

        return {
            'id': str(attraction.get('id', '')),
            'name': attraction.get('name', ''),
            'category': '; '.join(attraction.get('subcategories', [])),
            'subtype': '; '.join(attraction.get('subtype', [])),
            # 'address': attraction.get('address', ''),
            'city': city,
            'state': state,
            'country': country,
            'postalcode': postalcode,
            # 'regions': '; '.join(regions),
            'rating': rating if rating is not None else 0.0,
            'review_count': review_count if review_count is not None else 0,
            # 'description': description,
            'latitude': latitude or 0.0,
            'longitude': longitude or 0.0,
            # 'phone': attraction.get('phone', ''),
            # 'website': attraction.get('website', ''),
        }


    def build_and_store_embeddings(self, attractions: List[Dict[str, Any]], batch_size: int = 50):
        """Создание и сохранение векторных эмбеддингов с прогресс-баром и обработкой ошибок"""
        logger.info(f"Начинается создание индекса из {len(attractions)} записей")
        
        try:
            texts = [self._prepare_text(attr) for attr in attractions]
            metadatas = [self._create_metadata(attr) for attr in attractions]

            # Создаем/загружаем Chroma с persist_directory
            self.vector_store = Chroma(
                embedding_function=self.embedding_provider.model,
                persist_directory=self.persist_dir
            )

            successful_batches = 0
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            progress_bar = tqdm(total=total_batches, desc="Индексация батчей")
            
            for i in range(0, len(texts), batch_size):
                try:
                    batch_texts = texts[i : i + batch_size]
                    batch_metadatas = metadatas[i : i + batch_size]
                    
                    self.vector_store.add_texts(
                        texts=batch_texts, 
                        metadatas=batch_metadatas
                    )
                    successful_batches += 1
                    
                except Exception as batch_error:
                    logger.warning(f"Ошибка в батче {i//batch_size + 1}: {batch_error}")
                    # Пропускаем проблемный батч и продолжаем
                    continue
                finally:
                    progress_bar.update(1)
                    progress_bar.set_postfix({
                        'success': f'{successful_batches}/{total_batches}',
                        'batch_size': batch_size
                    })
            # Попытка сохранения базы
            try:
                if hasattr(self.vector_store, "persist"):
                    self.vector_store.persist()
                logger.info(f"Данные сохранены в {self.persist_dir}")
            except Exception as e:
                logger.warning(f"Не удалось вызвать persist: {e}")

            progress_bar.close()
            
            logger.info(f"Индекс создан. Успешных батчей: {successful_batches}/{total_batches}")
            logger.info(f"Данные сохранены в {self.persist_dir}")
            
        except Exception as e:
            logger.error(f"Критическая ошибка при создании индекса: {e}")
            raise


    def load_vector_store(self):
        """Загрузка существующего векторного хранилища"""
        logger.info(f"Загрузка векторного хранилища из {self.persist_dir}")
        try:
            self.vector_store = Chroma(
                embedding_function=self.embedding_provider.model,
                persist_directory=self.persist_dir
            )
            logger.info("Векторное хранилище успешно загружено")
        except Exception as e:
            logger.error(f"Ошибка при загрузке векторного хранилища: {e}")
            raise

    def add_new_data(self, new_attractions: List[Dict[str, Any]]):
        """Добавление новых данных в индекс"""
        logger.info(f"Добавление {len(new_attractions)} новых записей")
        try:
            if not self.vector_store:
                self.load_vector_store()
                
            new_texts = [self._prepare_text(attr) for attr in new_attractions]
            new_metadatas = [self._create_metadata(attr) for attr in new_attractions]
            
            self.vector_store.add_texts(texts=new_texts, metadatas=new_metadatas)
            logger.info("Новые записи успешно добавлены")
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении новых данных: {e}")
            raise

    def query(self, query_text: str, k: int = 5, distance_threshold: float = 0.7,
            metadata_filter: dict | None = None) -> list[dict[str, Any]]:
        """
        Возвращаем distance и нормализованный relevance_score = 1 - distance.
        distance_threshold по-прежнему используется (меньше = лучше).
        """
        logger.info(f"Поиск: '{query_text}' (top {k}, distance <= {distance_threshold})")

        if not self.vector_store:
            self.load_vector_store()

        try:
            results = self.vector_store.similarity_search_with_score(
                query_text,
                k=min(k * 2, 20),
                filter=metadata_filter  # если Chroma поддерживает
            )

            filtered = []
            for doc, distance in results:
                distance = float(distance)
                similarity = max(0.0, 1.0 - distance)  # безопасная нормализация
                if distance <= distance_threshold:
                    data = {
                        **(doc.metadata or {}),
                        "distance": distance,
                        "relevance_score": similarity,
                        "page_content": getattr(doc, "page_content", "")
                    }
                    filtered.append(data)

            # сортируем по релевантности (similarity) убыванию
            filtered.sort(key=lambda x: x["relevance_score"], reverse=True)
            return filtered[:k]

        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            raise

    def query_with_filters(self, query_text: str, k: int = 5, 
                        min_rating: float = None,
                        min_reviews: int = None,
                        categories: List[str] = None,
                        location_filter: str = None,
                        max_distance: float = None,
                        target_lat: float = None,
                        target_lon: float = None,
                        distance_threshold: float = 0.9) -> List[Dict[str, Any]]:
        """Расширенный поиск с фильтрами"""
        
        # Получаем базовые результаты
        results = self.query(query_text, k=20, distance_threshold=distance_threshold)
        
        # Применяем фильтры
        filtered_results = results
        
        if min_rating is not None:
            filtered_results = [r for r in filtered_results 
                              if r['rating'] >= min_rating]
        
        if min_reviews is not None:
            filtered_results = [r for r in filtered_results 
                              if r['review_count'] >= min_reviews]
        
        if categories:
            filtered_results = [r for r in filtered_results 
                              if any(cat.lower() in r['category'].lower() for cat in categories)]
        
        if location_filter:
            filtered_results = [r for r in filtered_results 
                              if location_filter.lower() in r.get('location', '').lower()]
        
        # Фильтрация по расстоянию (если есть координаты)
        if max_distance is not None and target_lat is not None and target_lon is not None:
            filtered_results = self._filter_by_distance(
                filtered_results, float(target_lat), float(target_lon), float(max_distance)
            )

        return filtered_results[:k]

    def _filter_by_distance(self, results: List[Dict], target_lat: float, 
                           target_lon: float, max_distance_km: float) -> List[Dict]:
        """Фильтрация результатов по расстоянию"""
        filtered = []
        
        for result in results:
            lat = result.get('latitude')
            lon = result.get('longitude')
            if lat is None or lon is None:
                continue
            try:
                lat_f = float(lat)
                lon_f = float(lon)
            except (TypeError, ValueError):
                continue
            distance = self._calculate_distance(target_lat, target_lon, lat_f, lon_f)
            if distance <= max_distance_km:
                result['distance_km'] = distance
                filtered.append(result)
        
        return filtered

    def _calculate_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Вычисление расстояния между двумя точками (км)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371.0  # Радиус Земли в км
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c

    def generate_rich_response(self, query_text: str, k: int = 3, 
                              format: str = "detailed") -> Dict[str, Any]:
        """Генерация богатого ответа с анализом результатов"""
        
        results = self.query(query_text, k=k)
        
        if not results:
            return {
                "success": False,
                "message": "К сожалению, по вашему запросу ничего не найдено.",
                "suggestions": [
                    "Попробуйте изменить формулировку запроса",
                    "Уточните местоположение",
                    "Используйте более общие ключевые слова"
                ]
            }
        
        response = {
            "success": True,
            "query": query_text,
            "results_count": len(results),
            "execution_time_ms": None,
            "top_results": results,
            "summary": self._generate_summary(results),
            "analysis": self._analyze_results(results),
            "recommendations": self._generate_recommendations(results)
        }
        
        if format == "minimal":
            response["top_results"] = [{
                'name': r['name'],
                'rating': r['rating'],
                'address': r['address'],
                'relevance': r['relevance_score']
            } for r in results]
        
        return response

    def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Генерация статистической сводки с обработкой отсутствующих полей"""
        if not results:
            return {}
        
        # Безопасное извлечение рейтингов
        ratings = []
        for r in results:
            rating = r.get('rating')
            if rating is not None and isinstance(rating, (int, float)) and rating > 0:
                ratings.append(rating)
        
        # Безопасное извлечение количества отзывов
        review_counts = []
        for r in results:
            review_count = r.get('review_count')
            if review_count is not None and isinstance(review_count, (int, float)) and review_count > 0:
                review_counts.append(review_count)
        
        # Безопасное извлечение категорий
        categories = []
        for r in results:
            category = r.get('category')
            if category and isinstance(category, str):
                categories.append(category)
        
        # Безопасное извлечение локаций
        locations = []
        for r in results:
            location = r.get('location')
            if location and isinstance(location, str):
                locations.append(location)
        
        return {
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "max_rating": max(ratings) if ratings else 0,
            "total_reviews": sum(review_counts) if review_counts else 0,
            "categories": list(set(categories)),
            "top_location": max(set(locations), key=lambda x: len(x)) if locations else ""
        }

    def _analyze_results(self, results: List[Dict]) -> List[str]:
        """Анализ и извлечение инсайтов из результатов"""
        insights = []
        
        if not results:
            return insights
        
        # Анализ рейтингов
        ratings = [r['rating'] for r in results if r['rating'] > 0]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            insights.append(f"Средний рейтинг найденных мест: {avg_rating:.1f}/5")
        
        # Анализ категорий
        categories = [r['category'] for r in results]
        from collections import Counter
        category_counts = Counter(categories)
        if category_counts:
            top_category = category_counts.most_common(1)[0][0]
            insights.append(f"Наиболее частая категория: {top_category}")
        
        # Анализ местоположений
        locations = [r.get('location', '') for r in results if r.get('location')]
        if locations:
            unique_locations = len(set(locations))
            insights.append(f"Результаты из {unique_locations} различных районов")
        
        return insights

    def _generate_recommendations(self, results: List[Dict]) -> List[Dict]:
        """Генерация персонализированных рекомендаций"""
        recommendations = []
        
        for i, result in enumerate(results[:3], 1):
            rec = {
                'rank': i,
                'name': result['name'],
                'rating': result['rating'],
                'review_count': result['review_count'],
                # 'address': result['address'],
                'highlight': self._get_highlight(result),
                'why_recommended': self._get_recommendation_reason(result, i)
            }
            recommendations.append(rec)
        
        return recommendations

    def _get_highlight(self, result: Dict) -> str:
        """Выделение ключевой особенности места"""
        if result['rating'] >= 4.5:
            return "Высокий рейтинг ⭐⭐⭐⭐⭐"
        elif result['review_count'] > 100:
            return "Популярное место 🎯"
        elif 'вид' in result.get('description', '').lower() or 'панорам' in result.get('description', '').lower():
            return "Красивый вид 🌅"
        else:
            return "Интересное место 🔍"

    def _get_recommendation_reason(self, result: Dict, rank: int) -> str:
        """Обоснование рекомендации"""
        reasons = [
            f"Высокий рейтинг ({result['rating']}/5) и {result['review_count']} отзывов",
            f"Находится в удобном районе: {result.get('location', '')}",
            f"Предлагает: {result.get('subtype', 'разнообразные услуги')}",
            f"Популярное место с хорошими отзывами"
        ]
        return reasons[rank % len(reasons)]

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики по векторной базе"""
        try:
            if not self.vector_store:
                self.load_vector_store()
            
            collection = self.vector_store._collection
            if collection:
                count = collection.count()
                return {
                    "total_entries": count,
                    "persist_directory": self.persist_dir,
                    "embedding_model": self.embedding_provider.model_name,
                    "collection_size": f"{count} объектов"
                }
            return {"error": "Collection not available"}
            
        except Exception as e:
            return {"error": str(e)}

    def clear_index(self):
        """Очистка векторного индекса"""
        try:
            import shutil
            import os
            if os.path.exists(self.persist_dir):
                shutil.rmtree(self.persist_dir)
                logger.info(f"Индекс в {self.persist_dir} очищен")
            else:
                logger.warning(f"Директория {self.persist_dir} не существует")
        except Exception as e:
            logger.error(f"Ошибка при очистке индекса: {e}")
            raise

    def pretty_print_results(self, response, style: str = "rich"):
        """
        Красивый вывод результатов
        Styles: 'rich', 'table', 'minimal', 'map'
        """
        # Проверяем тип response - может быть как Dict, так и List
        if isinstance(response, list):
            # Если передали просто список результатов
            results = response
            response = {
                "success": len(results) > 0,
                "message": f"Найдено {len(results)} результатов" if results else "Ничего не найдено",
                "results_count": len(results),
                "top_results": results
            }
        
        # Теперь response гарантированно Dict
        if not response.get('success', False):
            print(f"❌ {response.get('message', 'Ничего не найдено')}")
            return

        results = response.get('top_results', [])
        
        if style == "table":
            ResultRenderer.print_table_view(results, f"Результаты: {response['query']}")
        elif style == "minimal":
            ResultRenderer.print_minimal_view(results)
        elif style == "map":
            ResultRenderer.print_map_view(results)
        else:
            ResultRenderer.print_rich_response(response)

        # Дополнительная информация
        if len(results) > 0:
            print(f"\n📊 Найдено {len(results)} результатов (релевантность: {results[0]['relevance_score']:.3f})")

    def interactive_search(self):
        """Интерактивный режим поиска"""
        console = Console()
        
        while True:
            query = console.input("\n[bold cyan]🔍 Введите запрос (или 'quit' для выхода): [/bold cyan]")
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query.strip():
                continue
                
            try:
                response = self.generate_rich_response(query, k=5)
                self.pretty_print_results(response)
                
                # Предложить варианты экспорта
                if response.get('success') and response.get('results_count', 0) > 0:
                    export = console.input("\n💾 Сохранить результаты? (y/n): ")
                    if export.lower() == 'y':
                        filename = f"results_{query[:20]}.json".replace(' ', '_')
                        ResultRenderer.save_to_json(response, filename)
                        
            except Exception as e:
                console.print(f"[red]❌ Ошибка: {e}[/red]")
