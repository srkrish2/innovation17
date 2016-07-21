package schema_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

/**
 * The MovieSurvey sample application creates a simple HIT using the Amazon
 * Mechanical Turk SDK for Java. The file mturk.properties must be found in the
 * current file path.
 */
public class PostSchemaHIT {

	private RequesterService service;

	/*
	 * Define the location of the file containing the QAP and the properties of
	 * the HIT
	 */
	private String rootDir = ".";
	private String propertiesFile = rootDir + "/generate_schema_hit.properties";

	// Define the properties of the HIT to be created.
	private String question;

	/**
	 * Constructor
	 */
	public PostSchemaHIT(String question) {
		this.question = question;
		service = new RequesterService(new PropertiesClientConfig());
	}

	/**
	 * Create a HIT that will ask to generate a schema.
	 * 
	 */
	public void createTurkHIT(int assignmentsNum) {
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

	private String makeQuestion(String question) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./generate_schema.xml" );
        VelocityContext context = new VelocityContext();
        context.put("question", question);
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
		String question = args[0];
		int assignmentsNum = Integer.parseInt(args[1]);
//		String question = "i have a problem with peeling mango";
//		int assignmentsNum = 1;

		// Create an instance of this class.
		PostSchemaHIT app = new PostSchemaHIT(question);

		// Create the new HIT.
		app.createTurkHIT(assignmentsNum);
	}
}