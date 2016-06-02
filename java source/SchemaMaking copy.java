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
		q += 
		'''<section class="container" id="Survey" style="margin-bottom:15px; padding: 10px 10px; font-family: Verdana, Geneva, sans-serif; color:#333333; font-size:0.9em;">
<div class="row col-xs-12 col-md-12"><!-- Instructions -->
<div class="panel panel-primary">
<div class="panel-heading"><strong>Instructions</strong></div>

<div class="panel-body">
<p><b>Problems share patterns which describe the structure and&nbsp;essence of problems abstractly. In this task, we would like you to generate a pattern for a problem. We will first demonstrate the process of generating a pattern through an example. <span style="color:#FF0000;">(read the instruction carefully, otherwise you risk being rejected) </span></b></p>
</div>
</div>
<b><!-- End Instructions --><!-- Survey Body --> </b>

<section>
<fieldset>
<div class="input-group">
<p><span style="font-family:verdana,geneva,sans-serif;"><b>An example problem: </b>In cold weather, you often find single dropped gloves lying on the street lonely. Almost everyone, not only kids, has lost one of their gloves, leaving the other useless. It is frustrating and a waste of money. How can we solve the problem of losing gloves? An abstract description for this problem is the following: Some objects need to work together in a pair. The problem is one of the pair is often lost leaving their partner useless. How can we prevent losing one of the pair?</span></p>

<p><span style="font-family:verdana,geneva,sans-serif;"><b>A similar problem: </b> Women like wearing earrings. But they get lost very easily. There&rsquo;s nothing more frustrating than looking in the mirror and realizing you&rsquo;ve lost an earring or going to grab a pair from your dresser and finding only one. How can we solve the problem of losing earrings?</span></p>

<p><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11.7px; line-height: 20.8px;"><b>By comparing the gloves-dropping problem with the earrings dropping problem, we can generate a pattern for the gloves-dropping problem like this: </b><br />
Some objects need to work together in a pair. The problem is one of the pair is often lost leaving their partner useless. How can we prevent losing one of the pair? </span></p>

<p>&nbsp;</p>

<h3><span style="font-family:arial,helvetica,sans-serif;"><span style="color:#000000;">The pattern describes the structure and essence of the problem without mentioning the specific domain information such as gloves. In this task, we would like you to generate a pattern for the following problem:</span></span></h3>

<p><span style="color:#008000;"><em><span style="font-family: Verdana, Geneva, sans-serif; font-size: 11.7px; line-height: 20.8px;">Engineers would like to put microphones around cars so that it can hear audio events, e.g. approaching ambulances. The size of the microphone is a couple of millimeters. How should the microphones be encased/housed so that they capture external audio events while encounter minimal wind noise.</span></em></span></p>

<p><strong>We know this task can be challenging. Please follow the steps that can help you generate a good pattern.</strong></p>

<p>Step 1: Please describe the engineer&#39;s&nbsp;problem in your own words: how do you describe it to a friend? Copy and paste is not allowed. <b><input id="description" name="description" size="160" type="text" /></b></p>

<p>Step 2: Can you think of a similar problem in a different domain? <b><input id="problem" name="problem" size="160" type="text" />'''+question+'''</b></p>

<p>Step 3: Now please generate a pattern for the engineer&#39;s problem. Tip 1: You can map the objects between the engineer&#39;s&nbsp;problem and the one you came up with to generate the shared structure.<span style="color:#000000;">Tip 2: The pattern should describe&nbsp;the characteristics of the objects in the problem and the relation structure between objects. If you have difficulty of describing objects and structures, you can search them in </span><a href="http://wordnetweb.princeton.edu/perl/webwn?s=&amp;sub=Search+WordNet&amp;o2=&amp;o0=1&amp;o8=1&amp;o1=1&amp;o7=&amp;o5=&amp;o9=&amp;o6=&amp;o3=&amp;o4=&amp;h=11010000000000" target="blank"><span style="color:#000000;">WordNet</span></a><span style="color:#000000;">&nbsp;for inspirations. </span><b><input id="pattern" name="pattern" size="160" type="text" /></b></p>
</div>
</fieldset>
</section>
<b> <b> </b></b></div>
</section>'''
		// q += "<Overview>";
		// q += "<FormattedContent><![CDATA[";
		// q += "  <h1 align=\"center\">Generate a schema</h1>";
		// q += "  <h2>Instructions</h2>";
		// q += "  Your task is to select <strong>one</strong> image";
		// q += "  <br/>It is possible that none of the images can satisfy all the evaluation criteria.";
		// q += "  <br/>";
		// q += "  <h3>Evaluation Criteria</h3>";
		// q += "  <ul>";
		// q += "      <li>The image should be a representation of the provided topic. </li>";
		// q += " 	    <li>The image should be in focus.  (i.e. not blurry)</li>";
		// q += "  </ul>";
		// q += "<h2>Task</h2>";
		// q += "]]></FormattedContent>";
		// q += "</Overview>";
		// q += "  <Question>";
		// q += "    <QuestionIdentifier>1</QuestionIdentifier>";
		// q += "    <IsRequired>true</IsRequired>";
		// q += "    <QuestionContent>";
		// q += "      <Text>" + question + "</Text>";
		// q += "    </QuestionContent>";
		// q += "    <AnswerSpecification>";
		// q += "      <FreeTextAnswer/>";
		// q += "    </AnswerSpecification>";
		// q += "  </Question>";
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