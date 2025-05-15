
VERSION := latest

all: build start

build:
	@echo "+++ Building docker image +++"
	docker build --pull --build-arg VERSION=$(VERSION) -t kalemena/photo-tools:$(VERSION) .

start:
	docker run -it --rm -v $(pwd):/projects kalemena/photo-tools:$(VERSION) bash
