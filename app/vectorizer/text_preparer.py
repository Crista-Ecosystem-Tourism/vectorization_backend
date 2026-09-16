from typing import Dict, Any, List


class TextPreparer:
    @staticmethod
    def _string_list(value: Any) -> List[str]:
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value if item is not None and str(item)]
        if value is None or value == '':
            return []
        return [str(value)]

    @classmethod
    def _categories(cls, place: Dict[str, Any]) -> List[str]:
        return cls._string_list(place.get('subcategories')) or cls._string_list(place.get('category'))

    @classmethod
    def _subtypes(cls, place: Dict[str, Any]) -> List[str]:
        return cls._string_list(place.get('subtype')) or cls._string_list(place.get('subcategory'))

    @staticmethod
    def _address(place: Dict[str, Any]) -> Dict[str, Any]:
        address = place.get('addressObj')
        if isinstance(address, dict):
            return address
        return {}

    @staticmethod
    def prepare_text(place: Dict[str, Any]) -> str:
        def safe_get(data, key, default=''):
            value = data.get(key, default)
            return str(value) if value is not None else default

        parts = [
            f"Название: {safe_get(place, 'name')}",
            f"Категории: {'; '.join(TextPreparer._categories(place))}",
        ]

        if rating := place.get('rating'):
            parts.append(f"Рейтинг: {rating} из 5 звезд")
        if reviews := place.get('numberOfReviews'):
            parts.append(f"Отзывов: {reviews}")

        if description := place.get('description'):
            parts.append(f"Описание: {str(description)}")

        if subtypes := TextPreparer._subtypes(place):
            parts.append(f"Особенности: {'; '.join(subtypes)}")

        if features := place.get('features', []):
            parts.append(f"Услуги и сервисы: {'; '.join(features)}")

        cuisines = place.get('cuisines', [])
        if cuisines:
            parts.append(f"Кухни: {'; '.join(cuisines)}")

        dietary = place.get('dietaryRestrictions', [])
        if dietary:
            parts.append(f"Диета: {'; '.join(dietary)}")

        meal_types = place.get('mealTypes', [])
        if meal_types:
            parts.append(f"Типы питания: {'; '.join(meal_types)}")

        if context := place.get('page_content'):
            parts.append(f"Контекст: {str(context)}")

        return ". ".join(parts)

    @staticmethod
    def create_metadata(place: Dict[str, Any]) -> Dict[str, Any]:
        description = place.get('description') or ''
        if len(description) > 300:
            description = description[:297] + "..."

        latitude = place.get('latitude')
        longitude = place.get('longitude')
        try:
            latitude = float(latitude) if latitude is not None else None
        except (TypeError, ValueError):
            latitude = None
        try:
            longitude = float(longitude) if longitude is not None else None
        except (TypeError, ValueError):
            longitude = None

        rating = place.get('rating')
        try:
            rating = float(rating) if rating is not None else None
        except (TypeError, ValueError):
            rating = None

        review_count = place.get('numberOfReviews')
        try:
            review_count = int(review_count) if review_count is not None else None
        except (TypeError, ValueError):
            review_count = None

        address_obj = TextPreparer._address(place)
        city = address_obj.get('city') or place.get('city') or ''
        state = address_obj.get('state') or place.get('region') or ''
        country = address_obj.get('country') or place.get('country') or ''
        postalcode = address_obj.get('postalcode', '') or ''

        return {
            'id': str(place.get('id', '')),
            'name': place.get('name', ''),
            'external_id': str(place.get('external_id', '')),
            'source': str(place.get('source', '')),
            'category': '; '.join(TextPreparer._categories(place)),
            'subtype': '; '.join(TextPreparer._subtypes(place)),
            'city': city,
            'state': state,
            'country': country,
            'postalcode': postalcode,
            'rating': rating,
            'review_count': review_count,
            'latitude': latitude,
            'longitude': longitude,
        }
