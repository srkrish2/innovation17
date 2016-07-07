package suggestion_stage;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostSuggestionHit {

	public static void post(String problem, String link, String explanation, int assignmentsNum) {
		RequesterService service = new RequesterService(new PropertiesClientConfig());
		try {
			HITProperties props = new HITProperties("./suggestion_hit.properties");

			HIT hit = service.createHIT(props.getTitle(), props.getDescription(), props.getRewardAmount(),
					makeQuestion(problem, link, explanation), assignmentsNum);

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
	
	private static String makeQuestion(String problem, String idea, String feedback) {
		String q = "";
		q += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		q += "<QuestionForm xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd\">";
		q += "<Overview>";
		q += "<FormattedContent><![CDATA[";
		q += "  <h1>Instructions</h1>";
		q += "  <p><strong>There is a problem, solution, and feedback. Improve solution to satisfy feedback.</strong></p>";
		q += "<p><strong>The problem:</strong></p>";
		q += "<p><i><font color=\"red\">" + problem + "</font></i></p>";
		q += "<p><strong>The idea:</strong></p>";
		q += "<p><i><font color=\"green\">" + idea + "</font></i></p>";
		q += "<p><strong>The feedback:</strong></p>";
		q += "<p><i><font color=\"blue\">" + feedback + "</font></i></p>";
		q += "]]></FormattedContent>";
		q += "</Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Enter improved solution. </Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "</QuestionForm>";
		return q;
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
		PostSuggestionHit.post(problem, idea, feedback, assignmentsNum);
	}
}
