import os
import pathlib, logging, json, argparse
from rdflib import Graph
from pathlib import Path
from JsonLdTransformer import JsonLdTransformer
import pprint

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

if __name__ == '__main__':

	logging.basicConfig(filename=main_log(),level=logging.DEBUG)

	# CLI arguments
	parser = argparse.ArgumentParser(
		prog='Cli',
		description='Converts an input RDF file using SHACL rules, then serializes the result using JSON-LD framing'
	)
	# Add arguments
	parser.add_argument('--r','--rules',help='Path to a input rules file',type=pathlib.Path,dest='rules')
	parser.add_argument('--d','--data',help='directory or file input',type=pathlib.Path,dest='data')
	parser.add_argument('--f','--frame',help='Path to a input JSON file',type=pathlib.Path,dest='frame')
	# Parse args
	args = parser.parse_args()
	
	file_list = []
	data_file_list = []
	output_result_framing = []
	if (args.rules and args.data and args.frame):

		# read a rule files
		graph_rules = Graph().parse(location=args.rules, format="turtle")

		# read JSON-LD framing spec file
		open_frame_file = args.frame.open('r')
		frame = json.loads(open_frame_file.read())

		# Create instance of JsonLdTransformer with rules graph and framing spec
		transformer = JsonLdTransformer(graph_rules,frame)

		# read a directory or a file data
		if os.path.isdir(args.data):
			file_list	= [p for p in pathlib.Path(args.data).iterdir() if p.is_file()]
			for f in file_list:
				logger.info("--------------------------------"+str(f)+"--------------------------------")
				
				data_input = Graph().parse(location=f, format="turtle")

				# Call method transform and print the result  
				output_result_framing.append(transformer.transform(data_input))
				#print(s.transform(data_input))
		
		if os.path.isfile(args.data):
			data_graph = Graph().parse(location=args.data, format="turtle")
			output_result_framing.append(transformer.transform(data_graph))

		if len(output_result_framing) > 0:
			for output in output_result_framing:
				pprint.pprint(output, indent=2)
	
	else:
		parser.print_help()