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

import json
from numpy.random import rand
from rest_framework import views, status
from rest_framework.response import Response
from Applications.Machine_Learning.registry import MLRegistry
from DDOS_Detection.wsgi import registry

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
    old_statuses = MLAlgorithmStatus.objects.filter(parent_mlalgorithm=instance.parent_mlalgorithm,
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


class PredictView(views.APIView):
    def post(self, request, endpoint_name, format=None):

        algorithm_status = self.request.query_params.get(
            "status", "production")
        algorithm_version = self.request.query_params.get("version")

        algs = MLAlgorithm.objects.filter(
            parent_endpoint__name=endpoint_name, status__status=algorithm_status, status__active=True)

        if algorithm_version is not None:
            algs = algs.filter(version=algorithm_version)

        if len(algs) == 0:
            return Response(
                {"status": "Error", "message": "ML algorithm is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(algs) != 1 and algorithm_status != "ab_testing":
            return Response(
                {"status": "Error", "message": "ML algorithm selection is ambiguous. Please specify algorithm version."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alg_index = 0
        if algorithm_status == "ab_testing":
            alg_index = 0 if rand() < 0.5 else 1

        algorithm_object = registry.endpoints[algs[alg_index].id]
        prediction = algorithm_object.compute_prediction(request.data)

        label = prediction["label"] if "label" in prediction else "error"
        ml_request = MLRequest(
            input_data=json.dumps(request.data),
            full_response=prediction,
            response=label,
            feedback="",
            parent_mlalgorithm=algs[alg_index],
        )
        ml_request.save()

        prediction["request_id"] = ml_request.id

        return Response(prediction)