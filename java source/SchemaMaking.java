package schema_stage;

import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;
import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;

/**
 * The MovieSurvey sample application creates a simple HIT using the Amazon
 * Mechanical Turk SDK for Java. The file mturk.properties must be found in the
 * current file path.
 */
public class SchemaMaking {

	private RequesterService service;

	/*
	 * Define the location of the file containing the QAP and the properties of
	 * the HIT
	 */
	private String rootDir = ".";
	private String propertiesFile = rootDir + "/generate_schema_hit.properties";

	// Define the properties of the HIT to be created.
	private String question;

	/**
	 * Constructor
	 */
	public SchemaMaking(String question) {
		this.question = question;
		service = new RequesterService(new PropertiesClientConfig());
	}

	/**
	 * Create a HIT that will ask to generate a schema.
	 * 
	 */
	public void createTurkHIT(int assignmentsNum) {
		try {
			/*
			 * Loading the HIT properties file. HITProperties is a helper class
			 * that contains the properties of the HIT defined in the external
			 * file. This allows us to define the HIT attributes externally as a
			 * file and be able to modify it without recompiling the code.
			 */
			HITProperties props = new HITProperties(propertiesFile);

			// Create a HIT using the properties and question files
			HIT hit = service.createHIT(props.getTitle(), props.getDescription(), props.getRewardAmount(),
					makeQuestion(question), assignmentsNum);

			/*
			 * We got so far with no error thrown => task successfully submitted
			 * => let the caller know the HITID, assignment duration, and the
			 * URL to view the HIT.
			 * 
			 * This module gets JAR-ed and is started by the python server, so
			 * the communication between the two is implemented by piping this
			 * module's STDOUT straight to python caller. So the printing format
			 * between the two must be agreed upon. 
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

	private String makeQuestion(String question) {
		String q = "";
		q += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		q += "<QuestionForm xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd\">";
		q += "<Overview>";
		q += "<FormattedContent><![CDATA[";
		q += "  <h1>Instructions</h1>";
		q += "<p><b>Problems share patterns which describe the structure and&nbsp;essence of problems abstractly."
				+ " In this task, we would like you to generate a pattern for a problem. We will first demonstrate"
				+ " the process of generating a pattern through an example.<font color=\"red\"> Read the instruction carefully, "
				+ "otherwise you risk being rejected</font></b></p>";
		q += "<p><b>An example problem:</b> In cold weather, you often find single dropped gloves lying on the street lonely. "
				+ "Almost everyone, not only kids, has lost one of their gloves, leaving the other useless. It is frustrating "
				+ "and a waste of money. How can we solve the problem of losing gloves? An abstract description for this problem "
				+ "is the following: Some objects need to work together in a pair. The problem is one of the pair is often lost "
				+ "leaving their partner useless. How can we prevent losing one of the pair?</p>";
		q += "<p><b>A similar problem:</b> Women like wearing earrings. But they get lost very easily. There’s nothing more frustrating than"
				+ " looking in the mirror and realizing you’ve lost an earring or going to grab a pair from your dresser and finding "
				+ "only one. How can we solve the problem of losing earrings?</p>";
		q += "<b> By comparing the gloves-dropping problem with the earrings dropping problem, we can generate a pattern for the gloves-dropping "
				+ "problem like this:</b>" 
				+ "Some objects need to work together in a pair. The problem is one of the pair is often lost leaving their partner useless."
				+ " How can we prevent losing one of the pair?";
		q += "<h3>The pattern describes the structure and essence of the problem without mentioning the specific domain information such as gloves."
				+ " In this task, we would like you to generate a pattern for the following problem:</h3>";
		q += "<p><i><font color=\"green\">" + question + "</font></i></p>";
		q += "<b> We know this task can be challenging. Please follow the steps that can help you generate a good pattern.</b>";
		q += "]]></FormattedContent>";
		q += "</Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Step 1: Please describe the engineer's problem in your own words: how do you describe it to a friend? Copy and paste is not allowed. </Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>2</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Step 2: Can you think of a similar problem in a different domain? </Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>3</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Step 3: Now please generate a pattern for the engineer's problem. Tip 1: You can map the objects between the "
				+ "engineer's problem and the one you came up with to generate the shared structure.Tip 2: The pattern should describe"
				+ " the characteristics of the objects in the problem and the relation structure between objects. If you have difficulty"
				+ " of describing objects and structures, you can search them in WordNet for inspirations. </Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "</QuestionForm>";
		return q;
	}
	
	/**
	 * Main method
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		String question = args[0];
		int assignmentsNum = Integer.parseInt(args[1]);
		// String question = "i have a problem with peeling mango";
		//int assignmentsNum = 10;

		// Create an instance of this class.
		SchemaMaking app = new SchemaMaking(question);

		// Create the new HIT.
		app.createTurkHIT(assignmentsNum);
	}
}