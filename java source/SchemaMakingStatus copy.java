import com.amazonaws.mturk.requester.Assignment;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public class SchemaMakingStatus {
	public static void main(String[] args) {
		String hitId = args[0];
		SchemaMakingStatus.getSubmittedAssignmentsCount(hitId);
	}

	private static void getSubmittedAssignmentsCount(String hitId) {
//		output format:
//	    # submitted_assignments_count if success
//	    # else:
//	    # FAIL
//	    # localizedMessage
		try {
			RequesterService service = new RequesterService(new PropertiesClientConfig());
			// get submitted assignments - basically answers to the HIT
			Assignment[] assignments = service.getAllSubmittedAssignmentsForHIT(hitId);
			System.out.println(assignments.length);
		} catch (Exception e) {
			System.out.println("FAIL");
			System.out.println(e.getLocalizedMessage());
		}
	}
}
