# SKM neo4j database

## Deployment

```bash
docker compose up --build -d
```

This creates a docker container with neo4j (5.26) and prepoulates it by running all the `.cypher` scripts in the `/src/cypher` folder.

# References and resources

* [PSS database](https://skm.nib.si/documentation/pss-db-deployment)
* [GitHub issue - allow for startup scripts](https://github.com/neo4j/docker-neo4j/issues/166#issuecomment-2136575757)