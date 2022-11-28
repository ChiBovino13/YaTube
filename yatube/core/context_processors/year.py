import datetime

dt_now = datetime.datetime.now()


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': dt_now.year
    }
