package fr.insee.ngsild.converter;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.nio.charset.StandardCharsets;

import org.apache.jena.query.DatasetFactory;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.riot.JsonLDWriteContext;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RDFFormat;
import org.apache.jena.riot.RDFLanguages;
import org.apache.jena.riot.RDFWriter;
import org.apache.jena.sparql.core.DatasetGraph;
import org.topbraid.shacl.rules.RuleUtil;

public class NgsiLdShaclRulesConverter implements NgsiLdConverterIfc {

	private static String DATACUBE_RULESET = "datacube-2-statdcatap.ttl";
	private static String FRAMING_CONTEXT = "framing-context.jsonld";
	
	public String convertJson(Model input) {
		Model outputModel = this.convertRdf(input);
		DatasetGraph g = DatasetFactory.wrap(outputModel).asDatasetGraph();
		JsonLDWriteContext ctx = new JsonLDWriteContext();
		// String frame = "{\"@type\" : \"http://schema.org/Person\"}";
		
		
		try(InputStream in = this.getClass().getClassLoader().getResourceAsStream(FRAMING_CONTEXT)) {
			String frame = new String(in.readAllBytes(), StandardCharsets.UTF_8);
			ctx.setFrame(frame);
		} catch (IOException e1) {
			e1.printStackTrace();
		}		
		
		
		RDFWriter w = RDFWriter.create()
            .format(RDFFormat.JSONLD_FRAME_PRETTY)
            .source(g)
            .context(ctx)
            .build();
		
		ByteArrayOutputStream baos = new ByteArrayOutputStream();
		w.output(baos);
		try {
			return baos.toString("UTF-8");
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
			return null;
		}
	}
	
	public String convertJsonFile(File f) {
		return this.convertJson(this.readFile(f));
	}
	
	public Model convertRdf(Model input) {
		// load ruleset from a resources
		Model shapesModel = ModelFactory.createDefaultModel();
		
		try(InputStream in = this.getClass().getClassLoader().getResourceAsStream(DATACUBE_RULESET)) {
			RDFDataMgr.read(shapesModel, in, RDFLanguages.filenameToLang(DATACUBE_RULESET, Lang.RDFXML));
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		Model output =RuleUtil.executeRules(input, shapesModel, null, null);
		return output;
	}

	@Override
	public Model convertRdfFile(File f) {
		return this.convertRdf(readFile(f));
	}
	
	private Model readFile(File f) {
		Model model = ModelFactory.createDefaultModel();
		try(FileInputStream in = new FileInputStream(f)) {
			RDFDataMgr.read(model, in, RDFLanguages.filenameToLang(f.getName(), Lang.RDFXML));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return model;
	}
	
}
