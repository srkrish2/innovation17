package inspiration_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostRankInspirationHIT {
	private static final String PROPERTIES_FILE = "./rank_inspiration_hit.properties";
	
	public static void createHit(String schema, String inspirationLink, int assignmentsNum) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			HITProperties props = new HITProperties(PROPERTIES_FILE);
			
			inspirationLink = inspirationLink.replace("&", "&amp;");
			
			HIT hit = service.createHIT(
			        null, // HITTypeId
			        props.getTitle(),
			        props.getDescription(),
			        null, // keywords 
			        makeQuestion(schema, inspirationLink),
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
	
	private static String makeQuestion(String schema, String inspirationLink) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./rank_inspiration.xml" );
        VelocityContext context = new VelocityContext();
        context.put("schema", schema);
        context.put("inspirationLink", inspirationLink);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}
	
	public static void main(String[] args) {
		String schema = args[0];
		String inspirationLink = args[1];
		int assignmentsNum = Integer.parseInt(args[2]);
//		String schema = "need an innovative way to think";
//		String inspirationLink = "http://ak1.ostkcdn.com/images/products/8624540/P15890133.jpg";
//		int assignmentsNum = 1;
		createHit(schema, inspirationLink, assignmentsNum);
	}
}
