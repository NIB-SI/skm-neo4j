#!/bin/bash

# Crash with error
set -e

source /src/.env

export NEO4J_AUTH="${NEO4J_USER}/${NEO4J_PASSWORD}"

# turn on bash's job control
set -m

# Start the primary process and put it in the background
echo "Starting Neo4j"
/startup/docker-entrypoint.sh neo4j &

# Wait for Neo4j to start
wget --quiet --tries=10 --retry-connrefused=on --waitretry=2 -O /dev/null http://localhost:7474

num_nodes=$(cypher-shell -u neo4j -p password --format plain "MATCH (n) RETURN count(*)" | tail -n1)
echo "Number of nodes in the graph: ${num_nodes}"

echo "Running cypher scripts: "

# Allows patterns which match no files to expand to a null string, rather than themselves
# Avoids (No such file or directory) if no .cyp files are in the logs directory
shopt -s nullglob

# Start the helper process
for f in /src/cypher/*.cypher; do
    echo "    ${f}"
    cypher-shell -u ${NEO4J_USER} -p ${NEO4J_PASSWORD} \
				 -a localhost:7687 \
				-f $f
done

# unset nullglob
shopt -u nullglob

echo "Run all cypher scripts."

num_nodes=$(cypher-shell -u neo4j -p password --format plain "MATCH (n) RETURN count(*)" | tail -n1)
echo "Number of nodes in the graph: ${num_nodes}"

# Bring the primary process back into the foreground
fg %1
