import json
from rdflib import Graph

from pyshacl import ShapesGraph
from pyld import jsonld
from pyld.documentloader import requests
# library for rules
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type, Union 

from pyshacl.pytypes import GraphLike
from pyshacl.shape import Shape

from sparql_custom import SPARQLRule_Custom

from pyshacl.consts import RDF_type, SH_rule, SH_SPARQLRule, SH_TripleRule
from collections import defaultdict

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
		#rules = gather_rules(shape_graph,True)
		rules = gather_rules_custom(shape_graph,True)
		self.logger.info(rules)

		# Apply rules
		#bNewStatements = apply_rules(rules, data_graph,False)
		r = apply_rules_custom(rules, data_graph,False)
		nbStatements, result_graph = r

		#nbNewStatements, gresult = rules_custom.apply_rules_custom(rules, data_graph,False)
		if nbStatements == 0:
			self.logger.warning("not include statement. ")
		else:
			self.logger.info("Added "+str(nbStatements)+" new statements")

		return result_graph.serialize(format="turtle")

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
		result_sparql = self.apply_rules_graph(self.graph_rules, self.datagraph)
		self.logger.info(result_sparql)

		
		graph_json = json.loads(self.normalize_graph_json(self.datagraph))
		
		
		# Framed with pyLD
		#self.logger.info("Document Loader.......")
		jsonld.set_document_loader(self.loader())
		#self.logger.info(jsonld.set_document_loader(self.loader()))

		self.logger.info("Step 4: the framed JSON-LD output.")
		output_frame = jsonld.frame(graph_json, self.frame)
		self.logger.info(json.dumps(output_frame,indent=2))

		self.logger.info("Step 5: Normalize JSON-LD to n-quads")
		# Normalized  jsonld.normalize(frame, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
		json_Normalize = jsonld.normalize(graph_json,{'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
		self.logger.info(json_Normalize)

		# output json framing file
		return json.dumps(output_frame, indent=2)


def gather_rules_custom(shacl_graph: 'ShapesGraph', iterate_rules=False) -> Dict['Shape', List['SHACLRule']]:
    """

    :param shacl_graph:
    :type shacl_graph: ShapesGraph
    :return:
    :rtype: Dict[Shape, List[SHACLRule]]
    """
    triple_rule_nodes = set(shacl_graph.subjects(RDF_type, SH_TripleRule))
    sparql_rule_nodes = set(shacl_graph.subjects(RDF_type, SH_SPARQLRule))
    if shacl_graph.js_enabled:
        from pyshacl.extras.js.rules import JSRule, SH_JSRule

        js_rule_nodes = set(shacl_graph.subjects(RDF_type, SH_JSRule))
        use_JSRule: Union[bool, Type] = JSRule
    else:
        use_JSRule = False
        js_rule_nodes = set()
    overlaps = triple_rule_nodes.intersection(sparql_rule_nodes)

    if len(overlaps) > 0:
        raise RuleLoadError(
            "A SHACL Rule cannot be both a TripleRule and a SPARQLRule.",
            "https://www.w3.org/TR/shacl-af/#rules-syntax",
        )
    overlaps = triple_rule_nodes.intersection(js_rule_nodes)
    if len(overlaps) > 0:
        raise RuleLoadError(
            "A SHACL Rule cannot be both a TripleRule and a JSRule.",
            "https://www.w3.org/TR/shacl-af/#rules-syntax",
        )
    overlaps = sparql_rule_nodes.intersection(js_rule_nodes)
    if len(overlaps) > 0:
        raise RuleLoadError(
            "A SHACL Rule cannot be both a SPARQLRule and a JSRule.",
            "https://www.w3.org/TR/shacl-af/#rules-syntax",
        )

    
    used_rules = shacl_graph.subject_objects(SH_rule)
    ret_rules = defaultdict(list)
    for sub, obj in used_rules:
        try:
            shape: Shape = shacl_graph.lookup_shape_from_node(sub)            
        except (AttributeError, KeyError):
            print(AttributeError)
            print(KeyError)
            raise RuleLoadError(
                "The shape that rule is attached to is not a valid SHACL Shape.",
                "https://www.w3.org/TR/shacl-af/#rules-syntax",
            )
        if obj in triple_rule_nodes:
            rule: SHACLRule = TripleRule(shape, obj, iterate=iterate_rules)            
        elif obj in sparql_rule_nodes:
            '''
            	Update for use a library custom
            '''
            rule = SPARQLRule_Custom(shape, obj)
            
        elif use_JSRule and callable(use_JSRule) and obj in js_rule_nodes:
            rule = use_JSRule(shape, obj)
        else:
            raise RuleLoadError(
                "when using sh:rule, the Rule must be defined as either a TripleRule or SPARQLRule.",
                "https://www.w3.org/TR/shacl-af/#rules-syntax",
            )
        ret_rules[shape].append(rule)       

    return ret_rules

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
            	n_modified, g = r.apply_custom(data_graph)
            	this_modified += n_modified
            	collect_graph += g
            if this_modified > 0:
            	nbStatements += this_modified
            	result_graph += collect_graph
            	if iterate:
            		continue
            	else:
            		break
            break
        
    return nbStatements, result_graph