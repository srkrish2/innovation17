package one_file;

import java.util.Arrays;

import idea_stage.IdeaHITResults;
import idea_stage.PostIdeaHIT;
import idea_stage.PostRankIdeaHIT;
import inspiration_stage.InspirationHITResults;
import inspiration_stage.PostInspirationHIT;
import inspiration_stage.PostRankInspirationHIT;
import schema_stage.PostRankSchemaHIT;
import schema_stage.RankSchemaHITResult;
import schema_stage.PostSchemaHIT;
import schema_stage.SchemaHITResults;
import suggestion_stage.PostRankSuggestionHIT;
import suggestion_stage.PostSuggestionHIT;
import suggestion_stage.SuggestionHITResults;

public class MTurkSDK {
	
	public static void main(String[] args) {
//		String[] args = {"InspirationHITResults", "32204AGAABCG7KAFWI3R0WIA8EAGHB"};
//		String[] args = {"IdeaHITResults", "32CAVSKPCEPO8RQWEYPNCO3U0X4U11"};
//		String[] args = {"PostIdeaHIT", "pr2222222blem", "http://www.bbc.com/sport/football/36669829", "", "explanation", "1"};
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
		case "RankHITResults":
			RankSchemaHITResult.main(args);
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
		case "PostIdeaHIT":
			PostIdeaHIT.main(args);
			break;
		case "IdeaHITResults":
			IdeaHITResults.main(args);
			break;
		case "PostRankIdeaHIT":
			PostRankIdeaHIT.main(args);
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
		default:
			System.out.println("not recognized");
			break;
		}
	}
}
