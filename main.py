import time
import sys
from typing import List, Dict, Optional
from scraper import AvitoScraper
from html_parser import AvitoHTMLParser
from db import DatabaseManager


class AvitoBot:
    """Основной класс для парсинга Avito"""
    
    def __init__(self, db_path: str = "avito_data.db", headless: bool = True):
        """
        Инициализация бота
        
        Args:
            db_path: Путь к базе данных
            headless: Запуск браузера в фоновом режиме
        """
        self.db_manager = DatabaseManager(db_path)
        self.headless = headless
        self.target_url = "https://www.avito.ru/volgograd/kvartiry/sdam/posutochno/-ASgBAgICAkSSA8gQ8AeSUg?context=H4sIAAAAAAAA_wEjANz_YToxOntzOjg6ImZyb21QYWdlIjtzOjc6ImNhdGFsb2ciO312FITcIwAAAA&f=ASgBAgECA0SSA8gQ8AeSUqqDD5z58AIBRdDmFEQie1widmVyc2lvblwiOjEsXCJ0b3RhbENvdW50XCI6MixcImFkdWx0c0NvdW50XCI6MixcImNoaWxkcmVuXCI6W119Ig"
    
    def run(self) -> None:
        """Основной метод запуска парсинга"""
        print("Запуск парсера Avito...")
        
        try:
            with AvitoScraper(headless=self.headless) as scraper:
                # Попытка загрузить сохраненные куки
                cookies_loaded = scraper.load_cookies()
                
                # Переход на целевую страницу
                if not scraper.navigate_to_page(self.target_url):
                    print("Ошибка при переходе на страницу")
                    return
                
                # Если куки не были загружены, сохраняем их после первого запроса
                if not cookies_loaded:
                    print("Сохранение куки после первого запроса...")
                    time.sleep(3)  # Даем время для загрузки страницы
                    scraper.save_cookies()
                
                # Прокрутка страницы для загрузки всего контента
                print("Прокрутка страницы для загрузки контента...")
                scraper.scroll_to_bottom()
                
                # Получение HTML кода страницы
                html_content = scraper.get_page_source()
                
                # Парсинг данных
                apartments = self._parse_page(html_content)
                
                if apartments:
                    # Сохранение в базу данных
                    self._save_apartments(apartments)
                    print(f"Успешно сохранено {len(apartments)} объявлений")
                else:
                    print("Объявления не найдены")
                
                # Вывод статистики
                self._print_statistics()
                
        except Exception as e:
            print(f"Ошибка при выполнении парсинга: {e}")
            sys.exit(1)
    
    def _parse_page(self, html_content: str) -> List[Dict[str, Optional[str]]]:
        """
        Парсинг HTML страницы
        
        Args:
            html_content: HTML содержимое страницы
            
        Returns:
            Список объявлений
        """
        print("Парсинг HTML страницы...")
        
        parser = AvitoHTMLParser(html_content)
        apartments = parser.parse_apartments()
        
        # Получение общей статистики
        total_count = parser.get_total_count()
        if total_count:
            print(f"Общее количество объявлений на странице: {total_count}")
        
        return apartments
    
    def _save_apartments(self, apartments: List[Dict[str, Optional[str]]]) -> None:
        """
        Сохранение объявлений в базу данных
        
        Args:
            apartments: Список объявлений для сохранения
        """
        print("Сохранение данных в базу...")
        
        # Подготовка данных для массовой вставки
        apartments_data = []
        for apt in apartments:
            apartments_data.append((
                apt.get('title', ''),
                apt.get('price', ''),
                apt.get('photo_url')
            ))
        
        # Массовая вставка
        self.db_manager.insert_apartments_batch(apartments_data)
    
    def _print_statistics(self) -> None:
        """Вывод статистики по базе данных"""
        total_count = self.db_manager.get_apartments_count()
        print(f"\n=== СТАТИСТИКА ===")
        print(f"Всего объявлений в базе данных: {total_count}")
        
        # Показать последние 5 записей
        recent_apartments = self.db_manager.get_all_apartments()[:5]
        if recent_apartments:
            print(f"\nПоследние {len(recent_apartments)} объявлений:")
            for apt in recent_apartments:
                print(f"- {apt[1]} | {apt[2]} | {apt[3] or 'Нет фото'}")
    
    def show_all_data(self) -> None:
        """Показать все данные из базы"""
        apartments = self.db_manager.get_all_apartments()
        
        if not apartments:
            print("База данных пуста")
            return
        
        print(f"\n=== ВСЕ ДАННЫЕ ({len(apartments)} записей) ===")
        for apt in apartments:
            print(f"ID: {apt[0]}")
            print(f"Заголовок: {apt[1]}")
            print(f"Цена: {apt[2]}")
            print(f"Фото: {apt[3] or 'Нет фото'}")
            print(f"Дата: {apt[4]}")
            print("-" * 50)
    
    def clear_database(self) -> None:
        """Очистка базы данных"""
        self.db_manager.clear_database()
        print("База данных очищена")


def main():
    """Главная функция"""
    # print("=== ПАРСЕР AVITO.ru ===")
    # print("1. Запустить парсинг")
    # print("2. Показать все данные")
    # print("3. Очистить базу данных")
    # print("4. Выход")
    
    while True:
        try:
            print("\n=== ПАРСЕР AVITO.ru ===")
            print("1. Запустить парсинг")
            print("2. Показать все данные")
            print("3. Очистить базу данных")
            print("4. Выход")
            choice = input("\nВыберите действие (1-4): ").strip()
            
            if choice == "1":
                bot = AvitoBot(headless=True)  # Запуск в фоновом режиме
                bot.run()
            
            elif choice == "2":
                bot = AvitoBot()
                bot.show_all_data()
            
            elif choice == "3":
                confirm = input("Вы уверены? (y/N): ").strip().lower()
                if confirm == 'y':
                    bot = AvitoBot()
                    bot.clear_database()
            
            elif choice == "4":
                print("До свидания!")
                break
            
            else:
                print("Неверный выбор. Попробуйте снова.")
        
        except KeyboardInterrupt:
            print("\nПрограмма прервана пользователем")
            break
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()