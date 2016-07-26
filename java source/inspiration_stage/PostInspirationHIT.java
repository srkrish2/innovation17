package inspiration_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostInspirationHIT {
	/*
	 * Define the location of the file containing the QAP and the properties of
	 * the HIT
	 */
	private static String rootDir = ".";
	private static String propertiesFile = rootDir + "/inspiration_hit.properties";

	/**
	 * Create a HIT that will ask to generate a schema.
	 * 
	 */
	public static void post(String question, int assignmentsNum) {
		RequesterService service = new RequesterService(new PropertiesClientConfig());
		try {
			/*
			 * Loading the HIT properties file. HITProperties is a helper class
			 * that contains the properties of the HIT defined in the external
			 * file. This allows us to define the HIT attributes externally as a
			 * file and be able to modify it without recompiling the code.
			 */
			HITProperties props = new HITProperties(propertiesFile);

			HIT hit = service.createHIT(
			        null, // HITTypeId
			        props.getTitle(),
			        props.getDescription(),
			        null, // keywords 
			        makeQuestion(question),
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

			/*
			 * We got so far with no error thrown => task successfully submitted
			 * => let the caller know the HITID, assignment duration, and the
			 * URL to view the HIT.
			 * 
			 * This module gets JAR-ed and is started by the python server, so
			 * the communication between the two is implemented by piping this
			 * module's STDOUT straight to python caller. So the printing format
			 * between the two must be agreed upon. 
			 * Format: 
			 *  "SUCCESS"
			 *  HIT_ID
			 *  URL
			 */
			System.out.println("SUCCESS");
			System.out.println(hit.getHITId());
			System.out.println(service.getWebsiteURL() + "/mturk/preview?groupId=" + hit.getHITTypeId());
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}

	private static String makeQuestion(String schema) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./generate_inspiration.xml" );
        VelocityContext context = new VelocityContext();
        context.put("schema", schema);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}

	/**
	 * Main method
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		String schema = args[0];
		int assignmentsNum = Integer.parseInt(args[1]);
//		 String schema = "How do you blah blah abstract";
//		 int assignmentsNum = 3;

		// Create an instance of this class.
		PostInspirationHIT.post(schema, assignmentsNum);
	}
}
