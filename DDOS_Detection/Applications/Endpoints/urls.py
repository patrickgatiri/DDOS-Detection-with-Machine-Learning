# This is the URL configuration specific to the 'Endpoints' application.

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from Applications.Endpoints.views import EndpointViewSet, MLAlgorithmStatusViewSet, MLAlgorithmViewSet, MLRequestViewSet, PredictView, ABTestViewSet, StopABTestView

router = DefaultRouter(trailing_slash=False)

# URL that provides an interface to the available REST API endpoints.
router.register(r"endpoints", EndpointViewSet, basename="endpoints")
router.register(r"mlalgorithms", MLAlgorithmViewSet, basename="mlalgorithms")
router.register(r"mlrequests", MLRequestViewSet, basename="mlrequests")
router.register(r"mlalgorithmstatuses", MLAlgorithmStatusViewSet,
                basename="mlalgorithmstatuses")
router.register(r"abtests", ABTestViewSet, basename="abtests")

'''
Our REST API will use the format "/api/<version>" for versioning purposes.
'''
urlpatterns = [
    url(r"^api/v1/", include(router.urls)),
    url(
        r"^api/v1/(?P<endpoint_name>.+)/predict$", PredictView.as_view(), name="predict"
    ),
    url(
        r"^api/v1/stop_ab_test/(?P<ab_test_id>.+)", StopABTestView.as_view(), name="stop_ab"
    ),
]
