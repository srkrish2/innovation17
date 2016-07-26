package suggestion_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostSuggestionHIT {

	public static void post(String problem, String link, String explanation, int assignmentsNum) {
		RequesterService service = new RequesterService(new PropertiesClientConfig());
		try {
			HITProperties props = new HITProperties("./suggestion_hit.properties");

			HIT hit = service.createHIT(
			        null, // HITTypeId
			        props.getTitle(),
			        props.getDescription(),
			        null, // keywords 
			        makeQuestion(problem, link, explanation),
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
	
	private static String makeQuestion(String problem, String idea, String feedback) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./generate_suggestion.xml" );
        VelocityContext context = new VelocityContext();
        context.put("problem", problem);
        context.put("idea", idea);
        context.put("feedback", feedback);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}
	
	public static void main(String[] args) {
		String problem = args[0];
		String idea = args[1];
		String feedback = args[2];
		int assignmentsNum = Integer.parseInt(args[3]);
//		String problem = "How to strip noises from the road but keep the sound of other cars";
//		String idea = "Use the same structure as birds ears";
//		String feedback = "How to make it washer safe?";
//		int assignmentsNum = 1;
		PostSuggestionHIT.post(problem, idea, feedback, assignmentsNum);
	}
}
