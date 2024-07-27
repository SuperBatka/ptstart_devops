FROM postgres:15.0
ENV POSTGRES_PASSWORD=123


COPY init.sql /docker-entrypoint-initdb.d/init.sql
RUN chmod 777 /docker-entrypoint-initdb.d/init.sql