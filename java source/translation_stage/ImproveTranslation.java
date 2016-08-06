package translation_stage;

import org.apache.velocity.VelocityContext;

public class ImproveTranslation extends PostTranslationHIT {
	String language;

	@Override
	String getPropertiesFilePath() {
		return String.format("./improve_translation_%s.properties", language);

	}

	@Override
	String getTemplateFilePath() {
		return String.format("./improve_translation_%s.xml", language);
	}

	@Override
	void fillVelocityContext(String[] args, VelocityContext context) {
		String english = args[0];
		String initial = args[1];
		context.put("english", english);
		context.put("initial", initial);
	}
	
	public ImproveTranslation(String language) {
		this.language = language;
	}

}
