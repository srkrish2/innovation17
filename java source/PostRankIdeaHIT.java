package idea_stage;

import java.io.StringWriter;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostRankIdeaHIT {
	private static final String PROPERTIES_FILE = "./rank_idea_hit.properties";
	
	private static void createHit(String problem, String idea, int assignmentsNum) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			HITProperties props = new HITProperties(PROPERTIES_FILE);
			HIT hit = service.createHIT(props.getTitle(), 
										props.getDescription(), 
										props.getRewardAmount(),
										makeQuestion(problem, idea),
										assignmentsNum);
			System.out.println("SUCCESS");
			System.out.println(hit.getHITId());
			System.out.println(service.getWebsiteURL() + "/mturk/preview?groupId=" + hit.getHITTypeId());
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}
	
	private static String makeQuestion(String problem, String idea) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate("./rank_idea.xml" );
        VelocityContext context = new VelocityContext();
        context.put("problem", problem);
        context.put("idea", idea);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}
	
	public static void main(String[] args) {
		String problem = args[0];
		String idea = args[1];
		int assignmentsNum = Integer.parseInt(args[2]);
//		String idea = "java problem";
//		String problem = "this is a test problem";
//		int assignmentsNum = 1;
		createHit(problem, idea, assignmentsNum);
	}
}
