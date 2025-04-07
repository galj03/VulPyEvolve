FROM ubuntu:latest
LABEL authors="galjo"

ENTRYPOINT ["top", "-b"]

#TODO: build project
#TODO: test project in docker image