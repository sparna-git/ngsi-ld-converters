package fr.insee.ngsild.converter;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Iterator;
import java.util.Map.Entry;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Statement;
import org.apache.jena.rdf.model.StmtIterator;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RDFLanguages;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;

import junit.framework.AssertionFailedError;
import junit.framework.Test;
import junit.framework.TestResult;

/**
 * Don't rename this class otherwise it could be picked up by Maven plugin to execute test.
 * @author thomas
 *
 */
public class NgsiLdConverterTestExecution implements Test {

	protected File testFolder;
	protected File outputFolder;
	protected NgsiLdShaclRulesConverter converter;
	private Model outputModel;
	// Jackson mapper
	protected ObjectMapper mapper = new ObjectMapper();
	
	public NgsiLdConverterTestExecution(File testFolder, File outputFolder) {
		super();
		this.testFolder = testFolder;
		this.outputFolder = outputFolder;
		
		this.converter = new NgsiLdShaclRulesConverter();
	}

	@Override
	public int countTestCases() {
		return 1;
	}

	@Override
	public void run(TestResult result) {
		result.startTest(this);
		File input = new File(this.testFolder, "input.ttl");
		if(!input.exists()) {
			input = new File(this.testFolder, "input.rdf");
		}
		if(!input.exists()) {
			input = new File(this.testFolder, "input.jsonld");
		}
		
		System.out.println("Testing "+input.getAbsolutePath());
		
		final File expected = new File(this.testFolder, "expected.ttl");
		final File expectedJson = new File(this.testFolder, "expected.jsonld");
		
		
		
		
		// convert
		outputModel = this.converter.convertRdfFile(input);
		
		System.out.println(this.converter.convertJsonFile(input));
		
		// debug in output folder
		try(FileOutputStream out = new FileOutputStream(new File(this.outputFolder, this.testFolder.getName()+".ttl"))) {
			outputModel.write(out, Lang.TTL.getName());
		} catch (Exception e1) {
			e1.printStackTrace();
		}
		
		
		if(expected.exists()) {
			Model expectedModel = ModelFactory.createDefaultModel();
			try(FileInputStream in = new FileInputStream(expected)) {
				RDFDataMgr.read(expectedModel, in, RDFLanguages.filenameToLang(expected.getName(), Lang.RDFXML));
			} catch (Exception e) {
				result.addError(this, e);
				throw new IllegalArgumentException("Problem with external.ttl in unit test "+this.testFolder.getName(), e);
			}			
			
			// test if isomorphic
			if(!expectedModel.isIsomorphicWith(outputModel)) {
				result.addFailure(this, new AssertionFailedError("Test failed on "+this.testFolder+":"
						+ "\nStatements in output not in expected:\n"+prettyPrint(outputModel.difference(expectedModel))
						+ "\nStatements in expected missing in output:\n"+prettyPrint(expectedModel.difference(outputModel))
				));
			}
		} 
		
		String outputJsonLdString = converter.convertJsonFile(input);
		
		if(expectedJson.exists()) {
			try(InputStream in = new FileInputStream(expectedJson)) {
				JsonNode outputJsonLd = mapper.readTree(outputJsonLdString);
				JsonNode expectedJsonLd = mapper.readTree(new String(in.readAllBytes(), StandardCharsets.UTF_8));
				
				// now remove the @context key to compare without context
				((ObjectNode)outputJsonLd).remove("@context");
				((ObjectNode)expectedJsonLd).remove("@context");
				
				// debug in output folder
				try(FileOutputStream out = new FileOutputStream(new File(this.outputFolder, this.testFolder.getName()+".jsonld"))) {
					String prettyString = outputJsonLd.toPrettyString();
					out.write(prettyString.getBytes());
				} catch (Exception e1) {
					e1.printStackTrace();
				}
				
				// compare
				if(!outputJsonLd.equals(expectedJsonLd)) {
					result.addFailure(this, new AssertionFailedError("Test failed on "+this.testFolder));
					System.out.println(prettyPrintDiff((ObjectNode)outputJsonLd, (ObjectNode)expectedJsonLd));
					System.out.println(prettyPrintDiff((ObjectNode)expectedJsonLd, (ObjectNode)outputJsonLd));
				}
				
			} catch (Exception e) {
				result.addError(this, e);
				throw new IllegalArgumentException("Problem in JSON comparison in unit test "+this.testFolder.getName(), e);
			}
		}
		
		result.endTest(this);
	}

	@Override
	public String toString() {
		return testFolder.getName();
	}
	
	private static String prettyPrint(Model model) {
		StringBuffer sb = new StringBuffer();
		
		for(StmtIterator iterator = model.listStatements(); iterator.hasNext();) {
			Statement statement = iterator.next();
			sb.append(statement.toString()+"\n");
		}
		
		return sb.toString();
	}
	
	private static String prettyPrintDiff(JsonNode node1, JsonNode node2) {
		StringBuffer sb = new StringBuffer();
		if(node1.getNodeType() == JsonNodeType.OBJECT) {
			for (Iterator<Entry<String, JsonNode>> iterator = node1.fields(); iterator.hasNext();) {
				Entry<String, JsonNode> entry = (Entry<String, JsonNode>) iterator.next();
				if(!node2.has(entry.getKey())) {
					sb.append("Missing "+entry.getKey()+"\n");
				}
				sb.append(prettyPrintDiff(entry.getValue(), node2.get(entry.getKey())));
			}
		}
		
		if(node1.getNodeType() == JsonNodeType.ARRAY) {
			if(!node1.equals(node2)) {
				for(int i =0;i<node1.size();i++) {
					JsonNode entry = node1.get(i);
					if(node2.get(i) == null) {
						sb.append("Missing value "+i+"\n");
					} else {
						sb.append(prettyPrintDiff(entry, node2.get(i)));
					}
				}
			}
		}
		
		if(node1.getNodeType() == JsonNodeType.STRING) {
			if(!node1.equals(node2)) {
				sb.append("Not identical "+node1+" and "+node2+" ");
			}
		}
		
		return sb.toString();
	}

}
