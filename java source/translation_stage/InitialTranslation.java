package translation_stage;

import org.apache.velocity.VelocityContext;

public class InitialTranslation extends PostTranslationHIT {
	
	String language;

	@Override
	String getPropertiesFilePath() {
		return String.format("./initial_translation_%s.properties", language);
	}

	@Override
	String getTemplateFilePath() {
		return String.format("./initial_translation_%s.xml", language);
	}

	@Override
	void fillVelocityContext(String[] args, VelocityContext context) {
		String english = args[0];
		context.put("english", english);
	}
	
	public InitialTranslation(String language) {
		this.language = language;
	}
}
