# Инструкция по установке Avito Parser

## Быстрая установка

### Windows (CMD)
Откройте командную строку (cmd.exe) и выполните:
```cmd
setup.bat
```

### Windows (PowerShell)
Откройте PowerShell и выполните:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\setup.ps1
```

## Ручная установка

### Шаг 1: Создание виртуального окружения
```bash
python -m venv venv
```

### Шаг 2: Активация виртуального окружения

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

### Шаг 3: Установка зависимостей

**Обязательные пакеты:**
```bash
pip install selenium beautifulsoup4 webdriver-manager
```

**Опциональный пакет (для ускорения парсинга):**
```bash
pip install lxml
```

Если lxml не устанавливается, это нормально - парсер будет использовать встроенный html.parser.

### Шаг 4: Проверка установки
```bash
python check_dependencies.py
```

## Устранение проблем

### Проблема: lxml не устанавливается

**Решение:** Это не критично. Парсер автоматически будет использовать встроенный html.parser.

### Проблема: "Python не распознан"

**Решение:** Убедитесь, что Python установлен и добавлен в PATH:
```cmd
python --version
```

Если команда не работает, переустановите Python и обязательно отметьте галочку "Add Python to PATH".

### Проблема: Ошибка при активации venv в PowerShell

**Решение:** Выполните команду для разрешения выполнения скриптов:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Проблема: Chrome WebDriver не найден

**Решение:** Библиотека webdriver-manager автоматически скачает нужный драйвер при первом запуске.

## Запуск парсера

После успешной установки:

1. Активируйте виртуальное окружение (если еще не активировано)
2. Запустите парсер:
```bash
python main.py
```

3. Выберите опцию "1" для запуска парсинга

## Проверка текущей установки

Чтобы проверить, какие пакеты установлены:
```bash
pip list
```

Чтобы проверить версию Python:
```bash
python --version
```

## Дополнительная информация

- Минимальная версия Python: 3.7+
- Требуется Google Chrome
- Требуется подключение к интернету
- Первый запуск может занять больше времени (скачивается ChromeDriver)

