# Mixins are a controlled way of adding functionality to classes in Python-Django.
# They enable our code to be DRY.
from rest_framework import mixins

# DRF Viewsets enable us to create the REST API faster through abstraction of the trivial and generic details.
from rest_framework import viewsets

# Import the models and serializers.
from Applications.Endpoints.models import Endpoint
from Applications.Endpoints.serializers import EndpointSerializer

from Applications.Endpoints.models import MLAlgorithm
from Applications.Endpoints.serializers import MLAlgorithmSerializer

from Applications.Endpoints.models import MLAlgorithmStatus
from Applications.Endpoints.serializers import MLAlgorithmStatusSerializer

from Applications.Endpoints.models import MLRequest
from Applications.Endpoints.serializers import MLRequestSerializer

# To maintain the ACID properties of the database.
from django.db import transaction

from rest_framework.exceptions import APIException

# Create your views here.

'''
We will use Django Mixins to handle the API logic.

ListModelMixin ==> Lists all the instances within a queryset.
RetrieveModelMixin ==> Retrieves an existing model instance.
CreateModelMixin ==> Creates and saves a new model instance.
UpdateModelMixin ==> Updates an existing model instance.
DeleteModelMixin ==> Deletes an existing model instance.
'''


# Retrieves all of the available endpoints.
class EndpointViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = EndpointSerializer
    queryset = Endpoint.objects.all()

# Retrieves all of the available Machine Learning algorithms.
class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = MLAlgorithmSerializer
    queryset = MLAlgorithm.objects.all()

# Retrieves all of the prediction requests received by the Machine Learning algorithms.
class MLRequestViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.UpdateModelMixin
):
    serializer_class = MLRequestSerializer
    queryset = MLRequest.objects.all()

'''
When the status of a Machine Learning algorithm is set to active (meaning it is actively used in production for classification),
the status of the previously active algorithm needs to be set to inactive.
'''

# Helper function that handles the deactivation of the previously active algorithm.
def deactivate_other_statuses(instance):
    # Retrieve all the statuses of the previously active algorithm.
    old_statuses = MLAlgorithmStatus.objects.filter(parent_mlalgorithm = instance.parent_mlalgorithm,
                                                        # Filter based on current time.
                                                        created_at__lt=instance.created_at,
                                                        active=True)
    
    # The previously active algorithm may have had multiple statuses that indicated it was active.
    # All of these need to be set to inactive.
    for i in range(len(old_statuses)):
        old_statuses[i].active = False
    MLAlgorithmStatus.objects.bulk_update(old_statuses, ["active"])

class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.CreateModelMixin
):
    # Retrieves all the statuses of the Machine Learning algorithms.
    serializer_class = MLAlgorithmStatusSerializer
    queryset = MLAlgorithmStatus.objects.all()

    # Function that allows the system administrator to choose an MLAlgorithm that should be deployed to production.
    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(active=True)
                # Set the statuses of the other algorithms to inactive.
                deactivate_other_statuses(instance)

        except Exception as e:
            raise APIException(str(e))