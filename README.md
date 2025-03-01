# PEINTAI

## How to run the project locally

### Activate the venv
`source .venv/bin/activate`

### To run the project
`python3 app.py`

### Deactivate the venv
`deactivate`

## How to create environment in AWS (Elastic Beanstalk)

### AWS init
`eb init`

### AWS create Elastic Beanstalk
`eb create peintai-prod --enable-spot`

### Set env variables
Go to the running environment, scroll down to Updates, monitoring and logging and set them in the env propertiy sections

### AWS deploy (to update with changes in the project the env when running)
`eb deploy`

### Check health
`eb health`

### Check logs
`eb logs`