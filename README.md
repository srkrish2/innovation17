## Installation
Dependencies:
- [pip](https://pip.pypa.io/en/stable/installing/) - will save you time installing the ones below 
- [CherryPy](http://docs.cherrypy.org/en/latest/install.html#installation)
- [MongoDB](http://www.mongodb.org/display/DOCS/Getting+Started)
- [PyMongo](http://api.mongodb.com/python/current/installation.html)
- [Jinja2](http://jinja.pocoo.org/docs/dev/intro/#installation)
- [dateutil](https://pypi.python.org/pypi/python-dateutil)

## Running the server
1. In one terminal, type `mongod` to start the database
2. In another terminal, go to your cloned directory of this repo and type `python server.py` to start the server
3. In browser, go to [http://localhost:8080](http://localhost:8080)

## Using mturk sandbox
- You can run mturk tests without payments via https://requestersandbox.mturk.com
- To configure the code, edit `mturk/mturk.properties`

## Frontend - server communication
### /problems page parser input
```
array of maps (dictionaries). each map has the following format:
{
  "title": string,
  "description": string,
  "problem_id": string,
  "time_created": string,
  "stage": string,
  "schema_count": int,
  "inspiration_count": int,
  "idea_count": int,
  "suggestion_count": int
  
  //// if stage=unpublished ////
  "edit_page_link": string,
  

  //// if stage=schema ////
  "schemas_page_link": string,
  "view_page_link": string
  
  //// if stage=inspiration ////
  "inspirations_page_link": string,


  //// if stage=idea ////
  "ideas_page_link": string,

  //// if stage=suggestion ////
  "suggestions_page_link": string
}
```

### /{{problem_slug}}/edit page parser input
```
"problem_id": string,
"schema_assignments_num": int,
"title": string,
"description": string
}
```

### /{{problem_slug}}/schemas page parser input
```
schemas = array of the format:
{
    "status" : int,
	"text" : string,
	"time_created" : string,
	"schema_id" : string,
	"worker_id" : string,
	"problem_id" : string
}
also problem_id, problem_stage, schemas_page_link, inspirations_page_link,ideas_page_link
```

### /{{problem_slug}}/inspirations page parser input
```
inspirations = array of the format:
{
    "status" : int,
	"source_link" : string,
	"inspiration_id" : string,
	"schema_id" : string,
    "schema_text": string,
	"time_created" : string,
	"summary" : string,
	"image_link" : string,
	"reason" : string,
	"worker_id" : string,
	"problem_id" : string,

}
also problem_id, problem_stage, schemas_page_link, inspirations_page_link,ideas_page_link
```


### /{{problem_slug}}/ideas page parser input
```
ideas = array of the format:
{
    "is_launched" : boolean,
	"feedbacks_num" : int,
	"text" : string,
	"inspiration_id" : string,
	"idea_id" : string,
	"time_created" : string,
	"slug" : string,
	"schema_id" : string,
	"worker_id" : string,
	"problem_id" : string,
	"suggestions_page_link": string
}
also problem_id, problem_stage, schemas_page_link, inspirations_page_link,ideas_page_link
```

### /idea/{{idea_slug}}/suggestions page parser input
```
feedbacks = 
{
  "feedback_id":string,
  "feedback_text" : string,
  "suggestions" : [{ //array of suggestions
      "time_created" : string,
      "suggestion_id" : string,
      "worker_id" : string,
      "text": string
  }]
}
also idea_id, idea_text, problem_id
```

### /problem/{{problem_slug}}/suggestions page parser input
```
array of ideas:
{
    "idea_id" : string
    "text" : string
    "feedbacks": [{ //array of feedbacks:
        "feedback_id":string,
        "feedback_text" : string,
        "suggestions" : [{ //array of suggestions
            "time_created" : string,
            "suggestion_id" : string,
            "worker_id" : string,
            "text": string
        }]
    }]
}
also problem_id
```


### /save_problem POST request
input
```
{
  "title": string,
  "description": string,
  "schema_assignments_num": int,
  "lazy": boolean,
  "problem_id": string or null
}
```
output
```
{
  "success": boolean,
  "url": string,       //only if success=true
}
```


### /submit_problem POST request
input
```
{
  "title": string,
  "description": string,
  "schema_assignments_num": int,
  "lazy": boolean
}
```
output
```
{
  "success": boolean,
  "url": string,       //only if success=true
}
```

### /publish_problem POST request
input
```
{
  "problem_id": string
}
```
output
```
{
  "success": boolean,   
  "new_id": string      //only if success=true
}
```

### /post_sign_in POST request
input
```
{
  "name": username or email string,
  "password": string
}
```
output
```
{
  "success": boolean,
  "url": string
}
```
### /post_new_account POST request
input
```
{
  "username": string,
  "email": string,
  "password": string
}
```
output
```
{
  "success": boolean,
  "url": string,       //only if success 
  "issue": string
}
```

### /get_count_updates GET request
output
```
"ideas" : array of maps:
{
  "problem_id": string,
  "schema_count": int,
  "inspiration_count": int,
  "idea_count": int,
  "suggestion_count": int
}
```

### /delete_problem POST request
input
```
{
  "problem_id": string
}
```

### /post_problem_edit POST request
input
```
{
  "problem_id": string,
  "schema_assignments_num": int,
  "title": string,
  "description": string
}
```

### /post_idea_task POST request
input
```
{
  "problem_id": string,
  "count_goal": int
}
```
output
```
{
  "success": boolean,
  "url": string,       //only if success=true
}
```

### /post_inspiration_task POST request
input
```
{
  "problem_id": string,
  "count_goal": int
}
```
output
```
{
  "success": boolean,
  "url": string,       //only if success=true
}
```

### /post_reject POST request
```
{
  "to_reject": boolean,
  "type": "schema" or "inspiration" or "idea"
  "id": string
}
```
### /post_feedback POST request
```
{
  "idea_id": string,
  "feedbacks": array of strings,
  "count_goal": int
}
```
output
```
{
  "success": boolean,
  "suggestion_page_link": string
}
```

### /suggestion_updates POST request
input
```
{
  "problem_id": string
}
```
output
```
"ideas" = array of maps. each map has the following format:
{
  "idea_id": string,
  "suggestion_count": int
}
```

### /get_accepted_schemas_count POST request
input
```
{
  "problem_id": string
}
```
output
```
{
  "count": int
}
```

### /more_schemas POST request
input
```
{
    "problem_id": string,
    "count": int
}
```
output
```
{
    "success": boolean
}
```

### /more_suggestions GET request
input
```
{
    "feedback_id": string,
    "count": int
}
```
output
```
{
    "success": boolean
}
```


### /get_feedbacks POST request
input
```
{
    "idea_id": string
}
```
output
```
"feedbacks": array of maps:
{
    "feedback_id": string,
    "text": string,
}
```
