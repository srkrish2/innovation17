package idea_stage;

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
	
	private static String makeQuestion(String problem, String idea) {
		String q = "";
		q += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		q += "<QuestionForm xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd\">";
		q += "  <Overview>";
		q += "  <FormattedContent><![CDATA[";
		q += "    <h1 align=\"center\">Rank an idea</h1>";
		q += "    <h2>Instructions</h2>";
		q += "    Your task is to rank an idea";
		q += "    <br/>";
		q += "    <h2>Instructions</h2>";
		q += "    Your task is to rank an idea";
		q += "    <br/>";
		q += "<p>Problem: <i><font color=\"green\">" + problem + "</font></i></p>";
		q += "<p>Idea: <i><font color=\"blue\">" + idea + "</font></i></p>";
		q += "    <h2>Task</h2>";
		q += "  ]]></FormattedContent>";
		q += "  </Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text> Rank the idea </Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "          <SelectionAnswer>";
		q += "            <MinSelectionCount>1</MinSelectionCount>";
		q += "            <MaxSelectionCount>1</MaxSelectionCount>";
		q += "            <StyleSuggestion>radiobutton</StyleSuggestion>";
		q += "            <Selections>";
		q += "              <Selection>";
		q += "                <SelectionIdentifier>1</SelectionIdentifier>";
		q += "                <Text>Good</Text>";
		q += "              </Selection>";
		q += "              <Selection>";
		q += "                <SelectionIdentifier>0</SelectionIdentifier>";
		q += "                <Text>Bad</Text>";
		q += "              </Selection>";
		q += "            </Selections>";
		q += "          </SelectionAnswer>";
		q += "        </AnswerSpecification>";
		q += "  </Question>";
		q += "</QuestionForm>";
		return q;
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
