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
			HIT hit = service.createHIT(
			        null, // HITTypeId
			        props.getTitle(),
			        props.getDescription(),
			        null, // keywords 
			        makeQuestion(problem, schemas),
			        props.getRewardAmount(),
			        props.getAssignmentDuration(),
			        props.getAutoApprovalDelay(),
			        props.getLifetime(),
			        assignmentsNum,
			        null, //requesterAnnotation
			        null, // qualificationRequirements
			        new String [] { "Minimal", "HITDetail", "HITQuestion", "HITAssignmentSummary" },
			        null, // uniqueRequesterToken
			        null, // assignmentReviewPolicy
			        null  // hitReviewPolicy
			);
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
//		String[] args = {"the problem", "3", "this is a test schema", "test schema 2", "schema 3", "1"};
		String problem = args[0];
		int howManySchemas = Integer.parseInt(args[1]);
		String[] schemas = new String[howManySchemas];
		for (int i = 2; i < args.length-1; i++) {
			schemas[i-2] = args[i];
		}
		int assignmentsNum = Integer.parseInt(args[args.length-1]);
//		int assignmentsNum = 1;
		createHit(problem, schemas, assignmentsNum);
	}
}
