package suggestion_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostRankSuggestionHIT {
	private static final String PROPERTIES_FILE = "./rank_suggestion_hit.properties";
	
	private static void createHit(String problem, String idea, String feedback, String[] suggestions, int assignmentsNum) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			HITProperties props = new HITProperties(PROPERTIES_FILE);
			HIT hit = service.createHIT(
			        null, // HITTypeId
			        props.getTitle(),
			        props.getDescription(),
			        null, // keywords 
			        makeQuestion(problem, idea, feedback, suggestions),
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
	
	private static String makeQuestion(String problem, String idea, String feedback, String[] suggestions) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./rank_suggestion.xml" );
        VelocityContext context = new VelocityContext();
        context.put("problem", problem);
        context.put("idea", idea);
        context.put("feedback", feedback);
        context.put("suggestions", suggestions);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}
	
	public static void main(String[] args) {
		String problem = args[0];
		String idea = args[1];
		String feedback = args[2];
		int howMany = Integer.parseInt(args[3]);
		String[] suggestions = new String[howMany];
		for (int i = 4; i < args.length-1; i++) {
			suggestions[i-4] = args[i];
		}
		int assignmentsNum = Integer.parseInt(args[args.length-1]);
//		String idea = "java idea";
//		String problem = "java problem";
//		String feedback = "java feedback";
//		String suggestion1 = "sugg1";
//		String suggestion2 = "sugg2";
//		String suggestion3 = "sugg3";
//		int assignmentsNum = 1;
//		String[] suggestions = {suggestion1, suggestion2, suggestion3};
		createHit(problem, idea, feedback, suggestions, assignmentsNum);
	}
}
