install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python3 -m pytest -vv --cov=service tests/test_*.py

format:	
	black *.py service/*.py app/*.py

lint:
	#disable comment to test speed
	#pylint --disable=R,C --ignore-patterns=test_.*?py *.py mylib/*.py
	#ruff linting is 10-100X faster than pylint
	ruff check --ignore F403,F405,F841 *.py service/*.py

container-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

# Building the Docker image
docker-build:
    docker build -t 0xhzx/llmops:latest .

# Pushing the image to a container registry (e.g., Docker Hub)
docker-push:
    docker push 0xhzx/llmops:latest


refactor: format lint

deploy:
	#deploy goes here
		
all: install lint test format
