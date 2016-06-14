## Installation
Dependencies:
 - [pip](https://pip.pypa.io/en/stable/installing/) - will save you time installing the ones below 
 - [CherryPy](http://docs.cherrypy.org/en/latest/install.html#installation)
 - [MongoDB](http://www.mongodb.org/display/DOCS/Getting+Started)
 - [PyMongo](http://api.mongodb.com/python/current/installation.html)
 - [Jinja2](http://jinja.pocoo.org/docs/dev/intro/#installation)
 - [PassLib](https://pythonhosted.org/passlib/install.html#installation-instructions)

## Running the server
1. In one terminal, type `mongod` to start the database
2. In another terminal, go to your cloned directory of this repo and type `python server.py` to start the server
3. In browser, go to [http://localhost:8080](http://localhost:8080)

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
  "schema_count_goal": int,
  "inspiration_count": int,
  "inspiration_count_goal": int,
  
  //// if stage=unpublished ////
  "edit_page_link": string,
  
  "schemas_page_link": string,
  "view_page_link": string,
  
  //// if stage=inspiration ////
  "inspirations_page_link": string,
  "view_page_link": string

}
```

### /{{problem_slug}}/edit page parser input
```
    "problem_id": string,
    "schema_count_goal": int,
    "title": string,
    "description": string
}
```

### /{{problem_slug}}/schemas page parser input
```
array of maps (dictionaries). each map has the following format:
{
    "text": string,
    "time": "19 May 2016 12:19 PM",
    "worker_id": string,
    "schema_id": string
}
also problem_id, problem_stage, stage_page_links
```

### /{{problem_slug}}/inspirations page parser input
```
array of maps (dictionaries). each map has the following format:
{
    "summary": string,
    "reason": string,
    "time": "19 May 2016 12:19 PM",
    "worker_id": string,
    "inspiration_id": string,
    "source_link": string,
    "image_link": string,
    "problem_id": string,
    "problem_text": string,
    "schema_id":string,
    "schema_text": string
}
also problem_id, problem_stage, stage_page_links
```

### /{{problem_slug}}/ideas page parser input
```
array of maps (dictionaries). each map has the following format:
{
    "text": string,
    "time_created": string,
    "worker_id": string,
    "idea_id": string,
    "problem_id": string,
    "problem_text": string,
    "schema_text": string,
    "inspiration_id": string,
    "inspiration_text": string,
    "launched": boolean,
    "suggestion_count": int,
    "suggestions_page_link": string  // if launched
}
also problem_id, problem_stage, stage_page_links
```

### /{{idea_slug}}/suggestions page parser input
```
array of maps:
{
    "text" : string,
	"idea_id" : string,
	"time_created" : string,
	"suggestion_id" : string,
	"worker_id" : string,
	"feedback_text" : string,
	"problem_id" : string
}
```


### /save_new_problem POST request
input
```
{
  "title": string,
  "description": string,
  "schema_count_goal": int
}
```
output
```
{
  "success": boolean,
  "url": string,       //only if success=true
}
```

### /post_new_problem POST request
input
```
{
  "title": string,
  "description": string,
  "schema_count_goal": int
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
array of maps. each map has the following format:
{
    "problem_id": string,
    "schema_count": int,
    "inspiration_count": int,
    "idea_count": int
}
```

### /post_schemas_for_inspiration POST request
input
```
{
    "schemas": [
        {"schema_id":string},
        {"schema_id":string}
    ]
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
    "schema_count_goal": int,
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
    "type": "schema" or "inspiration"
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
array of maps. each map has the following format:
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
