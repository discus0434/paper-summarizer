# Deploy to Cloud Run (use CPU)

* * Currently, the CPU inference is too slow to be operational. *

Please refer to the following procedure, recognizing that there is a cost associated with deploying this bot. Please rewrite your own account, etc. as necessary.

* Before executing the following procedure, you need to enable the APIs around Cloud Run, Artifact Registry and Cloud Vision API according to the official documentation, and grant the necessary permissions to the CLI login user.

- Deploy as a service according to the following procedure.

```
export GCP_PROJECT_ID=<YOUR_PROJECT_ID>
export GCP_LOCATION=<YOUR_LOCATION ex. us, us-west1, etc>
export GCP_REGION=<YOUR_SERVICE_REGION ex. us-west1, etc>
export GCP_REPOSITORY_NAME=<YOUR_REPOSITORY_NAME ex. bot>
export GCP_IMAGE_NAME=<YOUR_IMAGE_NAME ex. paper-summarizer-bot>

# google cloud login and set deploy project
gcloud auth login
gcloud config set project ${GCP_PROJECT_ID}

# enable apis
gcloud services enable vision.googleapis.com artifactregistry.googleapis.com run.googleapis.com

# create a repository in Artifact Registry
gcloud artifacts repositories create ${GCP_REPOSITORY_NAME} --repository-format=docker --location=${GCP_LOCATION}
gcloud auth configure-docker ${GCP_LOCATION}-docker.pkg.dev

# docker build
# NOTE: Currently, we have not started to slim down the Docker image, we would like to slim it down by using python*-slim image base and copying it from the builder image.
make build

# docker push
make push

# create env yaml
make deploy
```

- On the slack api page, set the `Service URL` to Event Subscriptions > Enable Events > Request URL.
- Note: Due to a limit on Slack apps responses, we are getting multiple requests per PDF from Slack apps to Cloud Run.
Currently, a local file named `msg_id.log` is created, and requests with the same `client_msg_id` are not processed.
Please be careful when setting `max-instances` in Cloud Run to anything other than 1.

## Cleanup

- delete Cloud Run service

```bash
make delete
```
