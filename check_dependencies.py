"""
Скрипт для проверки установленных зависимостей
"""

import sys

def check_dependencies():
    """Проверка наличия всех необходимых библиотек"""
    
    print("=" * 50)
    print("Проверка зависимостей для Avito Parser")
    print("=" * 50)
    print()
    
    dependencies = {
        'selenium': 'Selenium WebDriver',
        'bs4': 'BeautifulSoup4',
        'webdriver_manager': 'WebDriver Manager',
        'lxml': 'lxml (опционально)'
    }
    
    missing = []
    installed = []
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name:30} - Установлен")
            installed.append(name)
        except ImportError:
            if module == 'lxml':
                print(f"⚠ {name:30} - Не установлен (будет использован html.parser)")
            else:
                print(f"✗ {name:30} - НЕ УСТАНОВЛЕН")
                missing.append(name)
    
    print()
    print("=" * 50)
    
    if missing:
        print(f"\n❌ Отсутствуют обязательные зависимости: {', '.join(missing)}")
        print("\nДля установки выполните:")
        print("  pip install selenium beautifulsoup4 webdriver-manager")
        return False
    else:
        print("\n✅ Все обязательные зависимости установлены!")
        print(f"   Установлено: {len(installed)}/{len(dependencies)}")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)

