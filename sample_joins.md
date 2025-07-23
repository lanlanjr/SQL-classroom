# Basic SQL JOIN Examples - ClassicModels Database

This guide shows simple examples of JOIN operations using the ClassicModels database. JOINs are used to combine data from two or more tables.

## Important Tables

For these examples, we'll focus on these main tables:
- **customers**: Customer information (customerNumber, customerName, city, salesRepEmployeeNumber)
- **employees**: Employee information (employeeNumber, firstName, lastName, jobTitle)
- **orders**: Order information (orderNumber, orderDate, customerNumber)
- **products**: Product information (productCode, productName, buyPrice)

---

## 1. INNER JOIN

**What it does**: Shows only rows that exist in BOTH tables.

### Example: Show customers and their sales reps

```sql
SELECT 
    customerName,
    firstName,
    lastName
FROM customers
INNER JOIN employees ON customers.salesRepEmployeeNumber = employees.employeeNumber;
```

**Query Breakdown**:
- `SELECT`: Choose which columns to show in the result
- `customerName`: Get the customer's name from the customers table
- `firstName, lastName`: Get employee names from the employees table
- `FROM customers`: Start with the customers table
- `INNER JOIN employees`: Connect to the employees table
- `ON customers.salesRepEmployeeNumber = employees.employeeNumber`: Match records where the customer's sales rep ID equals the employee's ID

**Result**: Only customers who have a sales rep will show up. If a customer has no sales rep assigned, they won't appear in the results.

---

## 2. LEFT JOIN

**What it does**: Shows ALL rows from the first table, even if there's no match in the second table.

### Example: Show all customers (even those without a sales rep)

```sql
SELECT 
    customerName,
    firstName,
    lastName
FROM customers
LEFT JOIN employees ON customers.salesRepEmployeeNumber = employees.employeeNumber;
```

**Query Breakdown**:
- `SELECT`: Choose columns to display
- `FROM customers`: Start with customers table (this is the "left" table)
- `LEFT JOIN employees`: Connect to employees table (this is the "right" table)
- `ON customers.salesRepEmployeeNumber = employees.employeeNumber`: Match condition
- **Key difference**: LEFT JOIN keeps ALL customers, even if there's no matching employee

**Result**: All customers appear. If a customer has no sales rep, the firstName and lastName fields will be empty (NULL).

---

## 3. RIGHT JOIN

**What it does**: Shows ALL rows from the second table, even if there's no match in the first table.

### Example: Show all employees (even those with no customers)

```sql
SELECT 
    customerName,
    firstName,
    lastName
FROM customers
RIGHT JOIN employees ON customers.salesRepEmployeeNumber = employees.employeeNumber;
```

**Query Breakdown**:
- `FROM customers`: This is the "left" table
- `RIGHT JOIN employees`: This is the "right" table - we want ALL employees
- `ON customers.salesRepEmployeeNumber = employees.employeeNumber`: Match condition
- **Key difference**: RIGHT JOIN keeps ALL employees, even if they don't have any customers assigned

**Result**: All employees appear. If an employee has no customers, the customerName will be empty (NULL).

---

## 4. FULL JOIN

**What it does**: Shows ALL rows from BOTH tables, whether they match or not.

*Note: MySQL doesn't have FULL JOIN, but you can create the same result by combining LEFT and RIGHT JOIN.*

### Example: Show all customers and all employees

```sql
-- First part: All customers with their sales reps
SELECT 
    customerName,
    firstName,
    lastName
FROM customers
LEFT JOIN employees ON customers.salesRepEmployeeNumber = employees.employeeNumber

UNION

-- Second part: All employees (including those with no customers)
SELECT 
    customerName,
    firstName,
    lastName
FROM customers
RIGHT JOIN employees ON customers.salesRepEmployeeNumber = employees.employeeNumber
WHERE customerName IS NULL;
```

**Query Breakdown**:
- **First SELECT**: Gets all customers (using LEFT JOIN) - some may not have sales reps
- **UNION**: Combines results from two queries
- **Second SELECT**: Gets all employees who don't have customers (using RIGHT JOIN with WHERE customerName IS NULL)
- **WHERE customerName IS NULL**: Only gets employees who weren't matched in the first query

**Result**: Shows everyone - all customers and all employees, whether they're connected or not. This gives you a complete picture of both tables.

---

## Practice Examples

### Simple Example 1: Customers and their orders

```sql
SELECT 
    customerName,
    orderNumber,
    orderDate
FROM customers
INNER JOIN orders ON customers.customerNumber = orders.customerNumber
LIMIT 10;
```

**Query Breakdown**:
- Shows customers who have placed orders
- `customers.customerNumber = orders.customerNumber`: Matches customers to their orders using customer ID
- `LIMIT 10`: Only shows first 10 results

### Simple Example 2: Find customers without orders

```sql
SELECT 
    customerName
FROM customers
LEFT JOIN orders ON customers.customerNumber = orders.customerNumber
WHERE orderNumber IS NULL;
```

**Query Breakdown**:
- Uses LEFT JOIN to get all customers
- `WHERE orderNumber IS NULL`: Filters to only show customers who have no orders
- This is useful for finding inactive customers

---

## Key Points to Remember

**INNER JOIN**: Only shows matches from both tables
- Use when you only want records that exist in both tables
- Most restrictive type of JOIN

**LEFT JOIN**: Shows everything from the first table
- Use when you want all records from the first table, even if no match exists
- Most commonly used JOIN after INNER JOIN

**RIGHT JOIN**: Shows everything from the second table  
- Use when you want all records from the second table, even if no match exists
- Less common than LEFT JOIN

**FULL JOIN**: Shows everything from both tables
- Use when you want all records from both tables, whether they match or not
- Shows the complete picture of both tables

### Simple Rules:
1. **Always connect tables using their ID numbers** (like customerNumber, employeeNumber)
2. **Use simple column names in your SELECT** - don't overcomplicate at first
3. **Start with INNER JOIN**, then try LEFT JOIN once you understand the basics
4. **The ON clause is crucial** - it tells SQL how to match records between tables
5. **NULL values appear when there's no match** in LEFT, RIGHT, or FULL JOINs