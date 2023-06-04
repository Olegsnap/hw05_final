# Проект спринта: подписки на авторов

### Задача спринта - покрыть тестами проект Yatibe.

Реализовано тестирование проекта Yatube (Спринт 6.Яндекс.Практикум). Написаны Unittest, проверена их работоспобность и правильность. Минимальное значение в отчете Coverage(процент покрытия тестами) - 82%. 

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Olegsnap/hw05_final/
cd hw05_Final/
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/scripts/activate
```
Обновить pip:
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```

### Как протестировать проект:
Перейдите в директорию hw05_final/yatube/
Запусть тесты можно командой:
```
pytest
```
Или командой:
```
python manage.py test
```
Отдельно проетстировать, например, представления, можно через указание файла теста:
```
python manage.py test posts.tests.test_views
```

## Автор: Олег Асташкин &#128040;
