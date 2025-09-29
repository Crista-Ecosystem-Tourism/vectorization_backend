import statistics

from typing import List, Dict, Any
from collections import Counter, defaultdict


class DatasetQualityAnalyzer:
    def __init__(self, dataset: List[Any]):
        self.dataset = dataset
        self.total = len([item for item in dataset if isinstance(item, dict)])

    def analyze(self) -> Dict[str, float]:
        if self.total == 0:
            return {}

        fields = [
            'description',
            'rating',
            # 'numberOfReviews',
            'address',
            'website',
            'phone',
            'subcategories',
            'subtype',
            'latitude',
            'longitude',
        ]

        coverage = {field: 0 for field in fields}
        field_lengths = {field: [] for field in fields}  # для длины текста или значений

        review_thresholds = [5, 10, 50, 100, 500, 999]
        review_counts = {threshold: 0 for threshold in review_thresholds}

        # Гистограмма по конкретным рейтингам 1..5
        rating_distribution = {rating: 0 for rating in range(1, 6)}

        for item in self.dataset:
            if not isinstance(item, dict):
                continue
            for field in fields:
                value = item.get(field)
                if value:
                    if isinstance(value, (str, list)) and len(value) == 0:
                        continue
                    coverage[field] += 1
                    if isinstance(value, str):
                        field_lengths[field].append(len(value))
                    elif isinstance(value, (int, float)):
                        field_lengths[field].append(float(value))
                    elif isinstance(value, list):
                        field_lengths[field].append(len(value))

            num_reviews = item.get('numberOfReviews')
            try:
                num_reviews_val = int(num_reviews)
            except (TypeError, ValueError):
                num_reviews_val = 0

            for threshold in review_thresholds:
                if num_reviews_val > threshold:
                    review_counts[threshold] += 1

            rating = item.get('rating')
            if isinstance(rating, (int, float)):
                rating_rounded = int(round(rating))
                if rating_rounded in rating_distribution:
                    rating_distribution[rating_rounded] += 1

        coverage_percent = {field: (count / self.total) * 100 for field, count in coverage.items()}
        coverage_percent['total_items'] = self.total

        print(f"Отчёт о качестве данных (всего объектов: {self.total}):\n")
        max_bar_len = 80
        for field in fields:
            percent = coverage_percent[field]
            print(f"{field:15}: {percent:6.2f}% | ", end='')
            bar_len = int(percent / 100 * max_bar_len)
            bar = "█" * bar_len
            print(bar.ljust(max_bar_len))

        max_bar_len = 40
        print("\nРаспределение по рейтингу (округлено до целого):")
        max_rating_count = max(rating_distribution.values()) if rating_distribution else 1
        for rating in range(5, 0, -1):
            count = rating_distribution[rating]
            percent = (count / self.total) * 100
            bar_len = int(count / max_rating_count * max_bar_len)
            bar = "█" * bar_len
            print(f"Рейтинг {rating}: {percent:6.2f}% | {bar}")

        return coverage_percent
    
    def analyze_review_counts(self):
        """
        Анализирует распределение по количеству отзывов с красивым форматированием.
        """
        from collections import defaultdict
        exact_reviews = list(range(0, 6))
        thresholds = [5, 50, 100, 500, 1000]
        exact_counts = defaultdict(int)
        threshold_counts = defaultdict(int)

        for item in self.dataset:
            if not isinstance(item, dict):
                continue
            num_reviews = item.get('numberOfReviews')
            try:
                num_reviews_val = int(num_reviews)
            except (TypeError, ValueError):
                num_reviews_val = 0

            if num_reviews_val in exact_reviews:
                exact_counts[num_reviews_val] += 1
            for t in thresholds:
                if num_reviews_val > t:
                    threshold_counts[t] += 1

        total = self.total
        max_bar_len = 40
        max_exact = max(exact_counts.values()) if exact_counts else 1
        max_thr = max(threshold_counts.values()) if threshold_counts else 1

        print("\nРаспределение по точному количеству отзывов (0–5):")
        for n in exact_reviews:
            count = exact_counts[n]
            percent = count / total * 100 if total > 0 else 0
            bar_len = int(count / max_exact * max_bar_len)
            bar = "█" * bar_len
            print(
                f"Мест с {str(n).rjust(2)} отзывов: {str(count).rjust(4)} {percent:6.2f}% "
                f"{bar.ljust(max_bar_len)}"
            )

        print("\nРаспределение по порогам (больше ...):")
        for t in thresholds:
            count = threshold_counts[t]
            percent = count / total * 100 if total > 0 else 0
            bar_len = int(count / max_thr * max_bar_len)
            bar = "█" * bar_len
            print(
                f"Мест с больше {str(t).rjust(4)} отзывов: {str(count).rjust(4)} {percent:6.2f}% "
                f"{bar.ljust(max_bar_len)}"
            )

        return {
            'exact_counts': dict(exact_counts),
            'threshold_counts': dict(threshold_counts)
        }

    def analyze_categories(self, field_name: str = 'subcategories', top_n: int = 20):
        """
        Анализирует распределение категорий или подкатегорий по полю field_name
        и выводит топ-N наиболее частых категорий с диаграммой.
        """
        categories_list = []

        for item in self.dataset:
            if not isinstance(item, dict):
                continue
            categories = item.get(field_name)
            if categories:
                if isinstance(categories, list):
                    categories_list.extend(categories)
                elif isinstance(categories, str):
                    categories_list.append(categories)

        counter = Counter(categories_list)
        most_common = counter.most_common(top_n)

        # Печать результирующей гистограммы
        total = sum(counter.values())
        max_len = max(len(name) for name, _ in most_common) if most_common else 10
        max_bar_len = 40

        print(f"\nТоп-{top_n} категорий по полю '{field_name}':")
        for name, count in most_common:
            percent = (count / total) * 100 if total > 0 else 0
            bar_len = int(count / total * max_bar_len) if total > 0 else 0
            bar = "█" * bar_len
            print(f"{name.ljust(max_len)} | {percent:6.2f}% | {bar} {count}")

        return dict(most_common)
    
    def analyze_subtypes(self, top_n: int = 20):
        """
        Анализирует распределение подтипов по полю 'subtype'
        и выводит топ-N наиболее частых подтипов с диаграммой.
        """
        subtypes_list = []

        for item in self.dataset:
            if not isinstance(item, dict):
                continue
            subtypes = item.get('subtype')
            if subtypes:
                if isinstance(subtypes, list):
                    subtypes_list.extend(subtypes)
                elif isinstance(subtypes, str):
                    subtypes_list.append(subtypes)

        from collections import Counter
        counter = Counter(subtypes_list)
        most_common = counter.most_common(top_n)

        total = sum(counter.values())
        max_len = max((len(name) for name, _ in most_common), default=10)
        max_bar_len = 40

        print(f"\nТоп-{top_n} подтипов (subtype):")
        for name, count in most_common:
            percent = (count / total) * 100 if total > 0 else 0
            bar_len = int(count / total * max_bar_len) if total > 0 else 0
            bar = "█" * bar_len
            print(f"{name.ljust(max_len)} | {percent:6.2f}% | {bar} {count}")

        return dict(most_common)

    def analyze_vectorizer_text_length_ranges(self, text_preparer):
        texts = [text_preparer.prepare_text(item) for item in self.dataset if isinstance(item, dict)]

        char_lengths = [len(text) for text in texts]

        def stats(data):
            return {
                'min': min(data),
                'avg_min': statistics.mean(sorted(data)[:max(1, len(data)//10)]),
                'avg': statistics.mean(data),
                'avg_max': statistics.mean(sorted(data)[-max(1, len(data)//10):]),
                'max': max(data)
            }

        char_stats = stats(char_lengths)

        # Высчитываем пороговые точки с +-15%
        def bound(val):
            return (val * 0.85, val * 1.15)

        min_low, min_high = bound(char_stats['min'])
        avg_min_low, avg_min_high = bound(char_stats['avg_min'])
        avg_low, avg_high = bound(char_stats['avg'])
        avg_max_low, avg_max_high = bound(char_stats['avg_max'])
        max_low, max_high = bound(char_stats['max'])

        bins = [
            ('Очень маленькие',             float('-inf'),         min_low),
            ('Маленькие',                  min_high,              avg_min_low),
            ('Ниже среднего',              avg_min_high,          avg_low),
            ('Средние',                   avg_high,              avg_max_low),
            ('Выше среднего',              avg_max_high,          max_low),
            ('Очень большие',              max_high,              float('inf')),
        ]

        counts = defaultdict(int)
        for length in char_lengths:
            for name, low, high in bins:
                if low <= length <= high:
                    counts[name] += 1
                    break

        max_count = max(counts.values()) if counts else 1

        def make_bar(count, max_count, width=40):
            bar_len = int(count / max_count * width) if max_count > 0 else 0
            return "█" * bar_len

        print("\nАнализ длины текстов с распределением по детальным диапазонам:\n")
        print(f"{'Категория':15} | {'кол-во символов':15} | {'кол-во':6} | {'гистограмма':40}")
        print("-" * 95)

        def range_str(low, high):
            low_s = f"{int(low)}" if low != float('-inf') else "-∞"
            high_s = f"{int(high)}" if high != float('inf') else "∞"
            return f"{low_s} - {high_s}"

        for name, low, high in bins:
            count = counts[name]
            bar = make_bar(count, max_count)
            print(f"{name.ljust(15)} | {range_str(low, high).ljust(15)} | {str(count).rjust(6)} | {bar.ljust(40)}")

        print(f"\nВсего элементов в датасете: {len(char_lengths)}")

        return {
            'char_stats': char_stats,
            'bins': bins,
            'counts': counts,
        }

    def _print_histogram(self, data: List[Any], percent: float = None, width: int = 40):
        if percent is not None:
            # строить по проценту заполнения
            bar_len = int(percent / 100 * width)
            bar = "█" * bar_len
            print(f"{bar.ljust(width)}")
            return
        if not data:
            print("(пусто)")
            return
        try:
            import numpy as np
            hist, _ = np.histogram(data, bins=width)
            max_count = max(hist) if max(hist) > 0 else 1
            for count in hist:
                bar_len = int(count / max_count * width)
                print("█" * bar_len, end='')
            print()
        except ImportError:
            print("(требуется numpy для гистограммы)")
