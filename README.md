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
  "schema_count": int,
  "schema_count_goal": int,
  "problem_id": string,
  "schemas_page_link": string,
  "time_created": string,
  "stage": string,
  "inspirations_page_link",
  "inspiration_count": int,        // only if stage=inspiration
  "inspiration_count_goal": int    // only if stage=inspiration
}
```

### /{{problem_title}}/schemas page parser input
```
array of maps (dictionaries). each map has the following format:
{
    "text": string,
    "time": "19 May 2016 12:19 PM",
    "worker_id": string,
    "schema_id": string
}
also problem_id. see render_schemas_page in server.py
```

### /{{problem_title}}/inspiration page parser input
```
array of maps (dictionaries). each map has the following format:
{
    "summary": string,
    "reason": string,
    "time": "19 May 2016 12:19 PM",
    "worker_id": string,
    "inspiration_id": string,
    "link": string,
    "problem_id": string,
    "problem_text": string,
    "schema_id":string,
    "schema_text": string
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
    "count": int
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


### /change_problem POST request
input
```
{
    "problem_id": string,
    "operation": "edit" or "view"
}
```
output
```

{
  "title": string,
  "description": string,
  "schema_count_goal": int
}
