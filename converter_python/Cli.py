import os
import pathlib, logging, json, argparse
from rdflib import Graph
from pathlib import Path
from JsonLdSerializer import JsonLdSerializer 
import pprint

def main_log():
	# directory
	_path_app = os.getcwd()
	# Log
	dirrectory_log = os.path.join(_path_app, "log")
	if not os.path.exists(dirrectory_log):
		# delete fole
		os.mkdir(dirrectory_log)
	else:
		for f in os.listdir(dirrectory_log):
			file = os.path.join(dirrectory_log, f)
			os.remove(file)

	dir_log = os.path.join(dirrectory_log,'log.txt')

	return dir_log

if __name__ == '__main__':

	'''
		loggin is the library for save all step in a log file

		- use the method main_log for config the path and create à folder 
	'''
	logging.basicConfig(filename=main_log(),level=logging.INFO)
	logger = logging.getLogger()

	# Header arguments
	parser = argparse.ArgumentParser(prog='convert_shacl_json',
										description='Convert a Graph rules to JSON Framing ')
	# Add arguments
	parser.add_argument('--r','--rules',help='Path to a input rules file',type=pathlib.Path,dest='rules')
	parser.add_argument('--d','--data',help='directory or file input',type=pathlib.Path,dest='data')
	parser.add_argument('--f','--frame',help='Path to a input JSON file',type=pathlib.Path,dest='frame')
	#try:
	args = parser.parse_args()
	
	file_list = []
	data_file_list = []
	output_result_framing = []
	if (args.rules and args.data and  args.frame):

		# read a rule files
		graph_rules_file = Graph().parse(location=args.rules, format="turtle")

		# read a frame file
		open_frame_file = args.frame.open('r')
		frame = json.loads(open_frame_file.read())

		# Generate instance
		s = JsonLdSerializer(graph_rules_file,frame, logger)

		# read a directory or a file data
		if os.path.isdir(args.data):
			file_list	= [p for p in pathlib.Path(args.data).iterdir() if p.is_file()]
			for f in file_list:
				logger.info("--------------------------------"+str(f)+"--------------------------------")
				
				data_input = Graph().parse(location=f, format="turtle")

				# Call method transform and print the result  
				output_result_framing.append(s.transform(data_input))
				#print(s.transform(data_input))
		if os.path.isfile(args.data):
			data_input = Graph().parse(location=args.data, format="turtle")
			output_result_framing.append(s.transform(data_input))

		if len(output_result_framing) > 0:
			for output in output_result_framing:
				pprint.pprint(output, indent=2)
	else:
		parser.print_help()