"""
Скрипт для диагностики и исправления проблем с ChromeDriver
"""

import sys
import os
import subprocess
import platform

def check_chrome_installed():
    """Проверка установки Chrome"""
    print("\n[1/5] Проверка установки Chrome...")
    
    system = platform.system()
    
    if system == "Windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"✓ Chrome найден: {path}")
                return True
        
        print("✗ Chrome не найден")
        print("  Скачайте: https://www.google.com/chrome/")
        return False
    
    else:
        print("⚠ Автопроверка доступна только для Windows")
        return None

def check_selenium():
    """Проверка установки Selenium"""
    print("\n[2/5] Проверка Selenium...")
    
    try:
        import selenium
        print(f"✓ Selenium установлен: версия {selenium.__version__}")
        return True
    except ImportError:
        print("✗ Selenium не установлен")
        return False

def check_webdriver_manager():
    """Проверка webdriver-manager"""
    print("\n[3/5] Проверка webdriver-manager...")
    
    try:
        import webdriver_manager
        print(f"✓ webdriver-manager установлен")
        return True
    except ImportError:
        print("✗ webdriver-manager не установлен")
        return False

def test_chromedriver():
    """Тест запуска ChromeDriver"""
    print("\n[4/5] Тест запуска ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("Попытка установки ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✓ ChromeDriver установлен: {driver_path}")
        
        print("Попытка запуска браузера...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ Браузер успешно запущен")
        driver.quit()
        print("✓ Браузер закрыт")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def fix_issues():
    """Попытка исправить проблемы"""
    print("\n[5/5] Попытка исправления проблем...")
    
    print("\nВыполняется переустановка зависимостей...")
    
    commands = [
        ["pip", "uninstall", "-y", "selenium", "webdriver-manager"],
        ["pip", "install", "selenium==4.15.2", "webdriver-manager==4.0.1"]
    ]
    
    for cmd in commands:
        print(f"\nВыполнение: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Успешно")
            else:
                print(f"⚠ Предупреждение: {result.stderr}")
        except Exception as e:
            print(f"✗ Ошибка: {e}")

def main():
    """Главная функция"""
    print("=" * 60)
    print("ДИАГНОСТИКА И ИСПРАВЛЕНИЕ CHROMEDRIVER")
    print("=" * 60)
    
    # Проверки
    chrome_ok = check_chrome_installed()
    selenium_ok = check_selenium()
    wdm_ok = check_webdriver_manager()
    
    if not selenium_ok or not wdm_ok:
        print("\n" + "=" * 60)
        print("ТРЕБУЕТСЯ УСТАНОВКА ЗАВИСИМОСТЕЙ")
        print("=" * 60)
        print("\nВыполните:")
        print("pip install selenium==4.15.2 webdriver-manager==4.0.1")
        return
    
    # Тест
    test_ok = test_chromedriver()
    
    # Итоги
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
    print("=" * 60)
    print(f"Chrome: {'✓' if chrome_ok else '✗'}")
    print(f"Selenium: {'✓' if selenium_ok else '✗'}")
    print(f"webdriver-manager: {'✓' if wdm_ok else '✗'}")
    print(f"Тест запуска: {'✓' if test_ok else '✗'}")
    print("=" * 60)
    
    if not test_ok:
        print("\n⚠ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        choice = input("\nПопытаться исправить автоматически? (y/N): ").strip().lower()
        
        if choice == 'y':
            fix_issues()
            print("\n✓ Исправление завершено")
            print("Попробуйте запустить парсер снова")
        else:
            print("\nРучное исправление:")
            print("1. Установите Chrome: https://www.google.com/chrome/")
            print("2. Выполните:")
            print("   pip uninstall -y selenium webdriver-manager")
            print("   pip install selenium==4.15.2 webdriver-manager==4.0.1")
            print("3. Перезапустите терминал")
    else:
        print("\n✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        print("Парсер готов к работе!")

if __name__ == "__main__":
    main()

