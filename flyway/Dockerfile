# Use the official Flyway base image
FROM flyway/flyway:latest

# Set the working directory to /flyway/sql
WORKDIR /flyway/sql

# Copy the Flyway configuration file into the container
COPY ./flyway.conf /flyway/conf/flyway.conf

# Copy the migration scripts into the container
COPY ./migrations ./
