import java.util.Calendar;
import java.util.List;

import com.amazonaws.mturk.dataschema.QuestionFormAnswers;
import com.amazonaws.mturk.dataschema.QuestionFormAnswersType;
import com.amazonaws.mturk.requester.Assignment;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;
/*
output format:
	# "SUCCESS"
	# "--[ANSWER START]--"
	#  worker_id
	#  epoch_time_ms
	#  answer: GOOD or BAD
	# "--[ANSWER END]--"
	# "--[END]--"
*/

public class SchemaRankingResults {
	public static void getResults(String hitId){
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			Assignment[] assignments = service.getAllSubmittedAssignmentsForHIT(hitId);
			
			System.out.println("SUCCESS");
		    
		    for (Assignment assignment : assignments) {
		        String answerXML = assignment.getAnswer();
		        
		        //Calling a convenience method that will parse the answer XML and extract out the question/answer pairs.
		        QuestionFormAnswers qfa = RequesterService.parseAnswers(answerXML);
		        
		        @SuppressWarnings("unchecked") // amazon sample code does casting here, suppressing the warning
				List<QuestionFormAnswersType.AnswerType> answers =
		        	(List<QuestionFormAnswersType.AnswerType>) qfa.getAnswer();
		        QuestionFormAnswersType.AnswerType answer = answers.get(0);
		        
	        	String assignmentId = assignment.getAssignmentId();
		        String answerValue = RequesterService.getAnswerValue(assignmentId, answer);
		        System.out.println("--[ANSWER START]--");
		        System.out.println(answerValue);
		        System.out.println(assignment.getWorkerId());
		        Calendar submit_time = assignment.getSubmitTime();
		        long epoch_time_ms = submit_time.getTimeInMillis();
		        System.out.println(epoch_time_ms);
		        System.out.println(answerValue);
		        System.out.println("--[ANSWER END]--");
	    	}
		    System.out.println("--[END]--");
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
