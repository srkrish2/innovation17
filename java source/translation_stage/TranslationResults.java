package translation_stage;

import java.util.List;
import java.util.concurrent.TimeUnit;

import com.amazonaws.mturk.dataschema.QuestionFormAnswers;
import com.amazonaws.mturk.dataschema.QuestionFormAnswersType;
import com.amazonaws.mturk.requester.Assignment;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class TranslationResults {
	
	static int MIN_DURATION = 1;
	
	static void getResults(String hitId) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			Assignment[] assignments = service.getAllSubmittedAssignmentsForHIT(hitId);
			
			System.out.println("SUCCESS");
			System.out.println(assignments.length);
			for (Assignment assignment : assignments) {
				String assignmentId = assignment.getAssignmentId();
				
				long acceptTimeMs = assignment.getAcceptTime().getTimeInMillis();
				long submitTimeMs = assignment.getSubmitTime().getTimeInMillis();
		        
		        long minDurationMs = TimeUnit.MILLISECONDS.convert(MIN_DURATION, TimeUnit.MINUTES);
				long duration = submitTimeMs - acceptTimeMs;
				if (duration < minDurationMs) {
					System.out.println("RESTART");
					service.rejectAssignment(assignmentId, "You spent less than a minute working on the assignment.");
					return;
				}
				
		        String answerXML = assignment.getAnswer();
		        //Calling a convenience method that will parse the answer XML and extract out the question/answer pairs.
		        QuestionFormAnswers qfa = RequesterService.parseAnswers(answerXML);
		        
		        @SuppressWarnings("unchecked") // amazon sample code does casting here, suppressing the warning
				List<QuestionFormAnswersType.AnswerType> answers =
		        	(List<QuestionFormAnswersType.AnswerType>) qfa.getAnswer();
		        
		        System.out.println(answers.size());
		        for (QuestionFormAnswersType.AnswerType answer : answers) {
		        	System.out.println(RequesterService.getAnswerValue(assignmentId, answer));	
		        }
		        
		        System.out.println(assignmentId);
		        System.out.println(assignment.getWorkerId());
		        System.out.println(acceptTimeMs);
		        System.out.println(submitTimeMs);
			}
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}
	
	public static void main(String[] args) {
		String hitId = args[0];
		getResults(hitId);
	}
	
}
