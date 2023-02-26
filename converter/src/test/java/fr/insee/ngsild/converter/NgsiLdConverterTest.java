package fr.insee.ngsild.converter;

import java.io.File;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.junit.runner.RunWith;
import org.junit.runners.AllTests;

import junit.framework.TestSuite;

/**
 * Don't rename this class , it has to end with *Test to be picked up my Maven surfefire plugin
 *
 */
@RunWith(AllTests.class)
public class NgsiLdConverterTest {
	
    public static TestSuite suite() {
        TestSuite ts = new TestSuite();

        File testDir = new File("src/test/resources/test-suites/datacube-2-statdcatap");
        File outputDir = new File("target/datacube-2-statdcatap");
        
        // create output dir if needed
        if(!outputDir.exists()) {
        	outputDir.mkdirs();
        }
        
        List<File> sortedList = Arrays.asList(testDir.listFiles());
        Collections.sort(sortedList);
        for (File aDir : sortedList) {
        	if(aDir.isDirectory()) {
        		ts.addTest(new NgsiLdConverterTestExecution(aDir, outputDir));
        	}
		}
        

        return ts;
    }

}
