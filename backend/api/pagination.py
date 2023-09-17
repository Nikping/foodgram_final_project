from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Класс формирования страниц в соответствии с ТЗ"""

    page_size = 6
    page_size_query_param = 'page'
