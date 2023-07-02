# Running Locally

Install environment
`python3 -m venv .venv`

Activate venv
`. .venv/bin/activate`

Install Flask
` pip install Flask`

or run requirements.text to also install dependencies
`pip install -r requirements.txt`

Run file
`flask run`
or to be able to share to other device on same network
`flask run --host=0.0.0.0`
or on debug mode
`flask run --debug`
if the file is not named `app`
`flask --app main run` (main is the name of the file)

