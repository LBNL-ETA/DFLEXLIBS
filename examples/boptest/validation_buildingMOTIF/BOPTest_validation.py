#%%
import yaml
from rdflib import Namespace
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model, Library
from buildingmotif.namespaces import BRICK # import this to make writing URIs easier

class ValidationInterface:
    def __init__(self, config_path, manifest_path):

        '''Interface for buildingMOTIF to run semantic sufficiency validation
        '''   
        try:
            with open(config_path) as fp:
                config = yaml.safe_load(fp)
        except Exception as e:
            print('Error reading configuration file')
            print(e)

        # Define graph path
        self.graph_path = config['graph_path']

        # Define manifest path
        self.manifest_path = manifest_path

    def validate(self):
    
        # in-memory instance
        bm = BuildingMOTIF("sqlite://")

        # create the namespace for the building
        BLDG = Namespace('urn:bldg/')


        # create the building model
        model = Model.create(BLDG, description="This is a test model for a simple building")

        print(model.graph.serialize())


        # load test case model
        model.graph.parse(self.graph_path, format="ttl")


        # load libraries included with the python package
        constraints = Library.load(ontology_graph="../../buildingmotif/libraries/constraints/constraints.ttl")

        # load libraries excluded from the python package (available from the repository)
        brick = Library.load(ontology_graph="validation_buildingMOTIF/Brick-subset.ttl")

        # pass a list of shape collections to .validate()
        validation_result = model.validate([brick.get_shape_collection()])
        print(f"Model is valid? {validation_result.valid}")

            
        # load manifest into BuildingMOTIF as its own library!
        manifest = Library.load(ontology_graph = self.manifest_path)

        # gather shape collections into a list for ease of use
        shape_collections = [
            brick.get_shape_collection(),
            constraints.get_shape_collection(),
            manifest.get_shape_collection(),
        ]

        # pass a list of shape collections to .validate()
        validation_result = model.validate(shape_collections)
        print(f"Model is valid? {validation_result.valid}")


        # print reasons
        for diff in validation_result.diffset:
            print(f" - {diff.reason()}")



   