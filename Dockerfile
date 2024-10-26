FROM maven:3.9-amazoncorretto-21 AS builder

WORKDIR /app

COPY pom.xml .

COPY src src

RUN mvn clean package

FROM amazoncorretto:21-alpine

COPY --from=builder /app/target/*.jar /app/java-api.jar

EXPOSE 8080

ENTRYPOINT ["java","-jar","/app/java-api.jar"]