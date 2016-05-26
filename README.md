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

| Command                              | Input                              | Output                      |
|--------------------------------------|------------------------------------|-----------------------------|
| POST request to `/post_problem`      | `{"problem": "%user's problem%"}`  | {"success": boolean}        |
| GET request to `/get_problems`       | No input                           | See example below           |
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

### /post_new_project input
```
{
  "title": string,
  "description": string,
  "category": string,
  "tags": [list of strings]
}
```

### /post_new_account 
*input*
```
{
  "username": string,
  "email": string,
  "password": string
}
```

*output*
```
{
  "success": boolean,
  "email_in_use": boolean,
  "username_taken": boolean
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


### /post_sign_in 
*input*
```
{
    "name": username or email string,
    "password": string
}
```

*output*
```
{
    "success": boolean,
    "url": string
}
```
