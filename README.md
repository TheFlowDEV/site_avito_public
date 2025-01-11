# StudentMarket  

**StudentMarket** — это сервис для продажи вещей студентами и студентам. Платформа разработана для удобного размещения объявлений, интеллектуального анализа данных и взаимодействия между пользователями.  

---

## 📋 Основные возможности  
- **Добавление и просмотр объявлений**: размещайте товары, указывайте описание и цену.  
- **Рекомендации товаров**: интеллектуальная система анализа данных с использованием модели **BERT** для более релевантных предложений.  
- **Современный дизайн**: интерфейс, основанный на **Material Design Bootstrap**.  
- **Надёжная архитектура**: использованы современные подходы разработки, включая **gRPC** и **REST API**.  

---

## 🚀 Установка и запуск  
### Требования  
- **Python 3.8** или выше  
- **PostgreSQL**  
- **Redis**  
- **pip** (установщик пакетов Python)  

### Инструкции  
Склонируйте репозиторий:  
```bash
git clone https://github.com/TheFlowDEV/site_avito_public.git
cd site_avito_public
```
Установите зависимости:

```bash
pip install -r requirements.txt
```
Убедитесь, что ваши серверы PostgreSQL и Redis запущены:

Для PostgreSQL убедитесь, что база данных создана, а параметры подключения указаны в файле settings.py.
Redis используется для асинхронных задач.
Запустите сервер локально:

```bash
python manage.py runserver
```
### 🛠️ Используемые технологии
- Django: основной фреймворк для разработки веб-приложения.
- Docker: контейнеризация сервисов.
- PostgreSQL: база данных для хранения информации о пользователях и объявлениях.
- Redis: кэширование и управление задачами.
- gRPC: взаимодействие между микросервисами.
- BERT: интеллектуальный анализ текста для рекомендаций.
- Material Design Bootstrap: современный дизайн интерфейса.
### 📂 Структура проекта
- config.py: файл конфигурации с параметрами подключения к базе данных и Redis.
- requirements.txt: список зависимостей проекта.
- manage.py: точка входа для запуска серверных задач.
- apps/: директория, содержащая основные модули приложения (пользователи, товары и т.д.).
### ❓ Часто задаваемые вопросы
- 1. Как изменить параметры подключения к базе данных и Redis?
Измените файл settings.py, указав свои параметры:

PostgreSQL: хост, порт, имя пользователя, пароль и имя базы данных.

Redis: хост и порт.
- 2. Какие платформы поддерживаются?

Приложение может быть запущено на любом сервере с поддержкой Python 3.8+, PostgreSQL и Redis.

- 3. Как работают рекомендации?

Модель BERT анализирует текстовые данные объявлений и предпочтения пользователей, чтобы предлагать более релевантные товары. Далее используя linear_kernel из библиотеки sklearn, сервис рекомендаций анализирует похожесть товаров с теми, которые вас интересуют.


### 📧 Контакты
Если у вас есть вопросы или предложения, свяжитесь со мной через GitHub.
