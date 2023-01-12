# PROBLEM TO SOLVE:
*The monitoring system for online stores is manual, not automated and does not have a single standard for generating reports and storing them.*


# PROJECT REQUIREMENTS:

## **MAIN FUNCTIONALITY:**
> ## 1. Defining monitoring parameters
> 1. Select categories, subcategories, groups and subgroups
> 2. Select internet-stores
> 3. Select additional parameters, if they are
> 4. Push "get report" button.

> ## 2. Collecting and processing data
> 1. Save reference shop's catalog to database.
> 2. Once a day scrap prices from all internet shops and save them to database.
> 3. Report by email if some new products appeared.
> 
> ## 3. Output data (report) in a json format
{
  "header": {
    "name": "string",
    "note": "string",
    "time_created": "2023-01-09:10:41",
    "user_name": "string"
  },
  "folders": [
    {
      "id": 0,
      "name": "string",
      "parent_id": 0,
      "el_type": 1
    }
  ],
  "products": [
    {
      "id": 0,
      "name": "string",
      "parent_id": 0,
      "el_type": 1,
      "prime_cost": 0
    }
  ],
  "retailers": [
    {
      "id": 0,
      "name": "string"
    }
  ],
  "content": [
    {
      "product_id": 0,
      "retailer_id": 0,
      "retail_price": 0,
      "promo_price": 0
    }
  ]
}
> 

## **ADDITIONAL FUNCTIONALITY:**

## 1. CRUD operations with saved instances:
 - categories
 - subcategories
 - groups
 - subgroups
 - products
 - internet-shop
 - reports
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
5. connect to running postgres container **docker exec -it <postgres_container_id> bash**
6. when connected - run **psql -U <psql_user_name>**
7. Now you can create database via **CREATE DATABASE <db_name>;** This name must be equal to name in docker-compose file.
8. Now connect to running container with application **docker exec -it <app_container_id> bash**
9. Make migrations via **alembic upgrade heads**
10. Fill .env file with correct data. Template is below.

**.env:**

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