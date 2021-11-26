"""

WSGI config for DDOS_Detection project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/

"""

from Applications.Machine_Learning.DDOS_Classifier.random_forest_classifier import RandomForestClassifier
from Applications.Machine_Learning.registry import MLRegistry
import inspect
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DDOS_Detection.settings')

application = get_wsgi_application()


# from Applications.Machine_Learning.DDOS_Classifier.extra_trees import ExtraTreesClassifier # import ExtraTrees ML algorithm

try:
    registry = MLRegistry()  # create ML registry
    # Random Forest classifier
    rf = RandomForestClassifier()
    # add to ML registry
    registry.add_algorithm(endpoint_name="ddos_classifier",
                           algorithm_object=rf,
                           algorithm_name="random forest",
                           algorithm_status="production",
                           algorithm_version="0.0.1",
                           owner="Patrick Gatiri X Karanja Mbuthia",
                           algorithm_description="Random Forest with simple pre- and post-processing",
                           algorithm_code=inspect.getsource(RandomForestClassifier))
    '''
    # Extra Trees classifier
    et = ExtraTreesClassifier()
    # add to ML registry
    registry.add_algorithm(endpoint_name="ddos_classifier",
                            algorithm_object=et,
                            algorithm_name="extra trees",
                            algorithm_status="testing",
                            algorithm_version="0.0.1",
                            owner="Mark Silla",
                            algorithm_description="Extra Trees with simple pre- and post-processing",
                            algorithm_code=inspect.getsource(ExtraTreesClassifier))
    '''

except Exception as e:
    print("Exception while loading the algorithms to the registry,", str(e))
