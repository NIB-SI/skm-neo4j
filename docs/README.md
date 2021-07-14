## SKM-neo4j database

```bash
git clone git@github.com:NIB-SI/skm-neo4j.git
cd skm-neo4j
git checkout v0.0.3

docker build . --tag skm-graph
docker run -it -p7474:7474 -p1337:1337 -p7687:7687 -v$PWD/conf:/conf skm-graph
```

Any changes made in the docker contaner will not be conserved between sessions. 

