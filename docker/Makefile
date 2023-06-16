NAME=pdf-summarizer
TAG=0.1.0
PROJECT_DIRECTORY=$(shell pwd)/..

build:
	docker build -t ${NAME}:${TAG} .

run:
	docker run -it \
		--name ${NAME} \
		-v ${PROJECT_DIRECTORY}:/home/${NAME} \
		--gpus all \
		-d --restart=always \
		-p 8760:8760 \
		${NAME}:${TAG} /bin/bash -c "cd /home/${NAME} && python3 app.py"

run-win:
	docker run -it \
		--name ${NAME} \
		-v ${PROJECT_DIRECTORY}:/home/${NAME} \
		--gpus all \
		-d --restart=always \
		-p 8760:8760 \
		${NAME}:${TAG}
