# Полезные команды для работы с Avito Parser

## Установка

### Автоматическая установка
```cmd
setup.bat
```
или
```powershell
.\setup.ps1
```

### Ручная установка зависимостей
```bash
pip install selenium beautifulsoup4 webdriver-manager lxml
```

## Работа с виртуальным окружением

### Создать виртуальное окружение
```bash
python -m venv venv
```

### Активировать виртуальное окружение
**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Деактивировать виртуальное окружение
```bash
deactivate
```

## Запуск парсера

### Основной запуск
```bash
python main.py
```

### Проверка зависимостей
```bash
python check_dependencies.py
```

## Управление зависимостями

### Показать установленные пакеты
```bash
pip list
```

### Обновить все пакеты
```bash
pip install --upgrade selenium beautifulsoup4 webdriver-manager lxml
```

### Переустановить зависимости
```bash
pip uninstall -y selenium beautifulsoup4 webdriver-manager lxml
pip install selenium beautifulsoup4 webdriver-manager lxml
```

## Работа с базой данных

База данных создается автоматически при первом запуске в файле `avito_data.db`.

### Просмотр данных (через парсер)
```bash
python main.py
# Выберите опцию 2
```

### Очистка базы данных (через парсер)
```bash
python main.py
# Выберите опцию 3
```

### Просмотр базы данных (SQLite CLI)
```bash
sqlite3 avito_data.db
SELECT * FROM apartments;
.exit
```

## Очистка проекта

### Удалить виртуальное окружение
**Windows:**
```cmd
rmdir /s /q venv
```

**Linux/macOS:**
```bash
rm -rf venv
```

### Удалить базу данных
```bash
del avito_data.db
```

### Удалить куки
```bash
del avito_cookies.pkl
```

### Полная очистка (сохранить только исходный код)
**Windows:**
```cmd
rmdir /s /q venv
del avito_data.db
del avito_cookies.pkl
del /q /s __pycache__
```

## Отладка

### Запуск с видимым браузером
Измените в `main.py`:
```python
bot = AvitoBot(headless=False)  # Браузер будет виден
```

### Проверка версии Python
```bash
python --version
```

### Проверка версии Chrome
Откройте Chrome и перейдите на: `chrome://version/`

### Просмотр логов Selenium
Добавьте в начало `scraper.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Git команды

### Инициализация репозитория
```bash
git init
git add .
git commit -m "Initial commit"
```

### Создание .gitignore (уже создан)
Файл `.gitignore` уже настроен и исключает:
- venv/
- *.db
- *.pkl
- __pycache__/

## Полезные сочетания клавиш

- `Ctrl + C` - прервать выполнение скрипта
- `Ctrl + D` (Linux/macOS) или `Ctrl + Z` (Windows) - выход из Python REPL

## Обновление проекта

### Получить последнюю версию (если используете Git)
```bash
git pull
pip install -r requirements.txt --upgrade
```

## Экспорт данных

Для экспорта данных из базы в CSV, добавьте в `main.py`:
```python
import csv
import sqlite3

def export_to_csv():
    conn = sqlite3.connect('avito_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM apartments')
    
    with open('export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'Price', 'Photo URL', 'Created At'])
        writer.writerows(cursor.fetchall())
    
    conn.close()
    print("Данные экспортированы в export.csv")
```

