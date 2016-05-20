import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class SchemaRanking {
	
	private static final String PROPERTIES_FILE = "./rank_schema_hit.properties";
	
	private static void createHit(String schema) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			HITProperties props = new HITProperties(PROPERTIES_FILE);
			HIT hit = service.createHIT(props.getTitle(), 
										props.getDescription(), 
										props.getRewardAmount(),
										makeQuestion(schema),
										props.getMaxAssignments());
			System.out.println("SUCCESS");
			System.out.println(hit.getHITId());
			System.out.println(service.getWebsiteURL() + "/mturk/preview?groupId=" + hit.getHITTypeId());
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}
	
	private static String makeQuestion(String schema) {
		String q = "";
		q += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		q += "<QuestionForm xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd\">";
		q += "  <Overview>";
		q += "  <FormattedContent><![CDATA[";
		q += "    <h1 align=\"center\">Rank a schema</h1>";
		q += "    <h2>Instructions</h2>";
		q += "    Your task is to rank a schema";
		q += "    <br/>";
		q += "    <h3>A good schema should meet the following criteria</h3>";
		q += "    <ul>";
		q += "      <li>It specifies a purpose (e.g., detaches things) </li>";
		q += " 	    <li>It specifies a mechanism (e.g., uses comb-like features) </li>";
		q += "      <li>It shouldn't be too vague (e.g. \"make things easy\" is too vague) </li>";
		q += " 	    <li>It shouldn't have too many details (e.g., the details of the given idea, such as the color or the dustpan, should not be included) </li>";
		q += "    </ul>";
		q += "    <h2>Task</h2>";
		q += "  ]]></FormattedContent>";
		q += "  </Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>" + schema + "</Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "          <SelectionAnswer>";
		q += "            <MinSelectionCount>1</MinSelectionCount>";
		q += "            <MaxSelectionCount>1</MaxSelectionCount>";
		q += "            <StyleSuggestion>radiobutton</StyleSuggestion>";
		q += "            <Selections>";
		q += "              <Selection>";
		q += "                <SelectionIdentifier>GOOD</SelectionIdentifier>";
		q += "                <Text>Good</Text>";
		q += "              </Selection>";
		q += "              <Selection>";
		q += "                <SelectionIdentifier>BAD</SelectionIdentifier>";
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
		String schema = args[0];
		createHit(schema);
	}
}
