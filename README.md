# PROBLEM TO SOLVE:
*The monitoring system for online stores is manual, not automated and does not have a single standard for generating reports.*


# PROJECT REQUIREMENTS:

## **MAIN FUNCTIONALITY:**
> ## 1. Defining monitoring parameters
> 1. Select categories, subcategories, groups or products.
> 2. Apply filter for:
> 3. Internet-stores.
> 4. Additional parameters, if they are.
> 5. Your report is ready.

> ## 2. Collecting and processing data
> 1. Save reference shop's catalog to database.
> 2. Once a day scrap prices from all internet shops and save them to database.
> 3. Report by email if some new products appeared.
> 
> ## 3. Output data (report) in a json format
*need to be added...*
> 

## **ADDITIONAL FUNCTIONALITY:**

## 1. CRUD operations with saved instances:
 - categories
 - subcategories
 - groups
 - products
 - internet-shop
 - users
 
## 2. AUTHORIZATION AND AUTHENTIFICATION
- register new user
- edit profile
- login
- logout
- delete user

## 3. PAYABLE FUNCTIONALITY
### Drawing up detailed reports with:
- Company purchase price
- Company retail price
- Company marging
- add something else
- and else...


# DEPLOY PROCESS:
1. Clone this repo.
2. cd /root folder (where docker-compose.yml is situated).
3. run **docker-compose up** to download and build images, create db volume.
4. follow the instructions on https://hub.docker.com/_/postgres
5. run psql on running postgres container **docker exec -it <postgres_container_id> psql -U <psql_user_name>**
6. Now you can create database via **CREATE DATABASE <db_name>;** This name must be equal to name in docker-compose file.
7. Now connect to running container with application **docker exec -it <app_container_id> bash**
8. Make migrations via **alembic upgrade heads**
9. Fill .env file with correct data. Template is below.

**.env file content:**

- SECRET_KEY=
- ALGORITHM=
- ACCESS_TOKEN_EXPIRE_MINUTES=

- POSTGRES_DRIVER=
- POSTGRES_USER=
- POSTGRES_PASSWORD=
- POSTGRES_HOST=
- POSTGRES_PORT=
- POSTGRES_BASE_NAME=

- MAIN_PARSER=

- TAVRIA_URL=
- TAVRIA_TEST_URL=
- TAVRIA_CONNECTIONS_LIMIT=
- TAVRIA_FACTORIES_PER_SESSION=
- TAVRIA_SESSION_TIMEOUT_SEC=