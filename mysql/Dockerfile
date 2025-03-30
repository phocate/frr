FROM mysql:8.0

# Arguments that can be overridden
ARG MYSQL_ROOT_PASSWORD=root_password
ARG MYSQL_DATABASE=frr
ARG MYSQL_USER=frr_user
ARG MYSQL_PASSWORD=frr_pass

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
ENV MYSQL_DATABASE=${MYSQL_DATABASE}
ENV MYSQL_USER=${MYSQL_USER}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD}

# Copy initialization SQL script
COPY ./init.sql /docker-entrypoint-initdb.d/

# Expose MySQL port
EXPOSE 3306

# Default command
CMD ["mysqld"]
