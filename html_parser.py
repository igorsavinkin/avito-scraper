import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class AvitoHTMLParser:
    """Класс для парсинга HTML страниц Avito"""
    
    def __init__(self, html_content: str):
        """
        Инициализация парсера
        
        Args:
            html_content: HTML содержимое страницы
        """
        try:
            self.soup = BeautifulSoup(html_content, 'lxml')
        except:
            # Если lxml не установлен, используем встроенный парсер
            self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def parse_apartments(self) -> List[Dict[str, Optional[str]]]:
        """
        Парсинг объявлений о квартирах
        
        Returns:
            Список словарей с данными о квартирах
        """
        apartments = []
        
        # Поиск контейнеров с объявлениями
        # На Avito объявления обычно находятся в элементах с определенными классами
        apartment_containers = self.soup.find_all('div', {'data-marker': 'item'})
        
        if not apartment_containers:
            # Альтернативный поиск по классам
            apartment_containers = self.soup.find_all('div', class_=re.compile(r'item.*'))
        
        if not apartment_containers:
            # Еще один вариант поиска
            apartment_containers = self.soup.find_all('div', class_=re.compile(r'iva-item.*'))
        
        print(f"Найдено контейнеров с объявлениями: {len(apartment_containers)}")
        
        for container in apartment_containers:
            apartment_data = self._parse_single_apartment(container)
            if apartment_data:
                apartments.append(apartment_data)
        
        return apartments
    
    def _parse_single_apartment(self, container) -> Optional[Dict[str, Optional[str]]]:
        """
        Парсинг одного объявления
        
        Args:
            container: HTML контейнер с объявлением
            
        Returns:
            Словарь с данными объявления или None
        """
        try:
            # Извлечение заголовка
            title = self._extract_title(container)
            
            # Извлечение цены
            price = self._extract_price(container)
            
            # Извлечение URL фотографии
            photo_url = self._extract_photo_url(container)
            
            if title and price:  # Минимальные требования
                return {
                    'title': title,
                    'price': price,
                    'photo_url': photo_url
                }
            
        except Exception as e:
            print(f"Ошибка при парсинге объявления: {e}")
        
        return None
    
    def _extract_title(self, container) -> Optional[str]:
        """Извлечение заголовка объявления"""
        # Различные селекторы для заголовка
        title_selectors = [
            'h3[data-marker="item-title"] a',
            'h3 a[data-marker="item-title"]',
            'a[data-marker="item-title"]',
            'h3 a',
            '.item-title a',
            '.iva-item-titleStep a',
            'a[href*="/volgograd/kvartiry/"]'
        ]
        
        for selector in title_selectors:
            title_elem = container.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title:
                    return title
        
        return None
    
    def _extract_price(self, container) -> Optional[str]:
        """Извлечение цены"""
        # Различные селекторы для цены
        price_selectors = [
            '[data-marker="item-price"]',
            '.item-price',
            '.price-text',
            '.iva-item-priceStep',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = container.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Очистка цены от лишних символов
                price = re.sub(r'[^\d\s₽]', '', price_text).strip()
                if price:
                    return price
        
        return None
    
    def _extract_photo_url(self, container) -> Optional[str]:
        """Извлечение URL фотографии"""
        # Различные селекторы для изображения
        img_selectors = [
            'img[data-marker="item-photo"]',
            '.item-photo img',
            '.photo-slider img',
            '.iva-item-photo img',
            'img[src*="avatars.mds.yandex.net"]',
            'img[src*="avito.st"]'
        ]
        
        for selector in img_selectors:
            img_elem = container.select_one(selector)
            if img_elem:
                photo_url = img_elem.get('src') or img_elem.get('data-src')
                if photo_url:
                    # Преобразование относительных URL в абсолютные
                    if photo_url.startswith('//'):
                        photo_url = 'https:' + photo_url
                    elif photo_url.startswith('/'):
                        photo_url = 'https://www.avito.ru' + photo_url
                    
                    return photo_url
        
        return None
    
    def get_total_count(self) -> Optional[int]:
        """
        Получение общего количества объявлений на странице
        
        Returns:
            Количество объявлений или None
        """
        # Поиск счетчика объявлений
        count_selectors = [
            '[data-marker="page-title/count"]',
            '.page-title-count',
            '[class*="count"]'
        ]
        
        for selector in count_selectors:
            count_elem = self.soup.select_one(selector)
            if count_elem:
                count_text = count_elem.get_text(strip=True)
                # Извлечение числа из текста
                numbers = re.findall(r'\d+', count_text)
                if numbers:
                    return int(numbers[0])
        
        return None
    
    def has_next_page(self) -> bool:
        """
        Проверка наличия следующей страницы
        
        Returns:
            True если есть следующая страница, False иначе
        """
        # Поиск кнопки "Следующая страница"
        next_selectors = [
            'a[data-marker="pagination-button/next"]',
            '.pagination-item_next',
            'a[aria-label="Следующая страница"]'
        ]
        
        for selector in next_selectors:
            next_elem = self.soup.select_one(selector)
            if next_elem and not next_elem.get('disabled'):
                return True
        
        return False
    
    def get_next_page_url(self) -> Optional[str]:
        """
        Получение URL следующей страницы
        
        Returns:
            URL следующей страницы или None
        """
        next_selectors = [
            'a[data-marker="pagination-button/next"]',
            '.pagination-item_next a',
            'a[aria-label="Следующая страница"]'
        ]
        
        for selector in next_selectors:
            next_elem = self.soup.select_one(selector)
            if next_elem:
                href = next_elem.get('href')
                if href:
                    if href.startswith('/'):
                        return 'https://www.avito.ru' + href
                    return href
        
        return None
