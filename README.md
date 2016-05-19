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

| Command                      | Input                              | Output                                              |
|------------------------------|------------------------------------|-----------------------------------------------------|
| POST request to /postproblem | `{"problem": "%user's problem%"}`  | Can do success/fail or something else. Let me know. |
| GET request to /getproblems  | No input                           | See example below                                   |
| POST request to /getschemas  | `{"problem_id": "%problem's id%"}` | See below                                           |


### /getproblems output example
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

### /getschemas output example
```json
{
  "schemas": [
    {
      "assignment_id": "3WT783CTPBHWLFPIK62EDEQDTZ3CB3",
      "text": "solution1",
      "time": "19 May 2016 12:19 PM",
      "worker_id": "A2IG0RMLWLDY0F",
      "problem_id": "3P6ENY9P79WU3BGAM63UL8VPD6QHIA"
    }
  ]
}
```
