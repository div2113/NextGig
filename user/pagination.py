from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = "page_size"  # Allow clients to specify page size
    max_page_size = 100  # Max limit for page size
