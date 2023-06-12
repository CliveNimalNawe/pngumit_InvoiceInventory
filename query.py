#Define your queries here
#Please make sure to always import new query variables in the 'main.py' file.

#Login Queries
id_query="Select username from users WHERE username = '%(userID)s'"
creds="SELECT username FROM users WHERE username = '%(uname)s' AND password = '%(pass)s'"
names="SELECT fname, lname FROM it_contact WHERE uname='%s'"

#Query to get all invetory
inventory = "SELECT * FROM inventory"
#Query to get total of a type of item in stock.
qty_query="SELECT DISTINCT itm_name, itm_img_url, curr_qty, tot_qty FROM items"

#Query to get last invoice no
lastInv="SELECT inv_no FROM invoices ORDER BY inv_no DESC LIMIT 1"
allInv="SELECT * FROM invoices"

#Query to get sold number of item
sold_query="SELECT itm_name, (tot_qty-curr_qty) AS itm_sold, tot_qty FROM items WHERE itm_name='{solditem}';"
items="SELECT itm_brand, itm_name, itm_model, itm_price, date_stocked FROM it_stock_db.items where curr_qty > 0"
mission="SELECT * FROM mission_entity"

#Insert invoice
invoice="INSERT INTO `invoices` (`inv_no`, `inv_date_time`, `inv_bill_to`, `inv_mission_dept`, `inv_it_contact`, `inv_mission_contact`, `inv_amount`) VALUES (%s, NOW(), %s, %s, %s, %s, %s);"