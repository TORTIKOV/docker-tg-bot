# OnTheWay

## Разработка

## Структура проекта

```
-> *flyway* - папка с миграциями и кнофигурацией
-> *config* — глобальные для проекта вещи, вроде настроек (`config.py`)
-> *handlers* - здесь размещены функции, отвечающие за обработку входящих сообщений, команд и других событий от пользователей
-> *db* — инициализация базы и сессии (скорее всего в процессе работы над проектом изменяться не будет)
-> *utils* — полезные утилиты, использующиеся в проекте. Здесь реализованы функции для уведомления администрации бота и показа возможных команд
-> *loader* - инициализирует бота и настраивает хранилище для управления состояниями бота
-> *repository* - содержит функции для взаимодействия с базами данных
-> *.env* — файл для перечисления всех используемых внутри сервиса переменных среды
```

* Создайте виртуальную среду:
~~~console
python -m venv venv
~~~

* В виртуальном окружении установите зависимости:
~~~console
pip install -r requirements.txt
~~~

* В корневой папке проекта создайте файл .env со следующими переменными:
~~~console
BOT_TOKEN = 

POSTGRES_DB = 
POSTGRES_USER = 
POSTGRES_PASSWORD = 
POSTGRES_PORT = 

FLYWAY_URL=jdbc:postgresql://db:5432/your_db_name
FLYWAY_USER=
FLYWAY_PASSWORD=
FLYWAY_LOCATIONS=filesystem:/flyway/sql

~~~
BOT_TOKEN можно получить в телеграме при создании бота: [Гайд](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0), [BotFather](https://t.me/BotFather)
* Запустите контейнер с базой данных следующей командой:
~~~console
docker-compose up --build
~~~
