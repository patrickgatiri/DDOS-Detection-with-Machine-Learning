'''
Serializers allow complex data such as querysets and model instances
to be converted to native Python datatypes such as  arrays and dictionaries
that can then be easily rendered into JSON, XML or other content types.
Serializers also provide deserialization,
allowing parsed data to be converted back into complex types,
after first validating the incoming data.

Serializers are the links between our views and our models.

Our frontend - The REST API - will be handling data in the form of Javascript Object Notation (JSON).
Our backend - SQLite - will be handling data in the form of Python objects, which are instances of our models.
The serializers will handle the conversion of data to and from these different formats.

We will use ModelSerializers to keep the code DRY.
'''
from rest_framework import serializers

# Import each of the models so as to create a serializer for each.
from Applications.Endpoints.models import Endpoint
from Applications.Endpoints.models import MLAlgorithm
from Applications.Endpoints.models import MLAlgorithmStatus
from Applications.Endpoints.models import MLRequest
from Applications.Endpoints.models import ABTest

'''
For each of the serializers, there is a variable named "read_only_fields".
This variable is descriptive of the fields of the model that cannot be edited via the REST API.
'''
class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        # Associate the serializer to the model.
        model = Endpoint

        # An endpoint can only be created or deleted directly from the backend.
        # As such, all its fields are read only fields relative to the REST API.
        read_only_fields = ("id", "name", "owner", "created_at")
        fields = read_only_fields

class MLAlgorithmSerializer(serializers.ModelSerializer):
    # Helper method used to retrieve the latest / current status of an algorithm.
    current_status = serializers.SerializerMethodField(read_only=True)
    def get_current_status(self, mlalgorithm):
        return MLAlgorithmStatus.objects.filter(parent_mlalgorithm=mlalgorithm).latest('created_at').status

    class Meta:
        # Associate the serializer to the model.
        model = MLAlgorithm

        # An algorithm can only be created or deleted directly from the backend.
        # As such, all its fields are read only fields relative to the REST API.
        read_only_fields = ("id", "name", "description", "code",
                            "version", "owner", "created_at",
                            "parent_endpoint", "current_status")
        fields = read_only_fields
        
class MLAlgorithmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        # Associate the serializer to the model.
        model = MLAlgorithmStatus

        # The status of an algorithm can be changed by the administrator via the HTTP REST API
        # As such, the "status", "created_by", "created_at" and "parent_mlalgorithm" fields of the MLAlgorithmStatus are not read only.
        # The "id" field is autogenerated is therefore read only.
        # The "active" field is a boolean flag that indicates whether or not the algorithm is in use during production.
        # It is True if the status of the algorithm is "Production", and False otherwise.
        # This means that it is also a read only field.
        read_only_fields = ("id", "active")
        fields = ("id", "active", "status", "created_by", "created_at",
                            "parent_mlalgorithm")

class MLRequestSerializer(serializers.ModelSerializer):
    class Meta:
        # Associate the serializer to the model.
        model = MLRequest

        # An MLRequest model represents each classification attempt by an MLAlgorithm.
        # The "input_data", "full_response", "response", "created_at" and "parent_mlalgorithm" fields cannot be changed once classification has taken place. They are read only.
        # The "feedback" field can be changed by the administrator, in order to monitor the performance of the algorithm. It is not read only.
        read_only_fields = (
            "id",
            "input_data",
            "full_response",
            "response",
            "created_at",
            "parent_mlalgorithm",
        )
        fields =  (
            "id",
            "input_data",
            "full_response",
            "response",
            "feedback",
            "created_at",
            "parent_mlalgorithm",
        )

class ABTestSerializer(serializers.ModelSerializer):
    class Meta:
        # Associate the serializer to the model.
        model = ABTest

        # An AB Test can be initiated by the administrator via the HTTP REST API.
        # When performing an AB Test, the administrator defines the "title", "created_by", "parent_mlalgorithm_1" and "parent_mlalgorithm_2" fields of the AB Test.
        # The "id", "created_at", "ended_at" and "summary" fields are generated by the system. They are read only.
        read_only_fields = (
            "id",
            "ended_at",
            "created_at",
            "summary",
        )
        fields = (
            "id",
            "title",
            "created_by",
            "created_at",
            "ended_at",
            "summary",
            "parent_mlalgorithm_1",
            "parent_mlalgorithm_2",
            )