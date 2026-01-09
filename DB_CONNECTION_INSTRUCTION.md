# Инструкция по подключению нескольких приложений к общей MySQL-базе данных

## Обзор

В этом руководстве описано, как безопасно и эффективно настроить подключение нескольких веб-приложений к одной общей MySQL-базе данных с использованием пула соединений, SSL/TLS и других механизмов безопасности.

## Требования безопасности

### 1. Хранение конфигурации в переменных окружения

Все параметры подключения к базе данных должны храниться в файле `.env`, а не в коде:

```
# .env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mydb
DB_USER=lalagame_user
DB_PASSWORD=your_secure_password
DB_SSL_CA=/path/to/ca-cert.pem
DB_SSL_CERT=/path/to/client-cert.pem
DB_SSL_KEY=/path/to/client-key.pem
DB_SSL_MODE=REQUIRED
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 2. Создание специального пользователя MySQL

Создайте отдельного пользователя MySQL с минимальными необходимыми правами:

```sql
-- Создание пользователя с ограниченными правами
CREATE USER 'lalagame_user'@'%' IDENTIFIED BY 'strong_password';

-- Предоставление минимальных необходимых прав на конкретную базу данных
GRANT SELECT, INSERT, UPDATE, DELETE ON mydb.* TO 'lalagame_user'@'%';

-- Обновление привилегий
FLUSH PRIVILEGES;
```

### 3. Настройка SSL/TLS

Для обеспечения безопасности соединений используйте SSL/TLS шифрование:

- `DB_SSL_CA` - путь к файлу сертификата центра сертификации
- `DB_SSL_CERT` - путь к клиентскому сертификату
- `DB_SSL_KEY` - путь к закрытому ключу клиента
- `DB_SSL_MODE=REQUIRED` - обязательное использование SSL

## Настройка пула соединений

### Параметры пула соединений

- `DB_POOL_SIZE=10` - размер пула соединений (может быть увеличен при необходимости)
- `DB_POOL_TIMEOUT=30` - время ожидания получения соединения из пула
- `DB_POOL_RECYCLE=3600` - время жизни соединения в секундах (1 час)

### Обработка ошибок и восстановление

Наша система включает следующие механизмы:

1. **Автоматическое восстановление соединений** - при сбоях соединений система автоматически пытается переподключиться
2. **Таймауты** - предотвращают зависание запросов
3. **Повторные попытки подключения** - при временных сбоях система делает повторные попытки

## Гарантирование согласованности данных

### Транзакции

Для атомарных операций, затрагивающих несколько таблиц, используйте транзакции:

```python
from db_config import get_db_transaction

with get_db_transaction() as conn:
    cursor = conn.cursor()
    
    # Выполнение нескольких связанных операций
    cursor.execute("UPDATE table1 SET column1 = %s WHERE id = %s", (value1, id1))
    cursor.execute("UPDATE table2 SET column2 = %s WHERE id = %s", (value2, id2))
    
    # Если всё прошло успешно, изменения будут зафиксированы
    # При ошибке произойдет автоматический откат (rollback)
```

### Обработка конфликтов одновременных изменений

Система обрабатывает следующие типы конфликтов:

1. **Deadlock** - автоматический откат и повторная попытка
2. **Duplicate entry** - корректная обработка дубликатов
3. **Lock wait timeout** - управление временем ожидания блокировок

## Масштабируемость

### Подготовка архитектуры для микросервисов

Для будущего разделения на микросервисы:

1. **ORM-модели** (`models.py`) вынесены в отдельный модуль, который может быть использован разными приложениями
2. **Конфигурация подключения** (`db_config.py`) также отделена от бизнес-логики
3. **Общие интерфейсы** для доступа к данным позволяют легко мигрировать на API-интерфейсы

## Тестирование

### Unit-тесты для проверки подключения

Запустите тесты для проверки корректности подключения к базе данных:

```bash
python -m pytest test_db_connection.py -v
```

### Проверка работоспособности из разных приложений

1. **Запуск health-check эндпоинта**:
   ```bash
   curl http://your-app-host/health
   ```

2. **Проверка конкурентного доступа**:
   ```bash
   # Запуск нескольких параллельных запросов для проверки работы пула
   for i in {1..10}; do
       curl -X POST http://your-app-host/api/get_question -H "Content-Type: application/json" \
       -d '{"session_id":"test_session","round_num":1}' &
   done
   wait
   ```

### Проверка производительности пула соединений

```bash
# Использование Apache Bench для нагрузочного тестирования
ab -n 100 -c 10 http://your-app-host/health
```

## Практический пример настройки нескольких приложений

### Приложение 1 (LaLaGame)

```python
# app1.py
from db_config import get_db_connection
from models import Question

def get_question(round_num):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions WHERE round_num = %s LIMIT 1", (round_num,))
        return cursor.fetchone()
```

### Приложение 2 (Аналитика)

```python
# app2.py
from db_config import get_db_connection

def get_game_statistics():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                g.session_id,
                g.current_round,
                p.player_name,
                p.score
            FROM game_states g
            LEFT JOIN players p ON g.session_id = p.session_id
        """)
        return cursor.fetchall()
```

## Мониторинг и логирование

Все операции с базой данных логируются с помощью стандартного логирования Python:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Database operation completed successfully")
logger.error("Database operation failed: {error_message}")
```

## Рекомендации по эксплуатации

1. **Мониторинг пула соединений** - регулярно проверяйте количество активных соединений
2. **Обновление SSL-сертификатов** - следите за сроком действия сертификатов
3. **Резервное копирование** - регулярно создавайте резервные копии базы данных
4. **Аудит доступа** - контролируйте список пользователей с доступом к базе данных

## Заключение

Рассмотренная архитектура обеспечивает:
- Безопасное подключение к общей базе данных
- Эффективное использование ресурсов через пул соединений
- Гарантированную согласованность данных через транзакции
- Возможность масштабирования до архитектуры микросервисов
- Надежную систему тестирования и мониторинга