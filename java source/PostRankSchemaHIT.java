package schema_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostRankSchemaHIT {
	
	private static final String PROPERTIES_FILE = "./rank_schema_hit.properties";
	
	private static void createHit(String problem, String[] schemas, int assignmentsNum) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			HITProperties props = new HITProperties(PROPERTIES_FILE);
			HIT hit = service.createHIT(props.getTitle(), 
										props.getDescription(), 
										props.getRewardAmount(),
										makeQuestion(problem, schemas),
										assignmentsNum);
			System.out.println("SUCCESS");
			System.out.println(hit.getHITId());
			System.out.println(service.getWebsiteURL() + "/mturk/preview?groupId=" + hit.getHITTypeId());
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}
	
	private static String makeQuestion(String problem, String[] schemas) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./rank_schema.xml" );
        VelocityContext context = new VelocityContext();
        context.put("problem", problem);
        context.put("schemas", schemas);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}
	
	public static void main(String[] args) {
		String problem = args[0];
		String schema1 = args[1];
		String schema2 = args[2];
		String schema3 = args[3];
		int assignmentsNum = Integer.parseInt(args[4]);
//		String problem = "the problem";
//		String schema1 = "this is a test schema";
//		String schema2 = "test schema 2";
//		String schema3 = "schema 3";
//		int assignmentsNum = 1;
		String[] schemas = {schema1, schema2, schema3};
		createHit(problem, schemas, assignmentsNum);
	}
}
