PROJECT_DIRECTORY=$(shell pwd)/../..
IMAGE_NAME=${GCP_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_REPOSITORY_NAME}/${GCP_IMAGE_NAME}

echo_envs:
	@echo ${GCP_PROJECT_ID}
	@echo ${GCP_LOCATION}
	@echo ${GCP_REGION}
	@echo ${GCP_REPOSITORY_NAME}
	@echo ${GCP_IMAGE_NAME}

create_env_file:
	cat ${PROJECT_DIRECTORY}/.env | sed -e 's/=/: /' | sed -e 's/MAX_WORKERS: \(.*\)/MAX_WORKERS: \"\1\"/' > env.yaml

build:
	docker build \
		-t  ${IMAGE_NAME} \
		-f Dockerfile ${PROJECT_DIRECTORY}

push:
	docker push ${IMAGE_NAME}

deploy:
	cat ${PROJECT_DIRECTORY}/.env | sed -e 's/=/: /' | sed -e 's/MAX_WORKERS: \(.*\)/MAX_WORKERS: \"\1\"/' > env.yaml
	gcloud run deploy ${GCP_IMAGE_NAME} \
		--image=${IMAGE_NAME} \
		--region=${GCP_REGION} \
		--concurrency=1 \
		--cpu=1 \
		--memory=4Gi \
		--min-instances=0 \
		--max-instances=1 \
		--port=8080 \
		--timeout=900 \
		--execution-environment=gen2 \
		--env-vars-file=env.yaml \
		--allow-unauthenticated

delete:
	gcloud run services delete ${GCP_IMAGE_NAME} --region=${GCP_REGION}

test_run:
	docker run --rm -it \
		-p 8080:8080 \
		--env-file ${PROJECT_DIRECTORY}/.env \
		--env PYTHON_ENV=test \
		-v ${PROJECT_DIRECTORY}/app.py:/home/app.py \
		-v ${PROJECT_DIRECTORY}/src:/home/src \
		-v ./cache/.cache:/root/.cache \
		-v ./cache/.paddleocr:/root/.paddleocr \
		-v ./radius5-ml-research-18a8df47e1d3.json:/root/radius5-ml-research-18a8df47e1d3.json \
		--env GOOGLE_APPLICATION_CREDENTIALS=/root/radius5-ml-research-18a8df47e1d3.json \
		paper-summarizer:0.1.0 \
		/bin/bash -c "cd /home/${NAME} && uvicorn app:app --reload --port=8080 --host='0.0.0.0'"

run:
	docker run --rm -it \
		-p 8080:8080 \
		--env-file ${PROJECT_DIRECTORY}/.env \
		${IMAGE_NAME} \
		gunicorn \
		 	--bind :8080 \
			--workers 1 \
			--worker-class uvicorn.workers.UvicornWorker \
			--threads 2 \
			--timeout 0 \
			app:app

test_curl:
	curl -X 'POST' \
	  'http://localhost:8080/summarize' \
	  -H 'accept: application/json' \
	  -H 'Content-Type: application/json' \
	  -d '{"token": "aaaa", "type": "bbb", "event": {"text": "https://arxiv.org/abs/2306.12380", "type": "app_mention", "client_msg_id": "$(shell uuidgen)"}}'

docker_connect:
	docker run --rm -it \
		--env-file ${PROJECT_DIRECTORY}/.env \
	${IMAGE_NAME} \
		bash
