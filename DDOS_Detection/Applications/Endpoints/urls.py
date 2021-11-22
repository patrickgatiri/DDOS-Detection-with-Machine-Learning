# This is the URL configuration specific to the 'Endpoints' application.

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from Applications.Endpoints.views import EndpointViewSet, MLAlgorithmStatusViewSet, MLAlgorithmViewSet, MLRequestViewSet

router = DefaultRouter(trailing_slash=False)

# URL that provides an interface to the available REST API endpoints.
router.register(r"endpoints", EndpointViewSet, basename="endpoints")
router.register(r"mlalgorithms", MLAlgorithmViewSet, basename="mlalgorithms")
router.register(r"mlrequests", MLRequestViewSet, basename="mlrequests")
router.register(r"mlalgorithmstatuses", MLAlgorithmStatusViewSet,
                basename="mlalgorithmstatuses")

'''
Our REST API will use the format "/api/<version>" for versioning purposes.
'''
urlpatterns = [
    url(r"^api/v1/", include(router.urls)),
]
