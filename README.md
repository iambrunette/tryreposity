# Bank System API  
Проект для управления картами и переводами.  

#Проект микросервиса для работы с картами и переводами.  
Поддерживает:
- Создание и управление картами
- Переводы между картами
- Кэширование данных (Redis)
- Периодические отчёты через Celery
- Логирование запросов и ответов
- Экспорт данных в Excel

---

## 🚀 Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/iambrunette/tryreposity.git
cd tryreposity
2. Создать виртуальное окружение

python3 -m venv .venv
source .venv/bin/activate
3. Установить зависимости
pip install -r requirements.txt
4. Настроить переменные окружения
Создайте файл .env с настройками:
DJANGO_SECRET_KEY=your_secret
DATABASE_URL=postgres://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
5. Применить миграции
python manage.py migrate
6. Запустить сервисы
Django:
python manage.py runserver
Redis:
redis-server
Celery:
celery -A bank_system worker -l info
Celery Beat (для периодических задач):
celery -A bank_system beat -l info
📌 API Эндпоинты
Метод	URL	Описание
GET	/card/info/	Информация о карте
POST	/transfer/create/	Создать перевод
POST	/transfer/confirm/	Подтвердить перевод
POST	/transfer/cancel/	Отменить перевод

📂 Кэширование
Метод card_info кэширует данные карты на 30 секунд.
Это снижает нагрузку на базу данных при большом количестве запросов.
📝 Логирование
Методы create, confirm, cancel логируют:
IP-адрес запроса
Тело запроса и ответа
Время обработки
📊 Отчёты
Celery периодически отправляет отчёты в Telegram с:
Общим количеством карт
Общим количеством переводов
📦 Экспорт данных
Можно экспортировать:
Таблицу карт в Excel
Таблицу переводов в Excel