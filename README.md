[![CI](https://github.com/0xhzx/codeReview-gitlab/actions/workflows/cicd.yml/badge.svg?branch=main)](https://github.com/0xhzx/codeReview-gitlab/actions/workflows/cicd.yml)

# Final Project - LLM-CodeReview-Gitlab

Link to my final demo video

## Requirements:

1. Has to be very well documented with a README.md that explains what the main purpose of the application is, how to set it up, and run it.
2. The documentation needs to have workable examples of the application.
3. It needs to have tests
4. The project should have automation with GitHub Actions that can produce a working container image. The resulting image should not include the LLM.

## Deliverables:
A fully working repository with documentation, tests, and an automated build

## Rubric:

#### Repository & Documentation
- Project purpose

The purpose of the LLM-Codereview application is to streamline and automate the process of code review in software development projects. It aims to improve the efficiency and effectiveness of code reviews by providing automated suggestions and feedback based on best coding practices.


- Architecture diagram

- Instructions for setup/running/testing the app including examples and screenshots

- Performance/evaluation results

- Unit tests for all core functionality (in /tests folder)

#### CI/CD Pipeline
- Use Github Actions or similar to trigger an automated CI/CD workflow on push/PR or manual trigger

- CI/CD pipeline should include all the stages:
```Makefile
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

```

#### Functionality & Performance
- Uses local .llamafile model outside the Docker container
- Chatbot runs successfully as a local containerized service
- Model selection 
- Frontend/UI 
- Code quality 

#### Bonus Points 
- Demonstrate that you've taken a risk to learn something new, incorporated a cool new framework/technology, or gone above and beyond the minimum requirements :rocket: