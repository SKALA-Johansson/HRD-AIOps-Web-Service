# Build stage
FROM gradle:8-jdk21 AS build
WORKDIR /app
COPY . .
RUN ./gradlew bootJar -x test

# Run stage
FROM eclipse-temurin:21-jre-jammy
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 9001
ENTRYPOINT ["java", "-jar", "app.jar"]
