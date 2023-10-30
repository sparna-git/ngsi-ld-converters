package fr.insee.ngsild.converter;

import java.io.File;

import org.apache.jena.rdf.model.Model;

public interface NgsiLdConverterIfc {

	public String convertJson(Model input);
	
	public String convertJsonFile(File f);
	
	public Model convertRdf(Model input);

	public Model convertRdfFile(File f);
}
