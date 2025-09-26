from typing import List, Dict, Any
import json
from pprint import pprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED
from rich import print as rprint

console = Console()

class ResultRenderer:
    @staticmethod
    def print_rich_response(response: Dict[str, Any]):
        """Красивый вывод богатого ответа"""
        if not response.get('success', False):
            console.print(Panel(
                f"[red]❌ {response.get('message', 'Ошибка')}[/red]",
                title="Результат поиска",
                border_style="red"
            ))
            return

        # Заголовок
        console.print(Panel.fit(
            f"[bold green]✅ Найдено {response['results_count']} результатов по запросу:[/bold green]\n"
            f"[cyan]\"{response['query']}\"[/cyan]",
            title="🎯 Поиск мест",
            border_style="green"
        ))

        # Сводка
        if 'summary' in response:
            summary = response['summary']
            console.print(Panel(
                f"📊 [bold]Статистика:[/bold]\n"
                f"• Средний рейтинг: [yellow]{summary.get('avg_rating', 0)}/5[/yellow]\n"
                f"• Максимальный рейтинг: [gold1]{summary.get('max_rating', 0)}/5[/gold1]\n"
                f"• Всего отзывов: [blue]{summary.get('total_reviews', 0)}[/blue]\n"
                f"• Категории: [magenta]{', '.join(summary.get('categories', []))}[/magenta]",
                title="📈 Общая информация",
                border_style="blue"
            ))

        # Топ результаты
        console.print("\n[bold underline]🏆 Топ результаты:[/bold underline]")
        for i, result in enumerate(response['top_results'][:3], 1):
            ResultRenderer._print_single_result(result, i)

        # Рекомендации
        if 'recommendations' in response:
            console.print("\n[bold underline]💡 Рекомендации:[/bold underline]")
            for rec in response['recommendations']:
                console.print(f"• [green]{rec['name']}[/green] - {rec.get('highlight', '')}")
                console.print(f"  [dim]{rec.get('why_recommended', '')}[/dim]")

        # Инсайты
        if 'analysis' in response:
            console.print("\n[bold underline]🔍 Инсайты:[/bold underline]")
            for insight in response['analysis']:
                console.print(f"• {insight}")

    @staticmethod
    def _print_single_result(result: Dict[str, Any], rank: int):
        """Вывод одного результата"""
        # Эмодзи для рейтинга
        rating_emoji = "⭐" * int(result.get('rating', 0))
        if result.get('rating', 0) >= 4.5:
            rating_emoji = "🌟" + rating_emoji[1:]

        panel = Panel(
            f"[bold cyan]{result.get('name', 'Без названия')}[/bold cyan]\n\n"
            f"{rating_emoji} [yellow]{result.get('rating', 'N/A')}/5[/yellow] "
            f"([blue]{result.get('review_count', 0)} отзывов[/blue])\n"
            f"📍 [green]{result.get('address', 'Адрес не указан')}[/green]\n"
            f"🎯 [magenta]{result.get('category', 'Категория не указана')}[/magenta]\n"
            f"📝 {result.get('description', 'Описание отсутствует')[:100]}...\n"
            f"🔗 Релевантность: [red]{result.get('relevance_score', 0):.3f}[/red]",
            title=f"#{rank}",
            border_style="cyan" if rank == 1 else "blue",
            subtitle=f"🚀 {result.get('subtype', '')}" if result.get('subtype') else None
        )
        console.print(panel)

    @staticmethod
    def print_table_view(results: List[Dict[str, Any]], title: str = "Результаты поиска"):
        """Табличное представление результатов"""
        table = Table(title=title, box=ROUNDED, show_header=True, header_style="bold magenta")
        
        table.add_column("#", style="dim", width=4)
        table.add_column("Название", style="cyan", no_wrap=True)
        table.add_column("Рейтинг", justify="center", style="yellow")
        table.add_column("Отзывы", justify="right", style="blue")
        table.add_column("Адрес", style="green")
        table.add_column("Релевантность", justify="center", style="red")

        for i, result in enumerate(results, 1):
            rating_str = f"{result.get('rating', 0):.1f} ⭐" if result.get('rating') else "N/A"
            reviews_str = str(result.get('review_count', 0))
            relevance_str = f"{result.get('relevance_score', 0):.3f}"

            table.add_row(
                str(i),
                result.get('name', 'Без названия')[:30],
                rating_str,
                reviews_str,
                result.get('address', '')[:25],
                relevance_str
            )

        console.print(table)

    @staticmethod
    def print_minimal_view(results: List[Dict[str, Any]]):
        """Минималистичный вывод"""
        for i, result in enumerate(results, 1):
            pprint(result)
            console.print(
                f"[bold]{i}. {result.get('name', 'Без названия')}[/bold]\n"
                f"   ⭐ {result.get('rating', 'N/A')}/5 | "
                f"📝 {result.get('review_count', 0)} отзывов | "
                f"📍 {result.get('address', '')}\n"
                f"   [dim]{result.get('category', '')}[/dim]"
            )
    
    @staticmethod
    def return_as_json(results: List[Dict[str, Any]]):
        return json.dumps(results, ensure_ascii=False, indent=2)

    @staticmethod
    def print_map_view(results: List[Dict[str, Any]]):
        """Вывод с гео-информацией"""
        console.print(Panel("[bold]🗺️ Географическое распределение:[/bold]", border_style="green"))
        
        for result in results:
            if result.get('latitude') and result.get('longitude'):
                console.print(
                    f"• [cyan]{result.get('name')}[/cyan] - "
                    f"🌐 {result.get('latitude'):.4f}, {result.get('longitude'):.4f} | "
                    f"📍 {result.get('location', '')}"
                )

    @staticmethod
    def save_to_json(response: Dict[str, Any], filename: str = "search_results.json"):
        """Сохранение результатов в JSON файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        console.print(f"[green]💾 Результаты сохранены в {filename}[/green]")

    @staticmethod
    def print_export_options(results: List[Dict[str, Any]]):
        """Вывод опций экспорта"""
        console.print("\n[bold]📤 Опции экспорта:[/bold]")
        console.print("1. 💾 Сохранить в JSON")
        console.print("2. 📋 Копировать в буфер обмена")
        console.print("3. 🗺️ Показать на карте")
        console.print("4. 📊 Создать отчет")