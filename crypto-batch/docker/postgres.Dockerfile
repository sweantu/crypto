FROM postgres:15

# Copy init scripts into the standard init directory
COPY init.sql /docker-entrypoint-initdb.d/