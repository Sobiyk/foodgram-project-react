from rest_framework import viewsets


class ListRetrieveViewSet(viewsets.mixins.ListModelMixin,
                          viewsets.mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class ListViewSet(viewsets.mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    pass
