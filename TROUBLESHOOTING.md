# Устранение неполадок

## ❌ Ошибка: OSError [WinError 193] %1 не является приложением Win32

### Причина
Эта ошибка возникает когда ChromeDriver поврежден или несовместим с вашей версией Chrome.

### Решение 1: Автоматическое исправление (рекомендуется)

```bash
python fix_chromedriver.py
```

Скрипт автоматически:
- Проверит установку Chrome
- Проверит зависимости
- Попытается исправить проблемы
- Протестирует запуск

### Решение 2: Ручное исправление

#### Шаг 1: Проверьте Chrome
```bash
# Убедитесь что Chrome установлен
# Скачайте: https://www.google.com/chrome/
```

#### Шаг 2: Переустановите зависимости
```bash
pip uninstall -y selenium webdriver-manager
pip install selenium==4.15.2 webdriver-manager==4.0.1
```

#### Шаг 3: Очистите кэш ChromeDriver
```bash
# Windows
rmdir /s /q %USERPROFILE%\.wdm

# Linux/macOS
rm -rf ~/.wdm
```

#### Шаг 4: Попробуйте снова
```bash
python main.py
```

### Решение 3: Ручная установка ChromeDriver

#### Шаг 1: Узнайте версию Chrome
1. Откройте Chrome
2. Перейдите на `chrome://version/`
3. Запомните версию (например, 120.0.6099.109)

#### Шаг 2: Скачайте ChromeDriver
1. Перейдите на https://chromedriver.chromium.org/downloads
2. Скачайте версию, соответствующую вашей версии Chrome
3. Распакуйте `chromedriver.exe`

#### Шаг 3: Добавьте в PATH
**Windows:**
```
1. Скопируйте chromedriver.exe в C:\Windows\System32\
   или
2. Добавьте папку с chromedriver.exe в PATH:
   - Панель управления → Система → Дополнительные параметры
   - Переменные среды → Path → Изменить
   - Добавить путь к папке с chromedriver.exe
```

**Linux/macOS:**
```bash
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

---

## ❌ Ошибка: Ссылки не найдены

### Причина
Структура сайта Avito изменилась или страница не загрузилась.

### Решение

#### 1. Проверьте URL
Откройте `main.py` и убедитесь что URL актуален:
```python
self.target_url = "https://www.avito.ru/volgograd/..."
```

#### 2. Запустите с видимым браузером
В `main.py` измените:
```python
bot = AvitoBot(headless=False)  # Браузер будет виден
```

#### 3. Проверьте селекторы
Если структура сайта изменилась, обновите селекторы в `html_parser.py`:
```python
apartment_containers = self.soup.find_all('div', {'data-marker': 'item'})
```

---

## ❌ Ошибка: Не удалось извлечь заголовок

### Причина
Объявление удалено или структура страницы изменилась.

### Решение

#### 1. Проверьте страницу вручную
Откройте ссылку в браузере и убедитесь что объявление существует.

#### 2. Обновите селекторы
В `html_parser.py` метод `_extract_detail_title()`:
```python
title_selectors = [
    'h1[data-marker="item-view/title-info"]',
    'h1[itemprop="name"]',
    # Добавьте новые селекторы
]
```

#### 3. Пропустите проблемные объявления
Парсер автоматически пропускает объявления без заголовка.

---

## ❌ Ошибка: Таймаут при загрузке страницы

### Причина
Медленное интернет-соединение или сайт не отвечает.

### Решение

#### 1. Увеличьте таймаут
В `scraper.py`:
```python
self.wait = WebDriverWait(self.driver, 20)  # было 10
```

#### 2. Увеличьте задержки
В `main.py`:
```python
time.sleep(5)  # было 2
```

#### 3. Проверьте интернет
```bash
ping avito.ru
```

---

## ❌ Ошибка: База данных заблокирована

### Причина
База данных используется другим процессом.

### Решение

#### 1. Закройте все экземпляры парсера
```bash
# Windows
taskkill /F /IM python.exe

# Linux/macOS
pkill -9 python
```

#### 2. Проверьте блокировку
```bash
# Если база открыта в SQLite Browser - закройте его
```

#### 3. Перезапустите парсер
```bash
python main.py
```

---

## ❌ Ошибка: Блокировка сайтом

### Признаки
- Капча
- Сообщение "Доступ ограничен"
- Пустые страницы

### Решение

#### 1. Удалите куки
```bash
del avito_cookies.pkl
```

#### 2. Увеличьте задержки
В `main.py`:
```python
time.sleep(3)  # между запросами
```

#### 3. Используйте VPN
Подключитесь к VPN и попробуйте снова.

#### 4. Измените User-Agent
В `scraper.py`:
```python
chrome_options.add_argument("--user-agent=Mozilla/5.0 ...")
```

---

## ❌ Ошибка: ModuleNotFoundError

### Причина
Не установлены зависимости.

### Решение

```bash
# Проверьте зависимости
python check_dependencies.py

# Установите недостающие
pip install -r requirements.txt

# Или по отдельности
pip install selenium beautifulsoup4 webdriver-manager lxml
```

---

## ❌ Ошибка: Permission denied

### Причина
Недостаточно прав для создания/изменения файлов.

### Решение

#### Windows:
```bash
# Запустите терминал от имени администратора
```

#### Linux/macOS:
```bash
sudo python main.py
# или
chmod +x main.py
```

---

## 🔍 Диагностика

### Проверка зависимостей
```bash
python check_dependencies.py
```

### Проверка ChromeDriver
```bash
python fix_chromedriver.py
```

### Проверка базы данных
```bash
sqlite3 avito_data.db "SELECT COUNT(*) FROM apartments;"
```

### Просмотр логов
Запустите с видимым браузером для отладки:
```python
bot = AvitoBot(headless=False)
```

---

## 📞 Получение помощи

### 1. Соберите информацию
```bash
python --version
pip list | grep selenium
pip list | grep beautifulsoup4
```

### 2. Проверьте документацию
- [README.md](README.md) - Основная документация
- [USAGE.md](USAGE.md) - Руководство по использованию
- [INSTALL.md](INSTALL.md) - Установка

### 3. Типичные проблемы
- Chrome не установлен → Установите Chrome
- Старая версия Python → Обновите до 3.7+
- Антивирус блокирует → Добавьте в исключения
- Firewall блокирует → Разрешите Python

---

## 💡 Советы по предотвращению проблем

1. **Регулярно обновляйте зависимости**
   ```bash
   pip install --upgrade selenium webdriver-manager
   ```

2. **Делайте резервные копии базы**
   ```bash
   copy avito_data.db avito_data_backup.db
   ```

3. **Используйте виртуальное окружение**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Проверяйте перед парсингом**
   - Режим 2 (сбор ссылок) для оценки
   - Режим 4 (статистика) для контроля

5. **Не перегружайте сайт**
   - Используйте разумные задержки
   - Парсите в нерабочее время
   - Соблюдайте правила сайта

