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
- In existing converter, why is URI mapped to dct:title and why is rdfs:label mapped to dct:description ?
- Existing converter generates separate files in the output. Is there a reason for this ? could the output be in a single file ?
- The STAT-DCAT-AP json-ld context at https://smart-data-models.github.io/dataModel.STAT-DCAT-AP/context.jsonld maps keys to wrong URIs. Is it intended ? This is a blocking issue as it forces us to use these URIs (and not the typical dct ones) so that we can then regenerate a JSON-LD valid according to the spec.
  - I have the feeling that the JSON-LD context of StatDCAT-AP is incomplete; it does not contain the classes documented at https://github.com/INTERSTAT/Statistics-Contextualized/tree/main/pilots/Deliverable%203.2#dcat-ap-data-models
- It seems there is an NGSI-V2 with key-values syntax for which it is not necessary to decompose the properties : https://github.com/smart-data-models/dataModel.STAT-DCAT-AP/blob/master/Dataset/doc/spec.md#datasetstat-dcat-ap-ngsi-v2-key-values-example is this interesting ?
- The prefix stat in StatDCAT-AP is not yet assigned : http://data.europa.eu/(xyz)/statdcat-ap/
- Is there any constraint on the URIs to generate ? the current generators construct URIs like `urn:ngsi-ld:Measure:m1000` (using the local part of existing URI and crafting a new URI with urn:ngsi-ld prefix)
- Should we create any dcat:Distribution ?
