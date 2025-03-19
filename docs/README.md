# SKM neo4j database

## Deployment

Environment variable file:
```bash
mv .env.example .env
```
Update/add any environemnt variables in the `.env` file. 

To run (in detached mode):

```bash
docker compose up --build -d
```

This creates a docker container with neo4j (5.26) and prepoulates it by running all the `.cypher` scripts in the `/src/cypher` folder.

Since the database is persistant in the mounted volumns, after the first deployment, (optionally) move the `.cypher` scripts, so that they are not attempted to be loaded again. 

# References and resources

* [PSS database](https://skm.nib.si/documentation/pss-db-deployment)
* [docker-neo4j: GitHub issue - allow for startup scripts](https://github.com/neo4j/docker-neo4j/issues/166#issuecomment-2136575757)
