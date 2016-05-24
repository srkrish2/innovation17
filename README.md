## Installation
Dependencies:
 - [pip](https://pip.pypa.io/en/stable/installing/) - not required, but will save you time
 - [CherryPy](http://docs.cherrypy.org/en/latest/install.html#installation)
 - [MongoDB](http://www.mongodb.org/display/DOCS/Getting+Started)
 - [PyMongo](http://api.mongodb.com/python/current/installation.html)

## Running the server
1. In one terminal, type `mongod` to start the database
2. In another terminal, go to your cloned directory of this repo and type `python server.py` to start the server
3. In browser, go to [http://localhost:8080](http://localhost:8080)

## Frontend - server communication

| Command                         | Input                              | Output               |
|---------------------------------|------------------------------------|----------------------|
| POST request to `/post_problem` | `{"problem": "%user's problem%"}`  | {"success": boolean} |
| GET request to `/get_problems`  | No input                           | See example below    |
| POST request to `/get_schemas`  | `{"problem_id": "%problem's id%"}` | See below            |
| POST request to `new_project`   | See below                          | See below            |
| POST request to `new_account`   | See below                          | See below            |
| POST request to `/sign_in`      | See below                          | See below            |


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
```json
{
  "title": string,
  "description": string,
  "category": string,
  "tags": [list of strings]
}
```

### /post_new_project output
```json
{
  "success": boolean,
  "url": string
}
```

### /post_new_account input
```json
{
  "username": string,
  "email": string,
  "password": string
}
```

### /post_new_account output
```json
{
  "success": boolean,
  "url": string
}
```

### /post_sign_in input
```json
{
    "name": username or email string,
    "password": string
}
```

### /post_sign_in output
```json
{
    "success": boolean,
    "url": string
}
```