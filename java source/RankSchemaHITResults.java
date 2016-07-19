package schema_stage;

import java.util.Calendar;
import java.util.List;

import com.amazonaws.mturk.dataschema.QuestionFormAnswers;
import com.amazonaws.mturk.dataschema.QuestionFormAnswersType;
import com.amazonaws.mturk.requester.Assignment;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;
/*
output format:
    #  "SUCCESS"
    #  assignments_num
    #  answers_num
    #  {{answers_num}} ranks
    #  assignment_id
    #  worker_id
    #  epoch_time_ms
*/

public class RankSchemaHITResults {
	public static void getResults(String hitId){
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			
			HIT hit = service.getHIT(hitId);
			System.out.println("SUCCESS");
			if (hit.getNumberOfAssignmentsAvailable() > 0 || hit.getNumberOfAssignmentsPending() > 0) {
				System.out.println(0);
				return;
			}
			
			Assignment[] assignments = service.getAllSubmittedAssignmentsForHIT(hitId);
			System.out.println(assignments.length);
			for (Assignment assignment : assignments) {
		        String answerXML = assignment.getAnswer();
		        //Calling a convenience method that will parse the answer XML and extract out the question/answer pairs.
		        QuestionFormAnswers qfa = RequesterService.parseAnswers(answerXML);
		        
		        @SuppressWarnings("unchecked") // amazon sample code does casting here, suppressing the warning
				List<QuestionFormAnswersType.AnswerType> answers =
		        	(List<QuestionFormAnswersType.AnswerType>) qfa.getAnswer();
		        String assignmentId = assignment.getAssignmentId();
		        String cheatCheckAnswer = RequesterService.getAnswerValue(assignmentId, answers.remove(0));
		        if (cheatCheckAnswer.equals("NO")) {
		        	service.rejectAssignment(assignmentId, 
		        			"In the first question, we showed a good schema from the instructions example, and you said it's not good");
		        	System.out.println(0);
		        	continue;
		        }
		        
		        System.out.println(answers.size());
		        for (QuestionFormAnswersType.AnswerType answer : answers) {
		        	System.out.println(RequesterService.getAnswerValue(assignmentId, answer));
		        }
		        
		        System.out.println(assignmentId);
		        System.out.println(assignment.getWorkerId());
		        Calendar submitTime = assignment.getSubmitTime();
		        long epochTimeMs = submitTime.getTimeInMillis();
		        System.out.println(epochTimeMs);
			}
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}
	
	public static void main(String[] args) {
		String hitId = args[0];
//		String hitId = "37S0QRNUFBG8LU34AGXXV68DHGT882";
		getResults(hitId);
	}
}
