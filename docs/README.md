# README! 

For on-dev purposes use branch v0.0.3. 

# SKM neo4j database manual

This document is in development [here](https://docs.google.com/document/d/1AuAAfYakcSc04a0oggwkTqQybx8QemAau_yvpneRIKg/edit?usp=sharing). Please request acess to edit that document, as this is simply a pandoc conversion atm. 

## Index
#### **[Naming conventions](#naming-conventions) 1**

#### **[Schema](#schema) 1**

* [Node labels](#node-labels) 2
* [Relationship Types](#relationship-types) 2
* [Properties](#properties) 2

#### **[Defined reactions](#defined-reactions) 5**

* [binding / oligomerisation](#binding-oligomerisation) 5
* [catalysis / auto-catalysis](#catalysis-auto-catalysis) 5
* [protein activation](#protein-activation) 5
* [transcriptional / translational induction](#transcriptional-translational-induction) 5

#### **[Example cypher](#example-cypher) 6**

#### **[Installation and deployment by Docker](#installation-and-deployment-by-docker) 7**

* [Repository structure](#repository-structure) 7 
* [Set up neo4j database](#set-up-neo4j-database) 7
* [Link the neo4j database to a Jupyter notebook](#link-the-neo4j-database-to-a-jupyter-notebook) 8
* [Remove database](#remove-database) 8
* [Dump a neo4j graph from Docker](#dump-a-neo4j-graph-from-docker) 9

#### **[Q and A](#q-and-a) 10**

---

## 1. Naming conventions

  - > Node labels: UpperCamelCase

  - > Relationship types: UPPER\_SNAKE\_CASE

  - > Property keys: snake\_case


## 2. Schema
    
### 2.1.  Node labels

| **Type**          | **Group**                | **Note** |
| ----------------- | ------------------------ | -------- |
| Clade             | family/clade definitions |          |
| Family            | family/clade definitions |          |
| Metabolite        | metabolite               |          |
| PathogenCoding    | component                |          |
| PlantAbstract     | component                |          |
| PathogenNonCoding | component                |          |
| PlantCoding       | component                |          |
| Complex           | component                |          |
| PlantNonCoding    | component                |          |
| Process           | component                |          |
| PseudoNode        | pseudo                   |          |

### 2.2. Relationship Types

| **Type**          | **Group**                     | **Note**                   | **In words**                                                          |
| ----------------- | ----------------------------- | -------------------------- | --------------------------------------------------------------------- |
| CONSUMED\_BY      | reaction                      | "left" side of a reaction  | Source node is consumed/taken up/catalysed by target node             |
| INHIBIT           | reaction                      |                            | Source node inhibits target node                                      |
| PRODUCE           | reaction                      | "right" side of a reaction | Target node is produced by source node                                |
| TRANSLOCATE\_FROM | reaction                      |                            | Source node is translocated from *source\_compartment* by target node |
| TRANSLOCATE\_TO   | reaction                      |                            | Target node is translocated to *target\_compartment* by source node   |
| ACTIVATE          | reaction                      |                            | Source node activates target node                                     |
| MEMBER\_OF        | family/clade definitions      |                            | Source node (clade) is a member of target node (family)               |
| COMPONENT\_OF     | complex/component definitions |                            | Source node is a component of target node (complex)                   |

### 2.3. Properties

| **Node/Edge** | **Group**    | **Property name**        | **Type**   | **Restricted to**                                    |
| ------------- | ------------ | ------------------------ | ---------- | ---------------------------------------------------- |
| \-            | \-           | added\_by                | string     |                                                      |
| \-            | \-           | additional\_information  | string     |                                                      |
| \-            | \-           | id()                     | number     |                                                      |
| \-            | \-           | model\_version           | string     |                                                      |
| \-            | \-           | process                  | list       |                                                      |
| edge          | reaction     | \<\>\_source\_orthologue | list       | \<\>\_orthologues of source node                     |
| edge          | reaction     | \<\>\_target\_orthologue | list       | \<\>\_orthologues of target node                     |
| ~~edge~~      | ~~reaction~~ | ~~comment~~              | ~~string~~ |                                                      |
| edge          | reaction     | literature\_sources      | list       | invented;database:\<\>;unknown;doi:\<\>;pmid:\<\>    |
| edge          | reaction     | name                     | string     |                                                      |
| edge          | reaction     | rate\_equation           |            |                                                      |
| edge          | reaction     | reaction\_id             | string     | UNIQUE(reactions)                                    |
| edge          | reaction     | reaction\_mechanism      | string     |                                                      |
| edge          | reaction     | source\_compartment      | string     | compartments                                         |
| edge          | reaction     | source\_form             | string     | gene;protein;protein\_active;complex;complex\_active |
| edge          | reaction     | species                  | list       | species                                              |
| edge          | reaction     | target\_compartment      |            | compartments                                         |
| edge          | reaction     | target\_form             | string     | gene;protein;protein\_active;complex;complex\_active |
| edge          | reaction     | trust\_level             | string     | R1;R2;Rx...                                          |
| node          | component    | \<\>\_orthologues        | list       |                                                      |
| node          | component    | clade                    | string     |                                                      |
| node          | component    | description              | string     |                                                      |
| node          | component    | family                   | string     |                                                      |
| node          | component    | gmm\_description         | string     |                                                      |
| node          | component    | gmm\_identifier          | string     |                                                      |
| node          | component    | gmm\_link                | string     |                                                      |
| node          | component    | gmm\_shortname           | string     |                                                      |
| node          | component    | gmm\_synonyms            | list       |                                                      |
| node          | component    | level                    | string     | orthologue;clade;family;pseudo                       |
| node          | component    | name                     | string     |                                                      |
| node          | component    | node\_id                 | string     | UNIQUE(nodes)                                        |
| node          | component    | species                  | list       | species                                              |
| node          | pseudo       | name                     | string     |                                                      |
| node          | pseudo       | reaction\_id             | string     |                                                      |

## 3.  Defined reactions
    
### binding / oligomerisation

> ![](media/image4.png)

### catalysis / auto-catalysis

> ![](media/image3.png)

### protein activation

> ![](media/image2.png)

### transcriptional / translational induction

> ![](media/image1.png)

## 4. Example cypher

Fetch all nodes:

    MATCH (n) RETURN DISTINCT n.name AS name, n.level AS level

## 5. Installation and deployment by Docker
    
### Repository structure

Clone the repository to your computer:

    git clone <https://github.com//NIB-SI/>skm-neo4j.git

Or if you have already cloned it, update it:

    git pull

The repository is organised as follows:

> skm-neo4j
> 
> ├─ README.md
> 
> ├─ docker-compose
> 
> ├─ docker-entrypoint.sh
> 
> ├─ Dockerfile
> 
> ├─ **conf**
> 
> ├─ **logs**
> 
> ├─ **data**
> 
> ├─ **dumps**
> 
> ├─ **raw**
> 
> ├─ **import**
> 
> └─ **db**
> 
> ├─ **work**
> 
> └─ **docs**

repository root

docker compose file

neo4j startup script

neo4j docker build script

contains configuration files for neo4j

for neo4j logging

contains dumped databases

raw, original data

for neo4j importing

neo4j graph storage

work scripts & notebooks

documentation

### Set up neo4j database

To deploy the graph database on your computer you will need docker.

In the repository root folder (after downloading graph.dump), build the
neo4j container with the graph:

    docker build --tag skm-graph .

To run this image:

    docker run -it -p7474:7474 -p1337:1337 -p7687:7687 -$PWD/logs:/logs -v$PWD/conf:/conf skm-graph

And visit [http://localhost:7474](http://localhost:7474/). 

### Link the neo4j database to a Jupyter notebook

Start up the neo4j database and link a jupyter notebook using
docker-compose. To run the first time, navigate to the repo folder
(containing docker-compose.yml) and run:

    docker-compose up

Thereafter you can use:

    docker-compose start

To stop the containers, use:

    docker-compose stop

Or to stop and remove them:

    docker-compose down

Open your browser at the http://localhost:8888/?token=... link printed
to the terminal. If the logs are not printed, run

    docker-compose logs | grep 'http://localhost:.\*/?token' | tail -1

to find the correct link.

## Remove database

If you need to remove the graph image, first remove the container:

    docker-compose down

Or get the container ID from the first column in:

    docker ps -a | grep skm-graph

And delete it using:

    docker rm \<container ID\>

Then delete the image:

    docker rmi skm-graph

Delete the folder with the graph data (if it exists).

    sudo rm -rf data/db/

### (dev only) Dump a neo4j graph from Docker

In neo4j enterprise edition, follow instructions
[here](https://markhneedham.com/blog/2020/01/28/neo4j-database-dump-docker-container/).

For community edition, do the following (based on
[How do you perform a dump of a Neo4j database
within a Docker container?](https://serverfault.com/questions/835092/how-do-you-perform-a-dump-of-a-neo4j-database-within-a-docker-container)
):

1.  Start up a neo4j container, without starting the neo4j database:

    ```bash
    docker run \
    --volume=$PWD/data/db/:/data \
    --volume=$PWD/data/dumps:/dumps \
    --ulimit=nofile=40000:40000 \
    --name=dump \
    -it \
    skm-graph-dev \
    /bin/bash
    ```

2. Use neo4j-admin to dumb the graph:

    ```bash
    bin/neo4j-admin dump --database=skm --to=/dumps/skm-v<version number>.dump
    ```


3.  Ctrl + d to exit the container. Remove the container:

    ```bash
    docker rm dump
    ```

## 6. Q and A
    
    10. **Q:** Why do you not simply use “activates” (“inhibts”) edge
        for protein activation (protein deactivation) reactions?

**A:** allow for different input *form* of the target, and … inhibit is
not the same as deactivation of an activated protein

11. **Q:** Why ...

**A:** …

## 7. Flow chart questions to choose reaction type
