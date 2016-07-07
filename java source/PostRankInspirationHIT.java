package inspiration_stage;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostRankInspirationHIT {
	private static final String PROPERTIES_FILE = "./rank_inspiration_hit.properties";
	
	public static void createHit(String problem, String schema, String inspirationLink, 
			String inspirationAdditional, String inspirationReason, int assignmentsNum) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			HITProperties props = new HITProperties(PROPERTIES_FILE);
			
			inspirationLink = inspirationLink.replace("&", "&amp;");
			inspirationAdditional = inspirationAdditional.replace("&", "&amp;");
			
			HIT hit = service.createHIT(props.getTitle(), 
										props.getDescription(), 
										props.getRewardAmount(),
										makeQuestion(problem, schema, inspirationLink, inspirationAdditional, inspirationReason),
										assignmentsNum);
			System.out.println("SUCCESS");
			System.out.println(hit.getHITId());
			System.out.println(service.getWebsiteURL() + "/mturk/preview?groupId=" + hit.getHITTypeId());
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}
	
	private static String makeQuestion(String problem, String schema, String sourceLink, String imageLink,
			String explanation) {
		String q = "";
		q += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		q += "<QuestionForm xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd\">";
		q += "  <Overview>";
		q += "  <FormattedContent><![CDATA[";
		q += "    <h1 align=\"center\">Rank an inspiration</h1>";
		q += "<p>Problem: <i><font color=\"green\">" + problem + "</font></i></p>";
		q += "<p>Schema: <i><font color=\"blue\">" + schema + "</font></i></p>";
		q += String.format("<p><strong><a href=\"%s\" target=\"blank\">Click here to look at the inspiration</a> It will open up a new tab.</strong></p>", sourceLink);
		if (!imageLink.isEmpty()) {
			q += "<p> The worker also attached the image: </p>";
			q += String.format("<img src=\"%s\" alt=\"Worker's image\" />", imageLink);
		}
		q += "<p>" + explanation + "</p>";
		q += "    <h2>Task</h2>";
		q += "  ]]></FormattedContent>";
		q += "  </Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Rank the inspiration</Text>";
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
		String schema = args[1];
		String inspirationLink = args[2];
		String inspirationAdditional = args[3];
		String inspirationReason = args[4];
		int assignmentsNum = Integer.parseInt(args[5]);
//		String problem = "wind noise problem";
//		String schema = "keep useful noise";
//		String inspirationLink = "http://stackoverflow.com/questions/963965/how-to-write-strategy-pattern-in-python-differently-than-example-in-wikipedia";
//		String inspirationAdditional = "https://www.gravatar.com/avatar/1449ec95d8c114dbca53136cc8194b61?s=64&d=identicon&r=PG&f=1";
//		String inspirationReason = "this will help because.";
//		int assignmentsNum = 1;
		createHit(problem, schema, inspirationLink, inspirationAdditional, inspirationReason, assignmentsNum);
	}
}
