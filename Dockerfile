FROM neo4j:5.26-community 

COPY ./src /src
COPY .env /src/.env

RUN chmod +x /src/build.sh 

ENTRYPOINT ["/src/build.sh"]