import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class PostInspirationHIT {
	/*
	 * Define the location of the file containing the QAP and the properties of
	 * the HIT
	 */
	private static String rootDir = ".";
	private static String propertiesFile = rootDir + "/inspiration_hit.properties";

	/**
	 * Create a HIT that will ask to generate a schema.
	 * 
	 */
	public static void post(String question, int assignmentsNum) {
		RequesterService service = new RequesterService(new PropertiesClientConfig());
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

	private static String makeQuestion(String schema) {
		String q = "";
		q += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		q += "<QuestionForm xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd\">";
		q += "<Overview>";
		q += "<FormattedContent><![CDATA[";
		q += "  <h1>Instructions</h1>";
		q += "  <strong>Please find inspirations for solving the following problem.</strong>";
		q += "<p><i><font color=\"green\">" + schema + "</font></i></p>";
		q += "  <strong>Please search online to find an inspiration that you think can help with solving the above problem.</strong>";
		q += "]]></FormattedContent>";
		q += "</Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Inspiration: Paste the link below. We are looking for inspirations (not solutions) to this problem."
				+ " Your answer has to be a revevant inspiration, otherwise you risk being rejected.  </Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>2</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Please summarize the inspiration in a few sentences.</Text>";
		q += "    </QuestionContent>";
		q += "    <AnswerSpecification>";
		q += "      <FreeTextAnswer/>";
		q += "    </AnswerSpecification>";
		q += "  </Question>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>3</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>Why do you think the inspiration you found might help with solving the problem? </Text>";
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
		String schema = args[0];
		int assignmentsNum = Integer.parseInt(args[1]);
		// String schema = "How do you blah blah abstract";
		// int assignmentsNum = 3;

		// Create an instance of this class.
		PostInspirationHIT.post(schema, assignmentsNum);
	}
}
