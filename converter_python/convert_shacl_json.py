import sys
import json
from rdflib import Graph, Namespace
from pyshacl.rules import gather_rules, apply_rules
from pyshacl import ShapesGraph
from pyld import jsonld
from pyld.documentloader import requests
import argparse, pathlib, logging

logging.basicConfig(filename="log.txt",level=logging.DEBUG)
logger = logging.getLogger()

def convert_graph_to_json(shacl_Graph_file,data_Graph_file):

	# Created Graph
	data_graph = Graph().parse(location=data_Graph_file, format="turtle")
	shacl_graph = Graph().parse(location=shacl_Graph_file, format="turtle")
	
	# Créer un objet ShaclGraph à partir de l'objet Graph
	'''
		ShapesGraph(shacl_graph, True, None)
	'''
	shape_graph = ShapesGraph(shacl_graph, True, None)

	# Lire les règles avec gather_rules
	'''
	    gather_rules(shacl_graph: 'ShapesGraph', iterate_rules=False)
	'''

	# Fixed the probleme 
	shape_graph.shapes
	# Get all rules
	rules = gather_rules(shape_graph,True)
	#print(rules)

	#Appliquer les règles sur le graphe de données d'input avec apply_rules
	'''
	    apply_rules(shapes_rules: Dict, data_graph: GraphLike, iterate=False)
	'''
	apply_rules(rules, data_graph,False)
	graphSerialize = data_graph.serialize(format='json-ld')

	return graphSerialize

def loader(*args, **kwargs):

	requests_loader = requests.requests_document_loader(*args, **kwargs)

	def loader(url,options={}):
		logger.info("Loading url :"+ url)
		return requests_loader(url, options={"header":'application/ld+json, application/json;q=0.5'})

	return loader

def write_json_framed(data_output, outputFile:str):

	if data_output:

		with open(outputFile, 'w') as f:
			json.dump(data_output, f,indent=2, sort_keys=True)

# Start process
if __name__ == '__main__':

	# Header arguments
	parser = argparse.ArgumentParser(prog='convert_shacl_json',
                    description='Convert a Graph model to JSON-LD')
	# Add arguments
	parser.add_argument('--r','--rules',help='Path to a input rules file',required=True,type=pathlib.Path,dest='rules')
	parser.add_argument('--d','--data',help='Path to a input data file',required=True,type=pathlib.Path,dest='data')
	parser.add_argument('--f','--frame',help='Path to a input JSON file',required=True,type=pathlib.Path,dest='frame')
	parser.add_argument('--o','--output',help='Path to an output file',required=True,type=str,dest='output')

	#try:
	args = parser.parse_args()

	jsonfile = args.frame.open('r')
	datacontext = json.loads(jsonfile.read())
	
	# Get the json from Graph
	logger.info("Step 1: (Get Graph serialize with JSON structure output)")
	graph_json = json.loads(convert_graph_to_json(args.rules,args.data))
	logger.info(json.dumps(graph_json,indent=2))

	# Framed with pyLD
	#jsonld.set_document_loader(loader())
	logger.info("Step 2: the framed JSON-LD output")
	jsonld.set_document_loader(loader())
	output_frame = jsonld.frame(graph_json, datacontext)
	logger.info(output_frame)
	

	logger.info("Step 3: Normalize JSON")
	# Normalized  jsonld.normalize(frame, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
	json_Normalize = jsonld.normalize(graph_json,{'algorithm': 'URDNA2015'})
	logger.info(json.dumps(graph_json,indent=2))

	write_json_framed(output_frame,args.output)

	#except Exception as e:
	#	parser.print_help()