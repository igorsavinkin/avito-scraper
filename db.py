import sqlite3
import os
from typing import List, Tuple, Optional


class DatabaseManager:
    """Класс для управления базой данных SQLite"""
    
    def __init__(self, db_path: str = "avito_data.db"):
        """
        Инициализация менеджера базы данных
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Создание таблиц если они не существуют"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица для хранения ссылок на объявления (промежуточная)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apartment_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    is_parsed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Основная таблица с детальной информацией
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apartments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    price TEXT,
                    media_url_1 TEXT,
                    media_url_2 TEXT,
                    media_url_3 TEXT,
                    about_apartment TEXT,
                    rules TEXT,
                    address TEXT,
                    description TEXT,
                    owner_name TEXT,
                    owner_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def insert_apartment_link(self, url: str) -> Optional[int]:
        """
        Вставка ссылки на объявление
        
        Args:
            url: URL объявления
            
        Returns:
            ID вставленной записи или None если ссылка уже существует
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO apartment_links (url)
                    VALUES (?)
                """, (url,))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Ссылка уже существует
            return None
    
    def insert_apartment_links_batch(self, urls: List[str]) -> int:
        """
        Массовая вставка ссылок на объявления
        
        Args:
            urls: Список URL объявлений
            
        Returns:
            Количество добавленных новых ссылок
        """
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for url in urls:
                try:
                    cursor.execute("""
                        INSERT INTO apartment_links (url)
                        VALUES (?)
                    """, (url,))
                    count += 1
                except sqlite3.IntegrityError:
                    # Ссылка уже существует
                    continue
            conn.commit()
        return count
    
    def get_unparsed_links(self, limit: Optional[int] = None) -> List[Tuple[int, str]]:
        """
        Получение непарсенных ссылок
        
        Args:
            limit: Максимальное количество ссылок
            
        Returns:
            Список кортежей (id, url)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if limit:
                cursor.execute("""
                    SELECT id, url FROM apartment_links
                    WHERE is_parsed = 0
                    LIMIT ?
                """, (limit,))
            else:
                cursor.execute("""
                    SELECT id, url FROM apartment_links
                    WHERE is_parsed = 0
                """)
            return cursor.fetchall()
    
    def mark_link_as_parsed(self, link_id: int) -> None:
        """
        Отметить ссылку как обработанную
        
        Args:
            link_id: ID ссылки
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE apartment_links
                SET is_parsed = 1
                WHERE id = ?
            """, (link_id,))
            conn.commit()
    
    def insert_apartment(self, apartment_data: dict) -> Optional[int]:
        """
        Вставка детальных данных о квартире
        
        Args:
            apartment_data: Словарь с данными объявления
            
        Returns:
            ID вставленной записи или None при ошибке
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO apartments (
                        title, url, price, media_url_1, media_url_2, media_url_3,
                        about_apartment, rules, address, description, owner_name, owner_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    apartment_data.get('title'),
                    apartment_data.get('url'),
                    apartment_data.get('price'),
                    apartment_data.get('media_url_1'),
                    apartment_data.get('media_url_2'),
                    apartment_data.get('media_url_3'),
                    apartment_data.get('about_apartment'),
                    apartment_data.get('rules'),
                    apartment_data.get('address'),
                    apartment_data.get('description'),
                    apartment_data.get('owner_name'),
                    apartment_data.get('owner_url')
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Ошибка при вставке объявления: {e}")
            return None
    
    def get_all_apartments(self) -> List[Tuple]:
        """
        Получение всех записей из базы данных
        
        Returns:
            Список кортежей с данными объявлений
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, url, price, media_url_1, media_url_2, media_url_3,
                       about_apartment, rules, address, description, owner_name, owner_url, created_at
                FROM apartments
                ORDER BY created_at DESC
            """)
            return cursor.fetchall()
    
    def get_apartments_count(self) -> int:
        """
        Получение количества записей в базе данных
        
        Returns:
            Количество записей
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM apartments")
            return cursor.fetchone()[0]
    
    def get_links_count(self) -> Tuple[int, int]:
        """
        Получение статистики по ссылкам
        
        Returns:
            Кортеж (всего ссылок, обработано)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM apartment_links")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM apartment_links WHERE is_parsed = 1")
            parsed = cursor.fetchone()[0]
            return (total, parsed)
    
    def clear_database(self) -> None:
        """Очистка базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM apartments")
            cursor.execute("DELETE FROM apartment_links")
            conn.commit()
    
    def close(self) -> None:
        """Закрытие соединения с базой данных"""
        # SQLite автоматически закрывает соединения, но метод оставлен для совместимости
        pass
