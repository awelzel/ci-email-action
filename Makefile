DOCKER ?= docker

test:
	$(DOCKER) build -f test.Dockerfile .
