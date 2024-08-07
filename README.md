# Aromastream Django

Этот проект — веб-приложение на Django, которое использует PostgreSQL в качестве базы данных. В этом `README.md` объясняется, как запустить проект с помощью Docker.

## Содержание

- [Предварительные требования](#предварительные-требования)
- [Создание сети проекта в докере](#Создание-сети-проекта-в-докере)
- [Запуск проекта](#запуск-проекта)
- [Структура проекта](#структура-проекта)
- [Важные настройки](#важные-настройки)
- [URL-шаблоны](#url-шаблоны)
- [Примечания](#примечания)

## <a name="предварительные-требования"></a>Предварительные требования

Убедитесь, что у вас установлены следующие инструменты:

- <a href="https://docs.docker.com/get-docker/" target="_blank">Docker</a>

## <a name="создание-сети-проекта-в-docker"></a>Создание сети проекта в Docker



Создайте сеть проекта в Docker:

<pre><code>docker network create aromastream</code></pre>


<h2>Запуск образа PostgreSQL</h2>
<h3>0. Склонируйте репозиторий</h3>
<h3>1. Соберите Docker-образ</h3>
<p>Если вы еще не собрали Docker-образ, выполните следующую команду в каталог db_dockerfile и выполните:</p>
<pre><code>docker build -t postgres .</code></pre>

<h3>2. Создайте volume для хранения данных</h3>
<p>Создайте volume для хранения данных PostgreSQL, чтобы сохранить данные между перезапусками контейнера:</p>
<pre><code>docker volume create postgres_data</code></pre>

<h3>3. Запуск контейнера</h3>
<p>Вы можете запустить контейнер PostgreSQL без использования переменных окружения. Этот метод использует стандартные настройки PostgreSQL, указанные в Dockerfile:</p>
<pre><code>docker run -d \
  --name psg \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  --network aromastream \
  postgres</code></pre>
<ul>
    <li><code>-d</code>: Запускает контейнер в фоновом режиме.</li>
    <li><code>--name my_postgres_container</code>: Задает имя контейнера.</li>
    <li><code>-p 5432:5432</code>: Пробрасывает порт 5432 контейнера на порт 5432 хоста.</li>
    <li><code>-v postgres_data:/var/lib/postgresql/data</code>: Подключает постоянное хранилище для данных PostgreSQL.</li>
</ul>

## <a name="запуск-проекта"></a> Запуск проекта 
    

<ol>
    <li><b>Создайте Docker-образ и запустите контейнер:</b>
    <pre><code>docker build -t aromastream_django .
docker  run -it --name django -p 80:80 --network aromastream aromastream_django</code></pre>
   
   Это запустит контейнер с вашим приложением. Порт 8000 будет использоваться для веб-сервиса Django
    </li>
    <li><b>Запустите веб-приложение:</b>
    <pre><code>python manage.py migrate</code></pre>
    <pre><code>python manage.py runserver 0.0.0.0:80</code></pre>
    </li>
</ol>




## <a name="структура-проекта"></a>Структура проекта

<ul>
    <li><b>Dockerfile</b> — файл с инструкциями для сборки Docker-образа.</li>
    <li><b>requirements.txt</b> — список зависимостей Python для проекта.</li>
    <li><b>manage.py</b> — утилита командной строки для управления проектом Django.</li>
    <li><b>api/</b> — основной каталог вашего проекта, содержащий Django-приложение.</li>
</ul>

## <a name="важные-настройки"></a>Важные настройки

### База данных

Проект использует PostgreSQL в качестве базы данных. Настройки подключения:

<ul>
    <li><b>ENGINE:</b> django.db.backends.postgresql — драйвер для работы с PostgreSQL.</li>
    <li><b>NAME:</b> django — имя базы данных.</li>
    <li><b>USER:</b> django — имя пользователя для подключения к базе данных.</li>
    <li><b>PASSWORD:</b> 8995 — пароль пользователя для подключения к базе данных.</li>
    <li><b>HOST:</b> 127.0.0.1 — адрес сервера базы данных.</li>
    <li><b>PORT:</b> 5432 — порт сервера базы данных.</li>
</ul>

### Безопасность

<ul>
    <li><b>DEBUG:</b> True — режим отладки, включающий детальные сообщения об ошибках (не рекомендуется для продакшн-окружения).</li>
    <li><b>ALLOWED_HOSTS:</b> ['*'] — список разрешенных хостов для доступа к приложению.</li>
</ul>

### Приложения и middleware

<ul>
    <li><b>INSTALLED_APPS:</b> включают базовые приложения Django и дополнительные, такие как <code>drf_spectacular</code> для автоматической генерации схем API, <code>rest_framework</code> для построения API и <code>drf_api_logger</code> для логирования запросов.</li>
    <li><b>MIDDLEWARE:</b> включают стандартные middleware Django и <code>APILoggerMiddleware</code> для логирования API.</li>
</ul>

### JWT Authentication

Используется библиотека <code>rest_framework_simplejwt</code> для аутентификации:

<ul>
    <li><b>SLIDING_TOKEN_LIFETIME:</b> 30 дней — время жизни JWT токена.</li>
    <li><b>SLIDING_TOKEN_REFRESH_LIFETIME:</b> 1 секунда — время жизни токена обновления.</li>
</ul>

### Логирование API

<ul>
    <li><b>DRF_API_LOGGER_DATABASE:</b> True — включение логирования запросов в базу данных.</li>
    <li><b>DRF_LOGGER_QUEUE_MAX_SIZE:</b> 50 — максимальный размер очереди для логов.</li>
    <li><b>DRF_API_LOGGER_EXCLUDE_KEYS:</b> ['password', 'token'] — ключи, которые будут исключены из логов.</li>
</ul>

### Дополнительные настройки

<ul>
    <li><b>ARDUINO_URL:</b> 'localhost:1203/{}' — URL для взаимодействия с Arduino.</li>
    <li><b>PAGE_SIZE:</b> 15 — размер страницы для пагинации API.</li>
    <li><b>TIME_ZONE:</b> 'Europe/Moscow' — настройка временной зоны.</li>
</ul>

## <a name="url-шаблоны"></a>URL-шаблоны

Ниже приведены доступные маршруты API и их назначения:

<ul>
    <li><b>/admin/:</b> интерфейс администратора Django для управления приложением.</li>
    <li><b>/api/:</b> основной префикс для всех API эндпоинтов. Все маршруты API будут доступны по этому пути.</li>
    <li><b>/api/login/:</b> <code>TokenObtainSlidingView</code> — получение JWT токена для аутентификации.</li>
    <li><b>/api/signup/:</b> <code>UserCreateView</code> — создание нового пользователя.</li>
    <li><b>/api/user/:</b> <code>UserGetView</code> — получение информации о текущем пользователе.</li>
    <li><b>/api/user/update/:</b> <code>UserUpdateView</code> — обновление данных текущего пользователя.</li>
    <li><b>/api/password_reset/:</b> <code>UserPasswordUpdateView</code> — сброс пароля пользователя.</li>
    <li><b>/api/password_reset/confirm/:</b> <code>UserPasswordUpdateConfirmView</code> — подтверждение сброса пароля.</li>
    <li><b>/api/timestamps/:</b> <code>TimeStampCreateView</code> — создание новых временных меток.</li>
    <li><b>/api/timestamps/&lt;int:video_id&gt;/:</b> <code>TimeStampListView</code> — получение списка временных меток для указанного видео.</li>
    <li><b>/api/videos/:</b> <code>VideoListView</code> — получение списка видео.</li>
    <li><b>/api/videos/&lt;int:video_id&gt;/:</b> <code>VideoDetailView</code> — получение детальной информации о видео.</li>
    <li><b>/api/videos/popular/:</b> <code>PopularVideoListView</code> — получение списка популярных видео.</li>
    <li><b>/api/videos/search/:</b> <code>SearchVideoListView</code> — поиск видео по критериям.</li>
    <li><b>/api/arduino/trigger:</b> <code>TriggerListView</code> — вызов триггера для взаимодействия с Arduino.</li>
    <li><b>/api/schema/swagger-ui/:</b> <code>SpectacularSwaggerView</code> — отображение схемы API в Swagger UI.</li>
    <li><b>/api/schema/redoc/:</b> <code>SpectacularRedocView</code> — отображение схемы API в ReDoc.</li>
</ul>

## <a name="примечания"></a>Примечания

<ul>
    <li>Пользователь PostgreSQL и база данных создаются автоматически при запуске контейнера.</li>
    <li>Для доступа к базе данных используйте следующие параметры:
        <ul>
            <li><b>Хост:</b> <имя контейнера с бд в той же сети докера></li>
            <li><b>Порт:</b> 5432</li>
            <li><b>Имя пользователя:</b> django</li>
            <li><b>Пароль:</b> 8995</li>
            <li><b>Имя базы данных:</b> django</li>
        </ul>
    </li>
    <li>Для безопасности важно изменить секретный ключ из SECRET_KEY в настройках Django.</li>
</ul>

Если у вас возникли вопросы или проблемы, пожалуйста, создайте issue в <a href="https://github.com/SkyAdam1/aromastream_django" target="_blank">репозитории проекта</a>.
