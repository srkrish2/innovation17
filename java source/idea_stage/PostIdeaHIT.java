package idea_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostIdeaHIT {
	
	public static void post(String problem, String sourceLink, String explanation, int assignmentsNum) {
		RequesterService service = new RequesterService(new PropertiesClientConfig());
		try {
			HITProperties props = new HITProperties("./idea_hit.properties");
			
			sourceLink = sourceLink.replace("&", "&amp;");

			HIT hit = service.createHIT(
			        null, // HITTypeId
			        props.getTitle(),
			        props.getDescription(),
			        null, // keywords 
			        makeQuestion(problem, sourceLink, explanation),
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
	
	private static String makeQuestion(String problem, String sourceLink, String explanation)
	 throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./generate_idea.xml" );
        VelocityContext context = new VelocityContext();
        context.put("problem", problem);
        context.put("sourceLink", sourceLink);
        context.put("explanation", explanation);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}
	
	public static void main(String[] args) {
		String problem = args[0];
		String sourceLink = args[1];
		String explanation = args[2];
		int assignmentsNum = Integer.parseInt(args[3]);
//		String problem = "How to strip noises from the road but keep the sound of other cars";
//		String sourceLink = "http://google.com/";
//		String imageLink = "https://www.gravatar.com/avatar/89927e2f4bde24991649b353a37678b9?s=32&d=identicon&r=PG";
//		String explanation = "Why this inspiration is good";
//		int assignmentsNum = 1;
		PostIdeaHIT.post(problem, sourceLink, explanation, assignmentsNum);
	}
}
