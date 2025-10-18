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
    
    def parse_apartment_links(self) -> List[str]:
        """
        Парсинг ссылок на объявления со страницы каталога
        
        Returns:
            Список URL объявлений
        """
        links = []
        
        # Поиск контейнеров с объявлениями
        apartment_containers = self.soup.find_all('div', {'data-marker': 'item'})
        
        if not apartment_containers:
            apartment_containers = self.soup.find_all('div', class_=re.compile(r'item.*'))
        
        if not apartment_containers:
            apartment_containers = self.soup.find_all('div', class_=re.compile(r'iva-item.*'))
        
        print(f"Найдено контейнеров с объявлениями: {len(apartment_containers)}")
        
        for container in apartment_containers:
            url = self._extract_apartment_url(container)
            if url:
                links.append(url)
        
        return links
    
    def _extract_apartment_url(self, container) -> Optional[str]:
        """Извлечение URL объявления из контейнера"""
        # Различные селекторы для ссылки
        link_selectors = [
            'a[data-marker="item-title"]',
            'h3 a',
            'a[href*="/kvartiry/"]',
            'a[itemprop="url"]'
        ]
        
        for selector in link_selectors:
            link_elem = container.select_one(selector)
            if link_elem:
                href = link_elem.get('href')
                if href:
                    # Преобразование относительных URL в абсолютные
                    if href.startswith('/'):
                        return 'https://www.avito.ru' + href
                    elif href.startswith('http'):
                        return href
        
        return None
    
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
    
    def parse_apartment_detail(self, url: str) -> Dict[str, Optional[str]]:
        """
        Парсинг детальной страницы объявления
        
        Args:
            url: URL объявления
            
        Returns:
            Словарь с детальными данными объявления
        """
        data = {
            'url': url,
            'title': None,
            'price': None,
            'media_url_1': None,
            'media_url_2': None,
            'media_url_3': None,
            'about_apartment': None,
            'rules': None,
            'address': None,
            'description': None,
            'owner_name': None,
            'owner_url': None
        }
        
        # Извлечение заголовка
        data['title'] = self._extract_detail_title()
        
        # Извлечение цены
        data['price'] = self._extract_detail_price()
        
        # Извлечение медиа (первые 3 фото/видео)
        media_urls = self._extract_media_urls()
        if len(media_urls) > 0:
            data['media_url_1'] = media_urls[0]
        if len(media_urls) > 1:
            data['media_url_2'] = media_urls[1]
        if len(media_urls) > 2:
            data['media_url_3'] = media_urls[2]
        
        # Извлечение информации о квартире
        data['about_apartment'] = self._extract_about_apartment()
        
        # Извлечение правил
        data['rules'] = self._extract_rules()
        
        # Извлечение адреса
        data['address'] = self._extract_address()
        
        # Извлечение описания
        data['description'] = self._extract_description()
        
        # Извлечение информации о владельце
        owner_info = self._extract_owner_info()
        data['owner_name'] = owner_info.get('name')
        data['owner_url'] = owner_info.get('url')
        
        return data
    
    def _extract_detail_title(self) -> Optional[str]:
        """Извлечение заголовка со страницы объявления"""
        title_selectors = [
            'h1[data-marker="item-view/title-info"]',
            'h1[itemprop="name"]',
            'h1.title-info-title',
            'span[class*="title"]',
            'h1'
        ]
        
        for selector in title_selectors:
            elem = self.soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title:
                    return title
        
        return None
    
    def _extract_detail_price(self) -> Optional[str]:
        """Извлечение цены со страницы объявления"""
        price_selectors = [
            'span[data-marker="item-view/item-price"]',
            'span[itemprop="price"]',
            'span[class*="price"]',
            '[class*="item-price"]'
        ]
        
        for selector in price_selectors:
            elem = self.soup.select_one(selector)
            if elem:
                price = elem.get_text(strip=True)
                if price:
                    return price
        
        return None
    
    def _extract_media_urls(self) -> List[str]:
        """Извлечение URL медиа-файлов (фото/видео)"""
        media_urls = []
        
        # Поиск галереи изображений
        img_selectors = [
            'div[data-marker="image-frame/image-wrapper"] img',
            'div[class*="gallery"] img',
            'img[itemprop="image"]',
            'div[class*="image"] img',
            'li[class*="image"] img'
        ]
        
        for selector in img_selectors:
            images = self.soup.select(selector)
            for img in images[:3]:  # Берем только первые 3
                src = img.get('src') or img.get('data-src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.avito.ru' + src
                    
                    if src not in media_urls:
                        media_urls.append(src)
                    
                    if len(media_urls) >= 3:
                        return media_urls
        
        return media_urls
    
    def _extract_about_apartment(self) -> Optional[str]:
        """Извлечение информации о квартире"""
        # Поиск блока с параметрами квартиры
        params_selectors = [
            'ul[class*="params"]',
            'div[class*="params"]',
            'ul[data-marker="item-view/item-params"]'
        ]
        
        for selector in params_selectors:
            params_block = self.soup.select_one(selector)
            if params_block:
                params = []
                items = params_block.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if text:
                        params.append(text)
                
                if params:
                    return ' | '.join(params)
        
        return None
    
    def _extract_rules(self) -> Optional[str]:
        """Извлечение правил проживания"""
        # Поиск блока с правилами
        rules_keywords = ['правил', 'условия', 'можно', 'нельзя']
        
        # Ищем в описании или отдельных блоках
        all_text_blocks = self.soup.find_all(['p', 'div', 'span'])
        
        rules_texts = []
        for block in all_text_blocks:
            text = block.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in rules_keywords):
                if len(text) > 10 and len(text) < 500:  # Фильтр по длине
                    rules_texts.append(text)
        
        if rules_texts:
            return ' | '.join(rules_texts[:3])  # Берем первые 3
        
        return None
    
    def _extract_address(self) -> Optional[str]:
        """Извлечение адреса"""
        address_selectors = [
            'span[class*="geo-root"]',
            'div[class*="item-address"]',
            'span[itemprop="address"]',
            '[data-marker="item-view/item-address"]',
            'div[class*="location"]'
        ]
        
        for selector in address_selectors:
            elem = self.soup.select_one(selector)
            if elem:
                address = elem.get_text(strip=True)
                if address:
                    return address
        
        return None
    
    def _extract_description(self) -> Optional[str]:
        """Извлечение описания объявления"""
        desc_selectors = [
            'div[data-marker="item-view/item-description"]',
            'div[itemprop="description"]',
            'div[class*="item-description"]',
            'p[class*="description"]'
        ]
        
        for selector in desc_selectors:
            elem = self.soup.select_one(selector)
            if elem:
                description = elem.get_text(strip=True)
                if description:
                    return description
        
        return None
    
    def _extract_owner_info(self) -> Dict[str, Optional[str]]:
        """Извлечение информации о владельце"""
        owner_info = {
            'name': None,
            'url': None
        }
        
        # Поиск блока с информацией о продавце
        seller_selectors = [
            'div[data-marker="seller-info"]',
            'div[class*="seller"]',
            'a[class*="seller"]'
        ]
        
        for selector in seller_selectors:
            seller_block = self.soup.select_one(selector)
            if seller_block:
                # Извлечение имени
                name_elem = seller_block.find(['span', 'div', 'a'])
                if name_elem:
                    owner_info['name'] = name_elem.get_text(strip=True)
                
                # Извлечение ссылки на профиль
                link_elem = seller_block.find('a', href=True)
                if link_elem:
                    href = link_elem.get('href')
                    if href:
                        if href.startswith('/'):
                            owner_info['url'] = 'https://www.avito.ru' + href
                        else:
                            owner_info['url'] = href
                
                if owner_info['name']:
                    break
        
        return owner_info
