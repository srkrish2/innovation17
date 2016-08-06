package translation_stage;

import java.io.StringWriter;
import java.util.Arrays;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.VelocityEngine;

import com.amazonaws.mturk.addon.HITProperties;
import com.amazonaws.mturk.requester.HIT;
import com.amazonaws.mturk.service.axis.RequesterService;
import com.amazonaws.mturk.util.PropertiesClientConfig;

public abstract class PostTranslationHIT {
	
	abstract String getPropertiesFilePath();
	abstract String getTemplateFilePath();
	abstract void fillVelocityContext(String[] args, VelocityContext context);
	
	void post(String[] templateArgs) {
		RequesterService service = new RequesterService(new PropertiesClientConfig());
		try {
			HITProperties props = new HITProperties(getPropertiesFilePath());

			HIT hit = service.createHIT(
			        null, // HITTypeId
			        props.getTitle(),
			        props.getDescription(),
			        props.getKeywords(),
			        makeQuestion(templateArgs),
			        props.getRewardAmount(),
			        props.getAssignmentDuration(),
			        props.getAutoApprovalDelay(),
			        props.getLifetime(),
			        1,    // maxAssignments
			        null, //requesterAnnotation
			        null, // qualificationRequirements
			        new String [] { "Minimal", "HITDetail", "HITQuestion", "HITAssignmentSummary" },
			        null, // uniqueRequesterToken
			        null, // assignmentReviewPolicy
			        null  // hitReviewPolicy
			);

			/*
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
	
	String makeQuestion(String[] templateArgs) throws Exception {
		VelocityEngine ve = new VelocityEngine();
        ve.init();
        Template t = ve.getTemplate(getTemplateFilePath(), "UTF-8");
        VelocityContext context = new VelocityContext();
        fillVelocityContext(templateArgs, context);
        StringWriter writer = new StringWriter();
        t.merge(context, writer);
		return writer.toString();
	}
	
	public static void main(String[] arrgs) {
		String problem = "People come in and out of a room frequently. The number of people who stay in a room changes all the time. There are many challenges of counting the number of people in a room automatically because people wear different clothes, are of different heights, sometimes carry things, and walk in a group. How to develop a real-time automatic approach to accurately count the number of people in a room or a building, or any other closed space?";
//		String initial = "有多人频繁地进出房间。待在房间里的人数一直再变。在数人数自动化上有许多挑战， 因为每个人穿不同的衣服、有着不同的身高、有时携带物品和走在一起。如何开发一个实时自动精准的方式数在房里、建筑物里或其它封闭空间里的人？";
//		String[] args = new String[] {"improve", "chinese", problem, initial};
//		String improved = "Люди часто входят и выходят из помещения. Количество людей, остающихся в помещении, постоянно меняется. Существует много трудностей при автоматическом подсчете количества людей в помещении, потому что люди одеты в разную одежду, имеют разный рост, иногда несут с собой вещи, ходят группами. Как разработать автоматический метод точного подсчета количества людей в помещении, здании или ином другом закрытом пространстве в режиме реального времени?";
		
//		String problem = "Vehicles are very well insulated to reduce noise. However, because of the noise reduction, drivers are distracted or not aware of their surroundings. Engineers would like to put microphones around the car so that it can hear audio events (e.g. approaching ambulances). The size of the microphone is a couple of millimeters. How should the microphones be encased and housed so that they capture external audio events while encountering minimal noise(mostly wind noise)?";
//		String improved = "В целях снижения уровня шума транспортные средства очень хорошо изолированы. Однако, из-за снижения уровня шума водители отвлечены или теряют бдительность к тому, что их окружает. Инженеры хотели бы установить микрофоны вокруг машины, чтобы она могла \"слышать\" звуковые события (например, приближение машины скорой помощи). Величина микрофона составляет несколько миллиметров. Каким образом микрофоны должны быть обрамлены и размещены, чтобы они могли захватывать внешние звуковые события в тоже время улавливая минимум шумов (в основном, шум ветра)?";
//		String[] args = new String[] {"verify", "russian", problem, improved};
		
		String improved = "有多人频繁地进出房间。待在房间里的人数一直在变。在自动化数人数上有许多挑战， 因为每个人穿不同的衣服、有着不同的身高、有时携带物品、有时走在一起。如何开发一个实时自动而精准的方式数在房間里、建筑物里或其它封闭空间里的人呢？";
		String[] args = new String[] {"verify", "chinese", problem, improved}; 
		
		String type = args[0];
		String language = args[1];
		args = Arrays.copyOfRange(args, 2, args.length);
		PostTranslationHIT poster;
		switch(type){
		case "initial":
			poster = new InitialTranslation(language);
			break;
		case "improve":
			poster = new ImproveTranslation(language);
			break;
		case "verify":
			poster = new VerifyTranslation(language);
			break;
		default:
			System.out.println("Flag not recognized: "+type);
			return;
		}
		poster.post(args);
	}
}
