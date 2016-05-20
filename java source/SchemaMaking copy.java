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
	public void createTurkHIT() {
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
					makeQuestion(question), props.getMaxAssignments());

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
		q += "  <h1 align=\"center\">Generate a schema</h1>";
		q += "  <h2>Instructions</h2>";
		q += "  Your task is to select <strong>one</strong> image";
		q += "  <br/>It is possible that none of the images can satisfy all the evaluation criteria.";
		q += "  <br/>";
		q += "  <h3>Evaluation Criteria</h3>";
		q += "  <ul>";
		q += "      <li>The image should be a representation of the provided topic. </li>";
		q += " 	    <li>The image should be in focus.  (i.e. not blurry)</li>";
		q += "  </ul>";
		q += "<h2>Task</h2>";
		q += "]]></FormattedContent>";
		q += "</Overview>";
		q += "  <Question>";
		q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		q += "    <IsRequired>true</IsRequired>";
		q += "    <QuestionContent>";
		q += "      <Text>" + question + "</Text>";
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
		String question = "my problem2";// args[0];

		// Create an instance of this class.
		SchemaMaking app = new SchemaMaking(question);

		// Create the new HIT.
		app.createTurkHIT();
	}
}