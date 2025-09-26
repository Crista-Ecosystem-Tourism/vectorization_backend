from typing import Dict, Any, List


class TextPreparer:
    @staticmethod
    def prepare_text(place: Dict[str, Any]) -> str:
        def safe_get(data, key, default=''):
            value = data.get(key, default)
            return str(value) if value is not None else default

        parts = [
            f"Название: {safe_get(place, 'name')}",
            f"Категории: {'; '.join(place.get('subcategories', []))}",
        ]

        if rating := place.get('rating'):
            parts.append(f"Рейтинг: {rating} из 5 звезд")
        if reviews := place.get('numberOfReviews'):
            parts.append(f"Отзывов: {reviews}")

        if description := place.get('description'):
            parts.append(f"Описание: {str(description)}")

        if subtypes := place.get('subtype', []):
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

        address_obj = place.get('addressObj', {})
        city = address_obj.get('city', '')
        state = address_obj.get('state', '')
        country = address_obj.get('country', '')
        postalcode = address_obj.get('postalcode', '') or ''

        return {
            'id': str(place.get('id', '')),
            'name': place.get('name', ''),
            'category': '; '.join(place.get('subcategories', [])),
            'subtype': '; '.join(place.get('subtype', [])),
            'city': city,
            'state': state,
            'country': country,
            'postalcode': postalcode,
            'rating': rating if rating is not None else 0.0,
            'review_count': review_count if review_count is not None else 0,
            'latitude': latitude or 0.0,
            'longitude': longitude or 0.0,
        }
