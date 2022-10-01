# PROBLEM TO SOLVE:
*The monitoring system for online stores is manual, not automated and does not have a single standard for generating reports and storing them.*


# PROJECT REQUIREMENTS:

## **MAIN FUNCTIONALITY:**
> ## 1. Defining monitoring parameters
> 1. Select categories, subcategories, groups and subgroups
> 2. Select internet-stores
> 3. Select additional parameters, if they are
> 4. Push "create report" button.

> ## 2. Collecting and processing data
> 
> ## 3. Output data (report) in a specific format
> 
> ## 4. Saving data (report) to database

## **ADDITIONAL FUNCTIONALITY:**

## 1. CRUD operations with saved instances:
 - categories
 - subcategories
 - groups
 - subgroups
 - products
 - internet-shop urls
 - reports
 - users
 
## 2. AUTHORIZATION AND AUTHENTIFICATION
- register new user
- login
- logout
- delete profile

## 3. PAYABLE FUNCTIONALITY
### Drawing up detailed reports with:
- Company purchase price
- Company retail price
- Company marging
- add something else
- and else...
- and else...


# INPUT DATA:
## USER INFORMATION:
> - source: user input in UI
> - format: text -> JSON

## PRODUCT CATALOG:
> - source: user file from UI
> - format xls/xlsx -> JSON

> - later: integration with with company products

## INTERNET-SHOP URLS:
> - source: user input in UI
> - format: text
> - securuty: superuser authorization

## SYSTEM PARAMETERS:
> - source: user input in UI
> - format: text
> - securuty: superuser authorization


# OUTPUT DATA:
## MONITORING REPORTS:
> - source: this system
> - format: web-page/xls/xlsx/csv 
