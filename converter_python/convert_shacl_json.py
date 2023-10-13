import json
from rdflib import Graph

from pyshacl import ShapesGraph
from pyshacl.rules import gather_rules
from pyld import jsonld
from pyld.documentloader import requests

# library for rules
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type, Union 

from pyshacl.pytypes import GraphLike
from pyshacl.shape import Shape

from pyshacl.helper import get_query_helper_cls
from pyshacl.rdfutil import clone_graph

class transformToJson():

	def __init__(self, graph_rules, frame, logger) -> object:

		self.graph_rules = graph_rules
		self.frame = frame
		self.logger = logger

	def apply_rules_graph(self,rules_graph, data_graph):


		# Créer un Shape objet à partir de l'objet Graph
		self.logger.info("Shape Graph")
		shape_graph = ShapesGraph(rules_graph, True, None)
		
		## This property getter triggers shapes harvest.
		shape_graph.shapes
		
		# Get all rules
		rules = gather_rules(shape_graph,True)
		#self.logger.info(rules)

		# Apply rules
		r = apply_rules_custom(rules, data_graph,False)
		nbStatements, result_graph = r

		if nbStatements == 0:
			self.logger.warning("not include statement. ")
		else:
			self.logger.info("Added "+str(nbStatements)+" new statements")

		return result_graph

	def normalize_graph_json(self,data_graph):

		#convert the data grap to json-ld
		graphSerialize = data_graph.serialize(format='json-ld')
				
		# return json-ld output
		return graphSerialize
	
	def loader(self,*args, **kwargs):

		requests_loader = requests.requests_document_loader(*args, **kwargs)

		def loader(url,options={}):
			return requests_loader(url, options={"header":'application/ld+json, application/json;q=0.5'})
		return loader
	
	def complex_encode(object):
	    # check using isinstance method
		if isinstance(object, complex):
			return [object.real, object.imag]
		# raised error using exception handling if object is not complex
		raise TypeError(repr(object) + " is not JSON serialized")

	def transform(self, data_graph) -> jsonld:

		self.datagraph = data_graph

		self.logger.info("Step 1: Apply rules")
		result_sparql = self.apply_rules_graph(self.graph_rules, self.datagraph)
		self.logger.info(result_sparql.serialize(format="turtle"))
		
		graph_json = json.loads(self.normalize_graph_json(result_sparql))
	
		# Framed with pyLD
		#self.logger.info("Document Loader.......")
		jsonld.set_document_loader(self.loader())
		#self.logger.info(jsonld.set_document_loader(self.loader()))

		self.logger.info("Step 4: the framed JSON-LD output.")
		output_frame = jsonld.frame(graph_json, self.frame)
		self.logger.info(output_frame)

		self.logger.info("Step 5: Normalize JSON-LD to n-quads")
		# Normalized  jsonld.normalize(frame, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
		json_Normalize = jsonld.normalize(graph_json,{'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
		self.logger.info(json_Normalize)

		# output json framing file
		output_graph = json.dumps(output_frame,indent=2,ensure_ascii=False)
		return output_frame


def apply_rules_custom(shapes_rules: Dict, data_graph: GraphLike, iterate=False) -> object:
    # short the shapes dict by shapes sh:order before execution

    sorted_shapes_rules: List[Tuple[Any, Any]] = sorted(shapes_rules.items(), key=lambda x: x[0].order)
    nbStatements = 0
    result_graph = Graph() 
    for shape, rules in sorted_shapes_rules:
        # sort the rules by the sh:order before execution
        rules = sorted(rules, key=lambda x: x.order)
        iterate_limit = 100
        while True:
            if iterate_limit < 1:
                raise ReportableRuntimeError("SHACL Shape Rule iteration exceeded iteration limit of 100.")
            iterate_limit -= 1
            this_modified = 0
            collect_graph = Graph()

            for r in rules:
            	if r.deactivated:
            		continue
            	# Code for get the result Sparql query and number of statement
            	n_modified, g = apply_sparql_rules_custom(r,data_graph)
            	this_modified += n_modified
            	collect_graph += g #save the result of graph
            if this_modified > 0:
            	nbStatements += this_modified
            	result_graph += collect_graph
            	if iterate:
            		continue
            	else:
            		break
            break
        
    return nbStatements, result_graph

def apply_sparql_rules_custom(self, data_graph: 'GraphLike'):

		focus_nodes = self.shape.focus_nodes(data_graph)  # uses target nodes to find focus nodes
		all_added = 0
		SPARQLQueryHelper = get_query_helper_cls()
		iterate_limit = 100
		collect_graph = Graph()
		while True:
			if iterate_limit < 1:
				raise ReportableRuntimeError("Local SPARQLRule iteration exceeded iteration limit of 100.")
			iterate_limit -= 1
			added = 0
			applicable_nodes = self.filter_conditions(focus_nodes, data_graph)
			construct_graphs = set()
			gResult = Graph()
			for a in applicable_nodes:
				for c in self._constructs:
					init_bindings = {}
					found_this = SPARQLQueryHelper.bind_this_regex.search(c)
					if found_this:
						init_bindings['this'] = a
					c = self._qh.apply_prefixes(c)
					results = data_graph.query(c, initBindings=init_bindings)
					if results.type != "CONSTRUCT":
						raise ReportableRuntimeError("Query executed by a SHACL SPARQLRule must be CONSTRUCT query.")
					this_added = False
					result_graph = results.graph
					if result_graph is None:
						raise ReportableRuntimeError("Query executed by a SHACL SPARQLRule did not return a Graph.")
					for i in result_graph:
						if not this_added and i not in data_graph:
							this_added = True
							# We only need to know at least one triple was added, then break!
							break
					if this_added:
						added += 1
						construct_graphs.add(result_graph)
						# result in new Graph
						gResult += result_graph
			if added > 0:
				for g in construct_graphs:
					data_graph = clone_graph(g, target_graph=data_graph)                    
				all_added += added
				collect_graph += gResult
				if self.iterate:
					continue  # Jump up to iterate
				else:
					break  # Don't iterate
			break  # We've reached a local steady state
		return all_added, collect_graph