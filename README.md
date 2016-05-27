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


### /problems page parser input
```
array of maps (dictionaries). each map has the following format:
{
  "problem_id": string,
  "title": string,
  "description": string,
  "schema_count": int,
  "schema_count_goal": int
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
  "email_in_use": boolean,
  "username_taken": boolean
}
```





<!---
# disregard this for now, still in development
## Frontend - server communication

| Command                              | Input                              | Output                      |
|--------------------------------------|------------------------------------|-----------------------------|
| POST request to `/get_schemas`       | `{"problem_id": "%problem's id%"}` | See below                   |
| POST request to `post_new_project`   | See below                          | `{"success": boolean}`      |
| POST request to `post_new_account`   | See below                          | See below                   |
| POST request to `/post_sign_in`      | See below                          | See below                   |
| POST request to `/post_go_to_sign_in`| `{"previous_url": string}`         | `{"url": string}`           |


### /get_problems output example
```json
{
  "problems": [
    {
      "problem_id": "3P6ENY9P79WU3BGAM63UL8VPD6QHIA",
      "schema_count": "1",
      "description": "problem1"
    },
    {
      "problem_id": "3JYPJ2TAYI8261C84B5ERKKOJ58PFW",
      "schema_count": "1",
      "description": "problem2"
    }
  ]
}
```

### /get_schemas output example
```json
{
  "schemas": [
    {
      "text": "solution1",
      "time": "19 May 2016 12:19 PM",
      "worker_id": "A2IG0RMLWLDY0F",
      "problem_id": "3P6ENY9P79WU3BGAM63UL8VPD6QHIA"
    }
  ]
}
```
    
### /post_go_to_sign_in 
*input*
```
{
    "previous_url": string
}
```

*output*
```
{
    "url": string
}
```
-->
