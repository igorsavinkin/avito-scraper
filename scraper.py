import time
import pickle
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


class AvitoScraper:
    """Класс для управления браузером и скрапинга Avito"""
    
    def __init__(self, headless: bool = True, cookies_file: str = "avito_cookies.pkl"):
        """
        Инициализация скрапера
        
        Args:
            headless: Запуск браузера в фоновом режиме
            cookies_file: Путь к файлу с куки
        """
        self.headless = headless
        self.cookies_file = cookies_file
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
    
    def setup_driver(self) -> None:
        """Настройка и запуск браузера"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Дополнительные опции для стабильности
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Отключение изображений для ускорения загрузки
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            # Метод 1: Автоматическая установка ChromeDriver через webdriver-manager
            driver_path = ChromeDriverManager().install()
            service = Service(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✓ Браузер успешно запущен")
        except Exception as e:
            print(f"⚠ Ошибка при запуске браузера (метод 1): {e}")
            print("Попытка альтернативного метода...")
            try:
                # Метод 2: Попытка использовать системный ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 10)
                print("✓ Браузер успешно запущен (системный ChromeDriver)")
            except Exception as e2:
                print(f"✗ Альтернативный метод также не сработал: {e2}")
                print("\n" + "=" * 60)
                print("РЕШЕНИЕ ПРОБЛЕМЫ:")
                print("=" * 60)
                print("1. Убедитесь, что Chrome установлен:")
                print("   https://www.google.com/chrome/")
                print("\n2. Попробуйте переустановить зависимости:")
                print("   pip uninstall selenium webdriver-manager -y")
                print("   pip install selenium==4.15.2 webdriver-manager==4.0.1")
                print("\n3. Или скачайте ChromeDriver вручную:")
                print("   https://chromedriver.chromium.org/downloads")
                print("   И добавьте в PATH")
                print("=" * 60)
                raise
    
    def load_cookies(self) -> bool:
        """
        Загрузка сохраненных куки
        
        Returns:
            True если куки загружены успешно, False иначе
        """
        if not os.path.exists(self.cookies_file):
            return False
        
        try:
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            # Сначала нужно зайти на домен, чтобы установить куки
            self.driver.get("https://www.avito.ru")
            time.sleep(2)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Ошибка при добавлении куки: {e}")
                    continue
            
            print("Куки успешно загружены")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке куки: {e}")
            return False
    
    def save_cookies(self) -> None:
        """Сохранение куки в файл"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            print("Куки успешно сохранены")
        except Exception as e:
            print(f"Ошибка при сохранении куки: {e}")
    
    def navigate_to_page(self, url: str) -> bool:
        """
        Переход на указанную страницу
        
        Args:
            url: URL страницы для перехода
            
        Returns:
            True если переход успешен, False иначе
        """
        try:
            print(f"Переход на страницу: {url}")
            self.driver.get(url)
            
            # Ожидание загрузки страницы
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Дополнительное время для загрузки контента
            
            return True
        except TimeoutException:
            print("Таймаут при загрузке страницы")
            return False
        except Exception as e:
            print(f"Ошибка при переходе на страницу: {e}")
            return False
    
    def get_page_source(self) -> str:
        """
        Получение HTML кода страницы
        
        Returns:
            HTML код страницы
        """
        if not self.driver:
            raise Exception("Браузер не инициализирован")
        
        return self.driver.page_source
    
    def scroll_to_bottom(self) -> None:
        """Прокрутка страницы вниз для загрузки всего контента"""
        if not self.driver:
            return
        
        # Получаем высоту страницы
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Прокручиваем вниз
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Ждем загрузки нового контента
            time.sleep(2)
            
            # Вычисляем новую высоту страницы
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
    
    def close(self) -> None:
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()
            print("Браузер закрыт")
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.close()
