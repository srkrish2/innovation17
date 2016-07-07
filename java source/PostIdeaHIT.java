package idea_stage;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostIdeaHIT {
	
	public static void post(String problem, String sourceLink, String imageLink, String explanation, int assignmentsNum) {
		RequesterService service = new RequesterService(new PropertiesClientConfig());
		try {
			HITProperties props = new HITProperties("./idea_hit.properties");
			
			sourceLink = sourceLink.replace("&", "&amp;");
			imageLink = imageLink.replace("&", "&amp;");

			HIT hit = service.createHIT(props.getTitle(), props.getDescription(), props.getRewardAmount(),
					makeQuestion(problem, sourceLink, imageLink, explanation), assignmentsNum);

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
	
	private static String makeQuestion(String problem, String sourceLink, String imageLink, String explanation) {
		String q = "";
		q += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		q += "<QuestionForm xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd\">";
		q += "<Overview>";
		q += "<FormattedContent><![CDATA[";
		q += "  <h1>Instructions</h1>";
		q += "  <p><strong>Below is a problem we have. In a previous task, we asked workers to find inspirations for this problem."
				+ " In this task, we would like you to solve this problem by using the inspiration.</strong></p>";
		q += "<p><i><font color=\"green\">" + problem + "</font></i></p>";
		q += String.format("<p><strong><a href=\"%s\" target=\"blank\">Click here to look at the inspiration</a> It will open up a new tab.</strong></p>", sourceLink);
		if (!imageLink.isEmpty()) {
			q += "<p> The worker also attached the image: </p>";
			q += String.format("<img src=\"%s\" alt=\"Worker's image\" />", imageLink);
		}
		q += "<p><strong>The explanation from the previous worker regarding why this link can help with solving the problem:</strong></p>";
		q += "<p>" + explanation + "</p>";
		q += "]]></FormattedContent>";
		q += "</Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Summarize the content of the inspiration link. </Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>2</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Generate a solution for the problem by using the inspiration provided. "
				+ "Describe your solution as detailed as possible. It should be elaborate enough that the engineers know how"
				+ " to design the product based on your solution description.</Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>3</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Come up with a short title (2-3 words) for your solution. </Text>";
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
		String sourceLink = args[1];
		String imageLink = args[2];
		String explanation = args[3];
		int assignmentsNum = Integer.parseInt(args[4]);
//		String problem = "How to strip noises from the road but keep the sound of other cars";
//		String sourceLink = "http://google.com/";
//		String imageLink = "https://www.gravatar.com/avatar/89927e2f4bde24991649b353a37678b9?s=32&d=identicon&r=PG";
//		String explanation = "Why this inspiration is good";
//		int assignmentsNum = 1;
		PostIdeaHIT.post(problem, sourceLink, imageLink, explanation, assignmentsNum);
	}
}
