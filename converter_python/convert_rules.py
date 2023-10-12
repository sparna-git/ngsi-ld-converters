import os
import pathlib, logging, json, argparse
from rdflib import Graph
from pathlib import Path
from convert_shacl_json import transformToJson 

graph_rules = '''
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix swa: <http://topbraid.org/swa#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dct: <http://purl.org/dc/terms/>.
@prefix this: <http://data.sparna.fr/ontologies/datacube-2-statdcatap#> .

<http://data.sparna.fr/ontologies/datacube-2-statdcatap>
  rdf:type owl:Ontology ;
  rdfs:label "Datacube 2 STAT-DCAT-AP ruleset"@en;
  rdfs:comment """Converts a Datacube Description to STAT-DCAT-AP"""@en;
  sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://www.w3.org/2000/01/rdf-schema#"^^xsd:anyURI ;
      sh:prefix "rdfs" ;
    ] ;
  sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://www.w3.org/2002/07/owl#"^^xsd:anyURI ;
      sh:prefix "owl" ;
    ] ;
   sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://www.w3.org/ns/shacl#"^^xsd:anyURI ;
      sh:prefix "sh" ;
    ] ;
  sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://www.w3.org/2001/XMLSchema#"^^xsd:anyURI ;
      sh:prefix "xsd" ;
    ] ;
   sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://www.w3.org/1999/02/22-rdf-syntax-ns#"^^xsd:anyURI ;
      sh:prefix "rdf" ;
    ] ;
    sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://datashapes.org/dash#"^^xsd:anyURI ;
      sh:prefix "dash" ;
    ] ;
    sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://purl.org/linked-data/cube#"^^xsd:anyURI ;
      sh:prefix "qb" ;
    ] ;
    sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://www.w3.org/ns/dcat#"^^xsd:anyURI ;
      sh:prefix "dcat" ;
    ] ;
    sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://purl.org/dc/terms/"^^xsd:anyURI ;
      sh:prefix "dct" ;
    ] ;
    sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "https://uri.etsi.org/ngsi-ld/"^^xsd:anyURI ;
      sh:prefix "ngsild" ;
    ] ;
    sh:declare [
      rdf:type sh:PrefixDeclaration ;
      sh:namespace "http://data.europa.eu/m8g/"^^xsd:anyURI ;
      sh:prefix "core" ;
    ] ;
.


this:DataStructureDefinition_Shape
  rdf:type sh:NodeShape ;
  # Create DCAT Dataset
  sh:rule this:CreateDataset;
  # reifies properties
  sh:rule this:reify_dctLanguage;
  sh:rule this:reify_dctDescription;
  # other rules
  sh:rule this:rdfsLabelOrDctTitle2dctTitle;
  sh:rule this:qbDimension2coreDimension;
  sh:rule this:qbAttribute2coreAttribute;
  sh:rule this:qbMeasure2coreStatUnitMeasure;
  # copy everythingElse
  sh:rule this:copyEverythingElse;

  sh:target [
      rdf:type sh:SPARQLTarget ;
      sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
      sh:select """
SELECT ?this
WHERE {
	?this a qb:DataStructureDefinition .
}""" ;
    ] ;
.


this:CreateDataset
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Creates DCAT Dataset" ;
  rdfs:label "Creates DCAT Dataset" ;
  sh:construct """
      CONSTRUCT {
        $this a dcat:Dataset .
      }
      WHERE {
        $this a qb:DataStructureDefinition .
      }
      """ ;
  sh:order 1 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

this:rdfsLabelOrDctTitle2dctTitle
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Generates dct:title from rdfs:label or dct:title" ;
  rdfs:label "Generates dct:title" ;
  sh:construct """
      CONSTRUCT {
        $this dct:title _:p .
        _:p a ngsild:LanguageProperty .
        _:p ngsild:languageMap ?x .
      }
      WHERE {
        # prevent a result to be generated if none is present
        $this dct:title|rdfs:label ?anything .
        OPTIONAL { $this dct:title ?dctTitle . }
        OPTIONAL { $this rdfs:label ?rdfsLabel . }
        BIND(COALESCE(?dctTitle, ?rdfsLabel) AS ?x)
      }
      """ ;
  sh:order 2 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

this:reify_dctLanguage
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Reifies dct:language as an ngsi-ld Property" ;
  rdfs:label "Reifies dct:language" ;
  sh:construct """
      CONSTRUCT {
        $this dct:language _:p .
        _:p a ngsild:Property .
        _:p ngsild:hasValue ?language .
      }
      WHERE {
        $this dct:language ?language .
      }
      """ ;
  sh:order 2 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

this:reify_dctDescription
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Reifies dct:description as an ngsi-ld Property" ;
  rdfs:label "Reifies dct:description" ;
  sh:construct """
      CONSTRUCT {
        $this dct:description _:p .
        _:p a ngsild:Property .
        _:p ngsild:hasValue ?description .
      }
      WHERE {
        $this dct:description ?description .
      }
      """ ;
  sh:order 2 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.




this:qbDimension2coreDimension
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Generates core:dimension from qb:component/qb:dimension" ;
  rdfs:label "Generates core:dimension" ;
  sh:construct """
      CONSTRUCT {
        $this core:dimension _:p .
        _:p a ngsild:Relationship .
        _:p ngsild:hasObject ?x .
      }
      WHERE {
        $this qb:component/qb:dimension ?x .
      }
      """ ;
  sh:order 3 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

this:qbAttribute2coreAttribute
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Generates core:attribute from qb:component/qb:attribute" ;
  rdfs:label "Generates core:attribute" ;
  sh:construct """
      CONSTRUCT {
        $this core:attribute _:p .
        _:p a ngsild:Relationship .
        _:p ngsild:hasObject ?x .
      }
      WHERE {
        $this qb:component/qb:attribute ?x .
      }
      """ ;
  sh:order 3 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

this:qbMeasure2coreStatUnitMeasure
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Generates core:statUnitMeasure from qb:component/qb:measure" ;
  rdfs:label "Generates core:statUnitMeasure" ;
  sh:construct """
      CONSTRUCT {
        $this core:statUnitMeasure _:p .
        _:p a ngsild:Relationship .
        _:p ngsild:hasObject ?x .
      }
      WHERE {
        $this qb:component/qb:measure ?x .
      }
      """ ;
  sh:order 3 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.


this:copyEverythingElse
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Copies everything else as-is" ;
  rdfs:label "Copies everything else as-is" ;
  sh:construct """
      CONSTRUCT { $this ?p ?o . }
      WHERE {
        $this ?p ?o . 
        FILTER(
          ?p NOT IN(
            rdf:type,
            qb:component,
            qb:sliceKey,
            rdfs:label,
            dct:title,
            dct:language,
            dct:description
          )
          &&
          !STRSTARTS(STR(?p), "http://rdf.insee.fr/def/base#")
        )
      }
      """ ;
  sh:order 4 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.




this:DimensionProperty_Shape
  rdf:type sh:NodeShape ;
  # Create DimensionProperty
  sh:rule this:CreateDimensionProperty;
  # reifies properties
  sh:rule this:reify_rdfsLabel;
  sh:rule this:reify_dctLanguage;
  sh:rule this:reify_dctDescription;
  sh:rule this:reify_qbCodeList;
  sh:rule this:reify_qbConcept;
  # copy everythingElse
  sh:rule this:copyEverythingElse_dimensionProperty;

  sh:target [
      rdf:type sh:SPARQLTarget ;
      sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
      sh:select """
SELECT ?this
WHERE {
  ?this a qb:DimensionProperty .
}""" ;
    ] ;
.

this:CreateDimensionProperty
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Creates DimensionProperty" ;
  rdfs:label "Creates DimensionProperty" ;
  sh:construct """
      CONSTRUCT {
        $this a qb:DimensionProperty .
      }
      WHERE {
        $this a qb:DimensionProperty .
      }
      """ ;
  sh:order 1 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

this:reify_rdfsLabel
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Reifies rdfs:label as an ngsi-ld Property" ;
  rdfs:label "Reifies rdfs:label" ;
  sh:construct """
      CONSTRUCT {
        $this rdfs:label _:p .
        _:p a ngsild:Property .
        _:p ngsild:hasValue ?label .
      }
      WHERE {
        $this rdfs:label ?label .
      }
      """ ;
  sh:order 2 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.


this:reify_qbCodeList
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Reifies qb:codeList" ;
  rdfs:label "Reifies qb:codeList" ;
  sh:construct """
      CONSTRUCT {
        $this qb:codeList _:p .
        _:p a ngsild:Relationship .
        _:p ngsild:hasObject ?x .
      }
      WHERE {
        $this qb:codeList ?x .
      }
      """ ;
  sh:order 3 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

this:reify_qbConcept
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Reifies qb:concept" ;
  rdfs:label "Reifies qb:concept" ;
  sh:construct """
      CONSTRUCT {
        $this qb:concept _:p .
        _:p a ngsild:Relationship .
        _:p ngsild:hasObject ?x .
      }
      WHERE {
        $this qb:concept ?x .
      }
      """ ;
  sh:order 3 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.


this:copyEverythingElse_dimensionProperty
  rdf:type sh:SPARQLRule ;
  rdfs:comment "Copies everything else as-is on DimensionProperty" ;
  rdfs:label "Copies everything else as-is on DimensionProperty" ;
  sh:construct """
      CONSTRUCT { $this ?p ?o . }
      WHERE {
        $this ?p ?o . 
        FILTER(
          ?p NOT IN(
            rdf:type,
            qb:codeList,
            qb:concept,
            rdfs:label,
            dct:title,
            dct:language,
            dct:description
          )
          &&
          !STRSTARTS(STR(?p), "http://rdf.insee.fr/def/base#")
        )
      }
      """ ;
  sh:order 4 ;
  sh:prefixes <http://data.sparna.fr/ontologies/datacube-2-statdcatap> ;
.

'''

graph_data = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xkos: <http://rdf-vocabulary.ddialliance.org/xkos#> .
@prefix qb: <http://purl.org/linked-data/cube#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix insee: <http://rdf.insee.fr/def/base#> .
@prefix sdmx: <http://purl.org/linked-data/sdmx#> .
@prefix sdmx-measure: <http://purl.org/linked-data/sdmx/2009/measure#> .
@prefix sdmx-code: <http://purl.org/linked-data/sdmx/2009/code#> .
@prefix sdmx-concept: <http://purl.org/linked-data/sdmx/2009/concept#> .
@prefix sdmx-attribute: <http://purl.org/linked-data/sdmx/2009/attribute#> .
@prefix sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#> .



<http://bauhaus/structuresDeDonnees/structure/dsd1001> a qb:DataStructureDefinition;
  dct:created "2021-07-01T11:58:08.642"^^xsd:dateTime;
  dct:identifier "dsd1001";
  dct:isRequiredBy "Melodi-Chargement", "Melodi-Diffusion";
  dct:modified "2021-07-01T12:00:31.583"^^xsd:dateTime;
  dct:relation "urn:sdmx:org.sdmx.infomodel.metadatastructure.MetadataStructure=FR1:TOURISME_CAPACITES(1.0)";
  # mapped to dct:title if no dct:title is present
  rdfs:label "Capacités des hébergements touristiques"@fr;
  # ignored
  insee:disseminationStatus <http://id.insee.fr/codes/base/statutDiffusion/PublicGenerique>;
  # ignored
  insee:validationState "Unpublished";
.

"""

frame = """{
  "@context": [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    {
      "dcat": "http://www.w3.org/ns/dcat#",
      "qb": "http://purl.org/linked-data/cube#",
      "dct":  "http://purl.org/dc/terms/",
      "stat": "http://data.europa.eu/xyz/statdcat-ap/",
      "xsd":  "http://www.w3.org/2001/XMLSchema#",
      "core": "http://data.europa.eu/m8g/",
      "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
      "skos": "http://www.w3.org/2004/02/skos/core#",
      "sdmx-dimension": "http://purl.org/linked-data/sdmx/2009/dimension#",
      "sdmx-attribute": "http://purl.org/linked-data/sdmx/2009/attribute#",
      
      "Dataset": "dcat:Dataset",
      "DimensionProperty": "qb:DimensionProperty",
      "LanguageProperty": "ngsi-ld:LanguageProperty",
      "languageMap": {
        "@id": "ngsi-ld:languageMap",
        "@container":"@language"
      },

      "dct:modified": {
        "@type":"xsd:dateTime"
      },
      "dct:created": {
        "@type":"xsd:dateTime"
      }
    }
  ],
  "@type": [ "Dataset", "DimensionProperty" ]
}

"""

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


'''

'''
if __name__ == '__main__':

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
	
	if (args.rules and args.data and  args.frame):

		# read a rule files
		graph_rules_file = Graph().parse(location=args.rules, format="turtle")

		# read a frame file
		open_frame_file = args.frame.open('r')
		frame = json.loads(open_frame_file.read())


		# Create of instance transformToJson
		s = transformToJson(graph_rules_file,frame, logger)

		# read a directory or a file data
		if os.path.isdir(args.data):
			file_list	= [p for p in pathlib.Path(args.data).iterdir() if p.is_file()]
			for f in file_list:
				logger.info("--------------------------------"+str(f)+"--------------------------------")
				#data_file_list.append(Graph().parse(location=f, format="turtle"))
				data_input = Graph().parse(location=f, format="turtle")

				# Call method transform and print the result  
				print(s.transform(data_input))
		elif os.path.isfile(args.data):
			#data_file_list.append(Graph().parse(location=args.data, format="turtle"))
			data_input = Graph().parse(location=args.data, format="turtle")
			# Call method transform and print the result
			print(s.transform(data_input))
		else:
			print("Error")
		
	else:

		'''
			Call the class for start instance 
		'''

		graph_rules = Graph().parse(data=graph_rules, format="turtle")
		data_file_list.append(Graph().parse(data=graph_data, format="turtle"))
		context_frame = json.loads(frame)

		# Create of instance transformToJson
		s = transformToJson(graph_rules,context_frame, logger)
		for data in data_file_list:
			# This line is for the log
			logger.info("----------------------------------------------------------------")
			# Call method transform and print the result  
			print(s.transform(data_file_list))