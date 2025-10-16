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
        """Создание таблицы если она не существует"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apartments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price TEXT NOT NULL,
                    photo_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def insert_apartment(self, title: str, price: str, photo_url: Optional[str] = None) -> int:
        """
        Вставка данных о квартире в базу данных
        
        Args:
            title: Заголовок объявления
            price: Цена
            photo_url: URL фотографии
            
        Returns:
            ID вставленной записи
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO apartments (title, price, photo_url)
                VALUES (?, ?, ?)
            """, (title, price, photo_url))
            conn.commit()
            return cursor.lastrowid
    
    def insert_apartments_batch(self, apartments: List[Tuple[str, str, Optional[str]]]) -> None:
        """
        Массовая вставка данных о квартирах
        
        Args:
            apartments: Список кортежей (title, price, photo_url)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO apartments (title, price, photo_url)
                VALUES (?, ?, ?)
            """, apartments)
            conn.commit()
    
    def get_all_apartments(self) -> List[Tuple[int, str, str, str, str]]:
        """
        Получение всех записей из базы данных
        
        Returns:
            Список кортежей (id, title, price, photo_url, created_at)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, price, photo_url, created_at
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
    
    def clear_database(self) -> None:
        """Очистка базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM apartments")
            conn.commit()
    
    def close(self) -> None:
        """Закрытие соединения с базой данных"""
        # SQLite автоматически закрывает соединения, но метод оставлен для совместимости
        pass
