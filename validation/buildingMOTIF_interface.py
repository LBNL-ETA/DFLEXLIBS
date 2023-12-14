#%%
import yaml
from rdflib import Namespace
from buildingmotif import BuildingMOTIF
from buildingmotif.dataclasses import Model, Library
from buildingmotif.namespaces import BRICK # import this to make writing URIs easier
from tabulate import tabulate
import json

class ValidationInterface:
    def __init__(self, model_path, manifest_paths):

        '''Interface for buildingMOTIF to run semantic sufficiency validation
        '''   

        # Define graph path
        self.graph_path = model_path

        # Define manifest path
        self.manifest_paths = manifest_paths

    def validate(self):
    
        table_data = []
        suitable_kpis = []

        # Iterate over manifest paths and validate each one
        for key, manifest_path in self.manifest_paths.items():

            # in-memory instance
            bm = BuildingMOTIF("sqlite://")

            # create the namespace for the building
            BLDG = Namespace('urn:bldg/')


            # create the building model
            model = Model.create(BLDG, description="This is a test model for a simple building")

            # load test case model
            model.graph.parse(self.graph_path, format="ttl")

            #print(model.graph.serialize())

            # load libraries included with the python package
            constraint = Library.load(ontology_graph="constraints.ttl")
            #print(constraint)

            # load libraries excluded from the python package (available from the repository)
            brick = Library.load(ontology_graph="Brick-subset.ttl")

            # pass a list of shape collections to .validate()
            validation_result = model.validate([brick.get_shape_collection()])
            #print(f"Model is valid? {validation_result.valid}")

            # load manifest into BuildingMOTIF as its own library!
            manifest = Library.load(ontology_graph=manifest_path)
            #print(manifest_path)
            #print(manifest)
            # gather shape collections into a list for ease of use
            shape_collections = [
                brick.get_shape_collection(),
                constraint.get_shape_collection(),
                manifest.get_shape_collection(),
            ]

            # pass a list of shape collections to .validate()
            validation_result = model.validate(shape_collections)

            # Append a row to the table with validation result and key
            row = [key, validation_result.valid]

            if validation_result.valid == True:
                suitable_kpis.append({key})

            # Add reasons for each diff if available
            for diff in validation_result.diffset:
                print (f" For KPI {key} - {diff.reason()}") 

            #print(f"KPI: {key}, Validation Result: {validation_result.valid}")

            # Append the row to the overall table data
            table_data.append(row)


        # Print the table without headers
        print(tabulate(table_data, headers=["KPI", "Brick model validation result"], tablefmt="fancy_grid"))

        return suitable_kpis    
    
    def get_results(self):
        validation_table = []
        suitable_kpis = []
        non_suitable_reason = []

                # Iterate over manifest paths and validate each one
        for key, manifest_path in self.manifest_paths.items():

            # in-memory instance
            bm = BuildingMOTIF("sqlite://")

            # create the namespace for the building
            BLDG = Namespace('urn:bldg/')


            # create the building model
            model = Model.create(BLDG, description="This is a test model for a simple building")

            # load test case model
            model.graph.parse(self.graph_path, format="ttl")

            #print(model.graph.serialize())

            # load libraries included with the python package
            constraint = Library.load(ontology_graph="constraints.ttl")

            # load libraries excluded from the python package (available from the repository)
            brick = Library.load(ontology_graph="Brick-subset.ttl")

            # pass a list of shape collections to .validate()
            validation_result = model.validate([brick.get_shape_collection()])
            #print(f"Model is valid? {validation_result.valid}")

            # load manifest into BuildingMOTIF as its own library!
            manifest = Library.load(ontology_graph=manifest_path)
            #print(manifest_path)
            #print(manifest)
            # gather shape collections into a list for ease of use
            shape_collections = [
                brick.get_shape_collection(),
                constraint.get_shape_collection(),
                manifest.get_shape_collection(),
            ]

            # pass a list of shape collections to .validate()
            validation_result = model.validate(shape_collections)


            # Append a row to the table with validation result and key
            row = [key, validation_result.valid]

            if validation_result.valid == True:
                suitable_kpis.append(key)

            # Add reasons for each diff if available
            for diff in validation_result.diffset:
                non_suitable_reason.append([key, diff.reason()]) 

            # Append the row to the overall table data
            validation_table.append(row)

        # Prepare a dictionary with table data and suitable KPIs
        results_dict = {
            "validation_table": validation_table,
            "suitable_kpis": list(suitable_kpis),
            "non_suitable_kpis": non_suitable_reason
        }

        # Convert the dictionary to JSON format
        json_results = json.dumps(results_dict, indent=2)

        # Print the JSON data
        print(json_results)

        return json_results