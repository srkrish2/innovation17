package one_file;

import java.util.Arrays;

import idea_stage.IdeaHITResults;
import idea_stage.PostIdeaHIT;
import inspiration_stage.InspirationHITResults;
import inspiration_stage.PostInspirationHIT;
import inspiration_stage.PostRankInspirationHIT;
import inspiration_stage.RankInspirationHITResults;
import schema_stage.PostRankSchemaHIT;
import schema_stage.RankSchemaHITResults;
import schema_stage.PostSchemaHIT;
import schema_stage.SchemaHITResults;
import suggestion_stage.PostRankSuggestionHIT;
import suggestion_stage.PostSuggestionHIT;
import suggestion_stage.RankSuggestionHITResults;
import suggestion_stage.SuggestionHITResults;
import translation_stage.PostTranslationHIT;
import translation_stage.TranslationResults;

public class MTurkSDK {
	
	public static void main(String[] args) {
//		String[] args = {"InspirationHITResults", "32204AGAABCG7KAFWI3R0WIA8EAGHB"};
//		String[] args = {"IdeaHITResults", "32CAVSKPCEPO8RQWEYPNCO3U0X4U11"};
//		String[] args = {"RankHITResults", "3VIVIU06FKCGVPHLD3J7DD3M4ESIM7"};
		String command = args[0];
		args = Arrays.copyOfRange(args, 1, args.length);
		switch (command) {
		case "PostSchemaHIT":
			PostSchemaHIT.main(args);
			break;
		case "SchemaHITResults":
			SchemaHITResults.main(args);
			break;
		case "PostRankSchemaHIT":
			PostRankSchemaHIT.main(args);
			break;
		case "RankSchemaHITResults":
			RankSchemaHITResults.main(args);
			break;
		case "PostInspirationHIT":
			PostInspirationHIT.main(args);
			break;
		case "InspirationHITResults":
			InspirationHITResults.main(args);
			break;
		case "PostRankInspirationHIT":
			PostRankInspirationHIT.main(args);
			break;
		case "RankInspirationHITResults":
			RankInspirationHITResults.main(args);
			break;
		case "PostIdeaHIT":
			PostIdeaHIT.main(args);
			break;
		case "IdeaHITResults":
			IdeaHITResults.main(args);
			break;
		case "PostSuggestionHIT":
			PostSuggestionHIT.main(args);
			break;
		case "SuggestionHITResults":
			SuggestionHITResults.main(args);
			break;
		case "PostRankSuggestionHIT":
			PostRankSuggestionHIT.main(args);
			break;
		case "RankSuggestionHITResults":
			RankSuggestionHITResults.main(args);
			break;
		case "PostTranslationHIT":
			PostTranslationHIT.main(args);
			break;
		case "TranslationResults":
			TranslationResults.main(args);
			break;
		default:
			System.out.println("Command not recognized: "+command);
			break;
		}
	}
}
