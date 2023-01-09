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
