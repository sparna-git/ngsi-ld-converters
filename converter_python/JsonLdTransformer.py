import logging, json
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


logger = logging.getLogger(__name__)

class JsonLdTransformer():
	"""
	A class that transforms an input Graph using SHACL rules and serializes
	the transformation result in pretty JSON-LD using a JSON-LD framing specification.
	"""

	def __init__(self, graph_rules: Graph, frame: Dict):
		"""
		Parameters
		----------
		graph_rules : Graph
			The Graph containing the SHACL rules
		frame : Dict
			The JSON-LD framing specification
		"""

		self.graph_rules = graph_rules
		self.frame = frame

		# Loads the rules graph
		logger.info("Shape Graph")
		shapes_graph = ShapesGraph(graph_rules, True, None)
		
		# This property getter triggers shapes harvest.
		# It is necessary to call it prior to calling gather_rules
		shapes_graph.shapes

		# loads the rules from the SHACL rules file
		self.rules = gather_rules(shapes_graph,True)


	def apply_rules_graph(self, data_graph: Graph) -> Graph:
		"""
		Applies the SHACL rules on the given data_graph, and returns the result Graph
		The result Graph contains only the triples that result from executing the rules
		"""

		# Apply rules
		nbStatements, result_graph = apply_rules(self.rules, data_graph, False)

		if nbStatements == 0:
			logger.warning("No statements were generated from the rules")
		else:
			logger.info("Created "+str(nbStatements)+" statements from rules")

		return result_graph
	
	def transform(self, data_graph: Graph) -> Dict:
		"""
		Transforms the input data_graph using the SHACL rules, and serializes it using
		the JSON-LD framing spec. This is the main method to be called from the outside.
		"""

		logger.info("Step 1: Apply rules")
		result_sparql = self.apply_rules_graph(data_graph)
		logger.debug(result_sparql.serialize(format="turtle"))
		
		logger.info("Step 2: Serialize rules output in JSON-LD (raw)")
		jsonSerialization = result_sparql.serialize(format='json-ld')
		graph_json = json.loads(jsonSerialization)

		# sets a document loader on the jsonld lib
		# even if we don't use it right now
		jsonld.set_document_loader(self.__buildDocumentLoader())
		
		logger.info("Step 3: frame the raw JSON-LD serialization.")
		output_frame = jsonld.frame(graph_json, self.frame)
		logger.debug(output_frame)

		# output result of framing
		return output_frame

	
	def __buildDocumentLoader(self,*args, **kwargs):
		"""
		Builds a document loader to pass to jsonld lib.
		For the moment, returns a default document loader.
		This is where we could adjust request headers to fetch context, or
		this is also where we could default to a local cached file, if needed
		"""

		requests_loader = requests.requests_document_loader(*args, **kwargs)

		def loader(url,options={}):
			# for the moment, just reuse the default loader
			return requests_loader(url, options)
			# This is where we could adjust request headers to fetch context e.g.
			# return requests_loader(url, options={"header":'application/ld+json, application/json;q=0.5'})
		
		return loader


def apply_rules(shapes_rules: Dict, data_graph: GraphLike, iterate=False) -> Graph:
    """
    This is a copy of pyshacl apply_rules_custom with a different behavior : 
    while pyshacl uses SHACL rules to make inference, and adds the resulting triples in the 
    same input graph, this method actually *returns* a new Graph containing the resulting
    triples.
    """

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
            	n_modified, g = apply_sparql_rule(r,data_graph)
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

def apply_sparql_rule(rule: SPARQLRule, data_graph: GraphLike) -> Graph:
	"""
	This is a copy of pyshacl apply_sparql_rules method, the difference being that
	it *returns* the result of applying the rules in a new Graph instead of adding the triples
	in the input Graph object.
	"""	

	focus_nodes = rule.shape.focus_nodes(data_graph)  # uses target nodes to find focus nodes
	all_added = 0
	SPARQLQueryHelper = get_query_helper_cls()
	iterate_limit = 100
	collect_graph = Graph()
	while True:
		if iterate_limit < 1:
			raise ReportableRuntimeError("Local SPARQLRule iteration exceeded iteration limit of 100.")
		iterate_limit -= 1
		added = 0
		applicable_nodes = rule.filter_conditions(focus_nodes, data_graph)
		construct_graphs = set()
		gResult = Graph()
		for a in applicable_nodes:
			for c in rule._constructs:
				init_bindings = {}
				found_this = SPARQLQueryHelper.bind_this_regex.search(c)
				if found_this:
					init_bindings['this'] = a
				c = rule._qh.apply_prefixes(c)
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
			if rule.iterate:
				continue  # Jump up to iterate
			else:
				break  # Don't iterate
		break  # We've reached a local steady state
	return all_added, collect_graph