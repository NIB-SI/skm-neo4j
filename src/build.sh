#!/bin/bash

# Crash with error
set -e

export NEO4J_AUTH=${MY_NEO4J_USER}/${MY_NEO4J_PASSWORD}

# turn on bash's job control
set -m

# Start the primary process and put it in the background
echo "Starting Neo4j"
/startup/docker-entrypoint.sh neo4j &

# Wait for Neo4j to start
wget --quiet --tries=10 --retry-connrefused=on --waitretry=2 -O /dev/null http://localhost:7474

num_nodes=$(cypher-shell -u ${MY_NEO4J_USER} -p ${MY_NEO4J_PASSWORD} --format plain "MATCH (n) RETURN count(*)" | tail -n1)
echo "Number of nodes in the graph: ${num_nodes}"

echo "Running cypher scripts: "

# Allows patterns which match no files to expand to a null string, rather than themselves
# Avoids (No such file or directory) if no .cyp files are in the logs directory
shopt -s nullglob

# Start the helper process
for f in /src/cypher/*.cypher; do
    echo "    ${f}"
    cypher-shell -u ${MY_NEO4J_USER} -p ${MY_NEO4J_PASSWORD} \
				 -a localhost:7687 \
				-f $f || echo "failed"
done

# unset nullglob
shopt -u nullglob

echo "Run all cypher scripts."

num_nodes=$(cypher-shell -u ${MY_NEO4J_USER} -p ${MY_NEO4J_PASSWORD} --format plain "MATCH (n) RETURN count(*)" | tail -n1)
echo "Number of nodes in the graph: ${num_nodes}"

# Bring the primary process back into the foreground
fg %1