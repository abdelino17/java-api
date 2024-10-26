# Java API

![springboot-3.3.5-informational](https://img.shields.io/badge/springboot-3.3.5-informational)
![Twitter Follow](https://img.shields.io/twitter/follow/abdelFare?logoColor=lime&style=social)

This repository contains code for a basic java api using the [SpringBoot framework](https://spring.io/projects/spring-boot).

This api will be used for [blog demo articles](https://blog.abdelfare.me).

## Installation method 1 (Run application locally)

1. Clone this Repo `git clone (https://github.com/abdelino17/java-api)`
2. Change into the Fast-Api folder `cd java-api`
3. Install the dependencies and build your executable `/gradlew build`
4. Run the app using `java -jar build/libs/webapp-0.0.1-SNAPSHOT.jar`

## Installation method 2 (Run Locally using Docker)

1. Ensure [Docker](https://docs.docker.com/install/) is installed.
2. Build your image `docker build . -t java-api:latest`
