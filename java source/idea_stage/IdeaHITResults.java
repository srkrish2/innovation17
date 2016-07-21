package idea_stage;

import java.util.Calendar;
import java.util.List;

import com.amazonaws.mturk.dataschema.QuestionFormAnswers;
import com.amazonaws.mturk.dataschema.QuestionFormAnswersType;
import com.amazonaws.mturk.requester.Assignment;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class IdeaHITResults {
	
	public static void getResults(String hitId) {
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			
//			# output format:
//		    # "SUCCESS"
//			#  assignments_count
//			#  assignmentId
//			#  worker_id
//			#  epoch_time_ms
//			# "--[ANSWER START]--"
//			#  answer
//			 # "--[ANSWER END]--"
			
			// get submitted assignments - basically answers to the HIT
			Assignment[] assignments = service.getAllSubmittedAssignmentsForHIT(hitId);
			System.out.println("SUCCESS");
			System.out.println(assignments.length);
			
			for (Assignment assignment : assignments) {
	    		//By default, answers are specified in XML
		        String answerXML = assignment.getAnswer();
		        //Calling a convenience method that will parse the answer XML and extract out the question/answer pairs.
		        QuestionFormAnswers qfa = RequesterService.parseAnswers(answerXML);
		        
		        @SuppressWarnings("unchecked") // amazon sample code does casting here, suppressing the warning
				List<QuestionFormAnswersType.AnswerType> answers =
		        	(List<QuestionFormAnswersType.AnswerType>) qfa.getAnswer();
		        String assignmentId = assignment.getAssignmentId();
		        System.out.println(assignmentId);
		        System.out.println(assignment.getWorkerId());
		        Calendar submit_time = assignment.getSubmitTime();
		        long epoch_time_ms = submit_time.getTimeInMillis();
		        System.out.println(epoch_time_ms);
		        for (int i = 1; i < 3; i++) { // skipping the first answer
		        	QuestionFormAnswersType.AnswerType answer = answers.get(i);
			        String answerValue = RequesterService.getAnswerValue(assignmentId, answer);
			        System.out.println("--[ANSWER START]--");
			        System.out.println(answerValue);
			        System.out.println("--[ANSWER END]--");
		        }
		    }
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}

	public static void main(String[] args) {
//	    String hitId = "3YZ7A3YHR5T7HWZBQGWZ0DYMLXH5SX";
		String hitId = args[0];
		IdeaHITResults.getResults(hitId);
	}
}
