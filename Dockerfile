FROM maven:3.9-amazoncorretto-23 AS builder

WORKDIR /app

COPY pom.xml .

COPY src src

RUN mvn clean package

FROM amazoncorretto:23-alpine

COPY --from=builder /app/target/*.jar /app/java-api.jar

EXPOSE 8080

USER java

ENTRYPOINT ["java","-jar","/app/java-api.jar"]