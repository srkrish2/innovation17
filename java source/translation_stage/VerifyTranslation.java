package translation_stage;

import org.apache.velocity.VelocityContext;

public class VerifyTranslation extends PostTranslationHIT {
	String language;

	@Override
	String getPropertiesFilePath() {
		return String.format("./verify_translation_%s.properties", language);
	}

	@Override
	String getTemplateFilePath() {
		return String.format("./verify_translation_%s.xml", language);
	}

	@Override
	void fillVelocityContext(String[] args, VelocityContext context) {
		String english = args[0];
		String improved = args[1];
		context.put("english", english);
		context.put("improved", improved);
	}

	public VerifyTranslation(String language) {
		this.language = language;
	}
}
