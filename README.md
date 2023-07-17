# Проект «𝕐𝕒𝕥𝕦𝕓𝕖» — социальная сеть
____
**Описание:**
Yatub представляет собой проект социальной сети в которой реализованы следующие возможности, публиковать записи, комментировать записи, а так же подписываться или отписываться от авторов.
____
## Технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  \
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)  \
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)  \
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
### 🎉🐚  Как запустить проект  в dev-режиме ⛵♣

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:ChiBovino13/YaTube.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
. venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd yatube_api
python3 manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Создание суперпользователя:

В терминале:
```
python manage.py createsuperuser

username: admin
password: admin
```


### Авторы
Горячева Дарья
