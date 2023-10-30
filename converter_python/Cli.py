import os
import pathlib
import logging
import json
import argparse
from rdflib import Graph
from JsonLdTransformer import JsonLdTransformer

logger = logging.getLogger(__name__)

def main_log():
	# current directory
	_path_app = os.getcwd()
	
	# log folder
	directory_log = os.path.join(_path_app, "log")
	# create folder if it does not exist
	if not os.path.exists(directory_log):
		os.mkdir(directory_log)
	else:
		# otherwise delete all files in it
		for f in os.listdir(directory_log):
			file = os.path.join(directory_log, f)
			os.remove(file)

	dir_log = os.path.join(directory_log,'log.txt')

	return dir_log

def write_file(outputfile,result):

	with open(outputfile,'w') as wfile:
		json.dump(result,wfile,indent=2, sort_keys=True)


if __name__ == '__main__':

	logging.basicConfig(filename=main_log(),level=logging.DEBUG)

	# CLI arguments
	parser = argparse.ArgumentParser(
		prog='Cli',
		description='Converts an input RDF file using SHACL rules, then serializes the result using JSON-LD framing'
	)
	# Add arguments
	parser.add_argument('--r','--rules',help='Path to a input rules file', required=True,type=pathlib.Path,dest='rules')
	parser.add_argument('--d','--data',help='Path to a input file', required=True,type=pathlib.Path,dest='data')
	parser.add_argument('--f','--frame',help='Path to a input JSON file', required=True,type=pathlib.Path,dest='frame')
	parser.add_argument('--o','--output',help='output JSON file', required=True,dest='outputFile')
	# Parse args
	args = parser.parse_args()
	
	if (args.rules and args.data and args.frame):

		# read a rule files
		graph_rules = Graph().parse(location=args.rules)

		# read JSON-LD framing spec file
		open_frame_file = args.frame.open('r')
		frame = json.loads(open_frame_file.read())

		# Create instance of JsonLdTransformer with rules graph and framing spec
		transformer = JsonLdTransformer(graph_rules,frame)

		if os.path.isfile(args.data):
			# Read data file
			data_graph = Graph().parse(location=args.data)

			# 
			result = transformer.transform(data_graph)

			# Write the result
			if result:
				write_file(args.outputFile,result)			
	else:
		parser.print_help()