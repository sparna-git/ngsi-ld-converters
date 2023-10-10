import sys, os
import pathlib, logging, json, argparse
from rdflib import Graph
from pyshacl.rules import gather_rules, apply_rules
from pyshacl import ShapesGraph
from pyld import jsonld
from pyld.documentloader import requests
from pathlib import Path

class transformToJson():

	def __init__(self, graph_rules, frame, logger) -> object:

		self.graph_rules = graph_rules
		self.frame = frame
		self.logger = logger

	def apply_rules_graph(self,rules_graph, data_graph):


		# Créer un Shape objet à partir de l'objet Graph
		self.logger.info("Shape Graph")
		shape_graph = ShapesGraph(rules_graph, True, None)
		self.logger.info(shape_graph)

		## This property getter triggers shapes harvest.
		shape_graph.shapes
		
		# Get all rules
		rules = gather_rules(shape_graph,True)
		self.logger.info(rules)

		# Apply rules
		nbNewStatements = apply_rules(rules, data_graph,False)
		if nbNewStatements == 0:
			self.logger.warning("not include statement. ")
		else:
			self.logger.info("Added "+str(nbNewStatements)+" new statements")

	def normalize_graph_json(self,data_graph):

		#convert the data grap to json-ld
		graphSerialize = data_graph.serialize(format='json-ld')
				
		# Log
		self.logger.info("Graph serialize in Turtle")
		self.logger.info(data_graph.serialize(format='turtle'))
		
		self.logger.info("Graph serialize in jsonld")
		self.logger.info(graphSerialize)

		# return json-ld output
		return graphSerialize
	
	def loader(self,*args, **kwargs):

		requests_loader = requests.requests_document_loader(*args, **kwargs)

		def loader(url,options={}):
			return requests_loader(url, options={"header":'application/ld+json, application/json;q=0.5'})
		return loader
	
	def transform(self, data_graph) -> jsonld:

		self.datagraph = data_graph

		self.logger.info("Step 1: Apply rules")
		self.apply_rules_graph(self.graph_rules, self.datagraph)
		self.logger.info("Step 2: Normalize data graph to json structure")
		graph_json = json.loads(self.normalize_graph_json(self.datagraph))
		self.logger.info(graph_json)
		
		# Framed with pyLD
		self.logger.info("Document Loader.......")
		jsonld.set_document_loader(self.loader())
		self.logger.info(jsonld.set_document_loader(self.loader()))

		self.logger.info("Step 4: the framed JSON-LD output.")
		output_frame = jsonld.frame(graph_json, self.frame)
		self.logger.info(json.dumps(output_frame,indent=2))

		self.logger.info("Step 5: Normalize JSON-LD to n-quads")
		# Normalized  jsonld.normalize(frame, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
		json_Normalize = jsonld.normalize(graph_json,{'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
		self.logger.info(json_Normalize)

		# output json framing file
		return json.dumps(output_frame, indent=2)