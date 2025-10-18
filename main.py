import time
import sys
from typing import List, Dict, Optional
from scraper import AvitoScraper
from html_parser import AvitoHTMLParser
from db import DatabaseManager
from datetime import datetime


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
        """Основной метод запуска двухэтапного парсинга"""
        print("=" * 60)
        print("ЗАПУСК ПАРСЕРА AVITO (ДВУХЭТАПНЫЙ РЕЖИМ)")
        print("=" * 60)
        
        try:
            # Этап 1: Сбор ссылок на объявления
            print("\n[ЭТАП 1] Сбор ссылок на объявления...")
            links_count = self._collect_apartment_links()
            
            if links_count == 0:
                print("Новые ссылки не найдены")
                return
            
            print(f"✓ Собрано новых ссылок: {links_count}")
            
            # Этап 2: Парсинг детальных страниц
            print("\n[ЭТАП 2] Парсинг детальных страниц объявлений...")
            parsed_count = self._parse_apartment_details()
            
            print(f"\n✓ Обработано объявлений: {parsed_count}")
            
            # Вывод статистики
            self._print_statistics()
            
        except KeyboardInterrupt:
            print("\n\nПарсинг прерван пользователем")
            self._print_statistics()
        except Exception as e:
            print(f"\nОшибка при выполнении парсинга: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _collect_apartment_links(self) -> int:
        """
        Этап 1: Сбор ссылок на объявления со страницы каталога
        
        Returns:
            Количество новых добавленных ссылок
        """
        with AvitoScraper(headless=self.headless) as scraper:
            # Попытка загрузить сохраненные куки
            cookies_loaded = scraper.load_cookies()
            
            # Переход на целевую страницу
            print(f"Переход на страницу каталога...")
            if not scraper.navigate_to_page(self.target_url):
                print("✗ Ошибка при переходе на страницу")
                return 0
            
            # Если куки не были загружены, сохраняем их
            if not cookies_loaded:
                print("Сохранение куки...")
                time.sleep(3)
                scraper.save_cookies()
            
            # Прокрутка страницы для загрузки всего контента
            print("Прокрутка страницы...")
            scraper.scroll_to_bottom()
            
            # Получение HTML кода страницы
            html_content = scraper.get_page_source()
            
            # Парсинг ссылок
            parser = AvitoHTMLParser(html_content)
            links = parser.parse_apartment_links()
            
            if not links:
                print("✗ Ссылки не найдены")
                return 0
            
            # Сохранение ссылок в базу данных
            new_links_count = self.db_manager.insert_apartment_links_batch(links)
            
            return new_links_count
    
    def _parse_apartment_details(self) -> int:
        """
        Этап 2: Парсинг детальных страниц объявлений
        
        Returns:
            Количество обработанных объявлений
        """
        # Получение непарсенных ссылок
        unparsed_links = self.db_manager.get_unparsed_links()
        
        if not unparsed_links:
            print("Нет непарсенных ссылок")
            return 0
        
        total = len(unparsed_links)
        print(f"Найдено непарсенных ссылок: {total}")
        
        parsed_count = 0
        failed_count = 0
        
        with AvitoScraper(headless=self.headless) as scraper:
            # Загрузка куки
            scraper.load_cookies()
            
            for idx, (link_id, url) in enumerate(unparsed_links, 1):
                try:
                    # Прогресс
                    progress = (idx / total) * 100
                    print(f"\n[{idx}/{total}] ({progress:.1f}%) Парсинг: {url}")
                    
                    # Переход на страницу объявления
                    if not scraper.navigate_to_page(url):
                        print(f"  ✗ Ошибка при переходе на страницу")
                        failed_count += 1
                        continue
                    
                    # Небольшая задержка для загрузки
                    time.sleep(2)
                    
                    # Получение HTML
                    html_content = scraper.get_page_source()
                    
                    # Парсинг детальной информации
                    parser = AvitoHTMLParser(html_content)
                    apartment_data = parser.parse_apartment_detail(url)
                    
                    # Проверка наличия основных данных
                    if not apartment_data.get('title'):
                        print(f"  ⚠ Не удалось извлечь заголовок")
                        failed_count += 1
                        self.db_manager.mark_link_as_parsed(link_id)
                        continue
                    
                    # Сохранение в базу данных
                    result = self.db_manager.insert_apartment(apartment_data)
                    
                    if result:
                        print(f"  ✓ Сохранено: {apartment_data['title'][:50]}...")
                        parsed_count += 1
                    else:
                        print(f"  ⚠ Объявление уже существует в БД")
                    
                    # Отметить ссылку как обработанную
                    self.db_manager.mark_link_as_parsed(link_id)
                    
                    # Задержка между запросами
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"  ✗ Ошибка при парсинге: {e}")
                    failed_count += 1
                    # Отметить как обработанную даже при ошибке
                    self.db_manager.mark_link_as_parsed(link_id)
                    continue
        
        if failed_count > 0:
            print(f"\n⚠ Не удалось обработать: {failed_count} объявлений")
        
        return parsed_count
    
    def _print_statistics(self) -> None:
        """Вывод статистики по базе данных"""
        apartments_count = self.db_manager.get_apartments_count()
        links_total, links_parsed = self.db_manager.get_links_count()
        
        print(f"\n{'=' * 60}")
        print("СТАТИСТИКА")
        print(f"{'=' * 60}")
        print(f"Ссылок собрано: {links_total}")
        print(f"Ссылок обработано: {links_parsed}")
        print(f"Ссылок осталось: {links_total - links_parsed}")
        print(f"Объявлений в БД: {apartments_count}")
        print(f"{'=' * 60}")
        
        # Показать последние 3 записи
        recent_apartments = self.db_manager.get_all_apartments()[:3]
        if recent_apartments:
            print(f"\nПоследние {len(recent_apartments)} объявления:")
            for apt in recent_apartments:
                print(f"\n  • {apt[1][:60]}...")
                print(f"    URL: {apt[2]}")
                print(f"    Цена: {apt[3] or 'Не указана'}")
                print(f"    Адрес: {apt[9] or 'Не указан'}")
    
    def show_all_data(self) -> None:
        """Показать все данные из базы"""
        apartments = self.db_manager.get_all_apartments()
        
        if not apartments:
            print("\nБаза данных пуста")
            return
        
        print(f"\n{'=' * 80}")
        print(f"ВСЕ ДАННЫЕ ({len(apartments)} записей)")
        print(f"{'=' * 80}")
        
        for apt in apartments:
            print(f"\n[ID: {apt[0]}]")
            print(f"Название: {apt[1]}")
            print(f"URL: {apt[2]}")
            print(f"Цена: {apt[3] or 'Не указана'}")
            print(f"Медиа 1: {apt[4] or '-'}")
            print(f"Медиа 2: {apt[5] or '-'}")
            print(f"Медиа 3: {apt[6] or '-'}")
            print(f"О квартире: {apt[7][:100] if apt[7] else '-'}...")
            print(f"Правила: {apt[8][:100] if apt[8] else '-'}...")
            print(f"Адрес: {apt[9] or 'Не указан'}")
            print(f"Описание: {apt[10][:150] if apt[10] else '-'}...")
            print(f"Владелец: {apt[11] or 'Не указан'}")
            print(f"Ссылка владельца: {apt[12] or '-'}")
            print(f"Дата добавления: {apt[13]}")
            print("-" * 80)
    
    def clear_database(self) -> None:
        """Очистка базы данных"""
        self.db_manager.clear_database()
        print("База данных очищена")


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print(" " * 15 + "ПАРСЕР AVITO (v2.0)")
    print("=" * 60)
    
    while True:
        try:
            print("\n📋 МЕНЮ:")
            print("  1. Запустить полный парсинг (сбор ссылок + детальный парсинг)")
            print("  2. Только собрать ссылки на объявления")
            print("  3. Только парсить детальные страницы")
            print("  4. Показать статистику")
            print("  5. Показать все данные")
            print("  6. Очистить базу данных")
            print("  7. Выход")
            
            choice = input("\n➤ Выберите действие (1-7): ").strip()
            
            if choice == "1":
                # Полный парсинг
                bot = AvitoBot(headless=True)
                bot.run()
            
            elif choice == "2":
                # Только сбор ссылок
                print("\n[РЕЖИМ] Сбор ссылок на объявления")
                bot = AvitoBot(headless=True)
                links_count = bot._collect_apartment_links()
                print(f"\n✓ Собрано новых ссылок: {links_count}")
                bot._print_statistics()
            
            elif choice == "3":
                # Только парсинг детальных страниц
                print("\n[РЕЖИМ] Парсинг детальных страниц")
                bot = AvitoBot(headless=True)
                parsed_count = bot._parse_apartment_details()
                print(f"\n✓ Обработано объявлений: {parsed_count}")
                bot._print_statistics()
            
            elif choice == "4":
                # Статистика
                bot = AvitoBot()
                bot._print_statistics()
            
            elif choice == "5":
                # Показать все данные
                bot = AvitoBot()
                bot.show_all_data()
            
            elif choice == "6":
                # Очистить базу
                confirm = input("\n⚠ Вы уверены? Все данные будут удалены! (yes/N): ").strip().lower()
                if confirm == 'yes':
                    bot = AvitoBot()
                    bot.clear_database()
                    print("✓ База данных очищена")
                else:
                    print("Отменено")
            
            elif choice == "7":
                # Выход
                print("\n👋 До свидания!")
                break
            
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
        
        except KeyboardInterrupt:
            print("\n\n⚠ Программа прервана пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()