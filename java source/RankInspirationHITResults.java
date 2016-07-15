package inspiration_stage;

import java.util.Calendar;
import java.util.List;

import com.amazonaws.mturk.dataschema.QuestionFormAnswers;
import com.amazonaws.mturk.dataschema.QuestionFormAnswersType;
import com.amazonaws.mturk.requester.Assignment;
import com.amazonaws.mturk.requester.AssignmentStatus;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

/*
output format:
    #  "SUCCESS"
    #  assignments_num
    #  answers
    #  assignment_id
    #  worker_id
    #  epoch_time_ms
*/

public class RankInspirationHITResults {
	public static void getResults(String hitId){
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			
			Assignment[] assignments = service.getAllAssignmentsForHIT(hitId);
			System.out.println("SUCCESS");
			for (Assignment assignment : assignments) {
				if (assignment.getAssignmentStatus() != AssignmentStatus.Submitted) {
					System.out.println(0);
					return;
				}
			}

			System.out.println(assignments.length);
			for (Assignment assignment : assignments) {
		        String answerXML = assignment.getAnswer();
		        //Calling a convenience method that will parse the answer XML and extract out the question/answer pairs.
		        QuestionFormAnswers qfa = RequesterService.parseAnswers(answerXML);
		        
		        @SuppressWarnings("unchecked") // amazon sample code does casting here, suppressing the warning
				List<QuestionFormAnswersType.AnswerType> answers =
		        	(List<QuestionFormAnswersType.AnswerType>) qfa.getAnswer();
		        String assignmentId = assignment.getAssignmentId();
		        
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
//		String hitId = "3SBNLSTU6U5ZML0I0E8QUIJIRG0DZL";
		getResults(hitId);
	}
}
