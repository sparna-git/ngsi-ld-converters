# ngsi-ld-converters

Existing FIWARE converter documentation : 
- https://github.com/flopezag/IoTAgent-Turtle
- https://github.com/INTERSTAT/Statistics-Contextualized/tree/main/pilots/Deliverable%203.2#sdmx-to-etsi-ngsi-ld

Smart data models :
- https://www.fiware.org/smart-data-models/ et https://smartdatamodels.org/
- STAT-DCAT-AP data model : https://github.com/smart-data-models/dataModel.STAT-DCAT-AP

DCAT problematics pointers :
- https://hackmd.io/@WeYQtPurSw-OcPBBOdwKLQ/HkB1jchXs

# Questions / remarks

- In existing converter, why are some properties reified (dct:description), and some not (dct:title, dct:identifier) ?

The problem is that some properties are defined in different contexts. There is a solution to correct it if inside 
the Smart Data Models Subject, we define unambiguously the property to be used in the scope of this subject. Then, 
we could dismiss the use of prefix in the JSON-LD. 

It also means that the IoTAgent-Turtle need to make an update to align with this approach. We have started to modify 
the Data Models to reflect it and afterwards we will plan the steps to modify the parser with the new version of the 
data models.


- In existing converter, why is URI mapped to dct:title and why is rdfs:label mapped to dct:description ?

First, it seems that something is missing in the question regarding the dct:title.
We are mapping the SDMX into DCAT-AP/statDCAT-AP, this is the reason why we map rdfs:label to dct:description.

- Existing converter generates separate files in the output. Is there a reason for this ? could the output be in a
single file ?

ETSI NGSI-LD API defines the world based on entities. NGSI-LD Entity is the informational representative of something 
that is supposed to exist in the real world, physically or conceptually. Each of the data models are making reference 
to a concrete Entity and they are sent to the FIWARE Context Brokers using different Entities that in the end are 
different files.


- The STAT-DCAT-AP json-ld context at https://smart-data-models.github.io/dataModel.STAT-DCAT-AP/context.jsonld maps 
keys to wrong URIs. Is it intended ? This is a blocking issue as it forces us to use these URIs (and not the typical 
dct ones) so that we can then regenerate a JSON-LD valid according to the spec.

In the context.jsonld there are automatically generated IRI based on the smart data models domain. These IRIs are 
provided for all terms and lead to a web page with basic information about the term, definition, data type, and data 
models where the term is also used. Now in some subjects, there is a complementary file ‘notes_context.jsonld’ with 
the original IRI whenever they are available. In order to create the proper context (with the original IRI) there is a 
service at the front page of smartdatamodels.org home -> tools -> map @context with external ontologies that whenever 
it detects a notes_context.jsonld file, make the change from the original terms producing a original @context.

  - I have the feeling that the JSON-LD context of StatDCAT-AP is incomplete; it does not contain the classes 
  documented at https://github.com/INTERSTAT/Statistics-Contextualized/tree/main/pilots/Deliverable%203.2#dcat-ap-data-models

Not all StatDCAT-AP is used in the project and only those classes used in the project have been mapped. Keep in mind 
that the Smart Data Models program is based on real cases and therefore, we define the data models to cover those real 
cases. For those classes, It should have all the first-level terms in the context.jsonld, because it is generated 
automatically, but errors in the scripts are always possible if you could be more precise we could fix it.  The other 
StatDACT-AP classes are not used because we are adopting the DCAT-AP analogue classes.

  - We can read at https://github.com/INTERSTAT/Statistics-Contextualized/tree/main/pilots/Deliverable%203.2#statdcat-ap-data-models 
  that stat:numSeries or dqv:qualityAnnotation are not created in StatDCAT-AP Smart Data Model. Why ? what is the reason
  for not declaring a complete Stat DCAt-AP Smart Data Model ?

This question has been previously answered.

  - Same strange thing with dataModel.DCAT-AP at https://raw.githubusercontent.com/smart-data-models/dataModel.DCAT-AP/master/context.jsonld, 
  which uses its own namespace, and fails to declare the types, e.g. `CatalogueDCAT-AP` used by the converter to convert
  Catalogs

Can you elaborate a little more the question. It is not clear for us.

- It seems there is an NGSI-V2 with key-values syntax for which it is not necessary to decompose the properties : 
https://github.com/smart-data-models/dataModel.STAT-DCAT-AP/blob/master/Dataset/doc/spec.md#datasetstat-dcat-ap-ngsi-v2-key-values-example is this interesting ?

Smart Data Models program is agnostic to the data model representation, and its data models look compatible with 
several formats, including NGSIv2, NGSI-LD, but also SQL, DTDL, etc. Then, these examples in the spec are useful for 
NGSIv2 users.

- The prefix stat in StatDCAT-AP is not yet assigned : http://data.europa.eu/(xyz)/statdcat-ap/ 

Correct, at the beginning of the implementation. We cannot find the URI in the specification. Nevertheless, during the 
modification of the data models to answer the first question, we discover that joinup has published the URI for the 
stat prefix (http://data.europa.eu/s1n). See https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/statdcat-application-profile-data-portals-europe/discussion/namespace-uri-still-be-finalised 
comment about it.

- Is there any constraint on the URIs to generate ? the current generators construct URIs like 
`urn:ngsi-ld:Measure:m1000` (using the local part of existing URI and crafting a new URI with urn:ngsi-ld prefix)

Only the limitation by the ETSI NGSI-LD standard (https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.06.01_60/gs_cim009v010601p.pdf, 
Annex A3). NGSI-LD defines a specific URN namespace. As it is based on URNs, the usage of this identification approach 
is not recommended when dereferenceable URIs are needed (fully-fledged linked data scenarios).

The referred namespace is defined as follows (to be registered with IANA):
• Namespace identifier: NID = "ngsi-ld"
• Namespace specific string: NSS = EntityTypeName ":" EntityIdentificationString

EntityTypeName shall be an Entity Type Name which can be expanded to a URI as per the @context.
EntityIdentificationString shall be a string that allows uniquely identifying the subject Entity in combination with 
the other items being part of the NSS.

EXAMPLE: urn:ngsi-ld:Person:28976543.

It is recommended that applications use this URN namespace when applicable. 

- Should we create any dcat:Distribution ?

At the moment, taking into account the current real cases, we did not need to use dcat:Distribution. If in the incoming 
months, we see a special scenario in which it is needed the definition of this class we work on its definition.

- Does generating the Catalogue automatically has any interest ?

SDMX DataStructureDefinition is mapped to the Dataset in DCAT-AP and the SDMX Dataset is mapped to the Catalogue DCAT-AP.

- What is the scope exactly of what we need to transform ? the current converter converts properties, concepts, concept
schemes, etc. but it looks like simple copy of the data. How should we deal with this ?

The scope of the IoTAgent-Turtle is to parse terse RDF TTL file format into the JSON-LD file format in order to apply 
ETSI NGSI-LD API and send the metadata and data to the FIWARE Context Brokers. It will demonstrate the integration of 
statistical scenarios into the FIWARE Architecture, facilitating the integration with third-parties services that can 
consume NGSI-LD API data.
