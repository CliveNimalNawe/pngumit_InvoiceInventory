#Define your queries here
#Please make sure to always import new query variables in the 'main.py' file.

#Login Queries
id_query="Select username from users WHERE username = '%(userID)s'"
creds="SELECT username FROM users WHERE username = '%(uname)s' AND password = '%(pass)s'"
names="SELECT fname, lname FROM it_contact WHERE uname='%s'"

#Query to get all invetory
inventory = "SELECT inventory.*, items.itm_model FROM inventory RIGHT JOIN items ON inventory.itm_id=item_id"
#Query to get total of a type of item in stock.
qty_query="SELECT DISTINCT itm_name, itm_img_url, curr_qty, tot_qty FROM items"

#Query to get last invoice no
lastInv="SELECT inv_no FROM invoices ORDER BY inv_no DESC LIMIT 1"
allInv="SELECT * FROM invoices"

#Query for invoice details
inv_basic="SELECT * FROM invoices WHERE inv_no=%s"
inv_details="SELECT * FROM invoice_items WHERE inv_no=%s"

#Query to get sold number of item
sold_query="SELECT itm_name, (tot_qty-curr_qty) AS itm_sold, tot_qty FROM items WHERE itm_name='{solditem}';"
items="SELECT itm_brand, itm_name, itm_model, itm_price, date_stocked FROM it_stock_db.items where curr_qty > 0"

#Query for mission address
mission="SELECT * FROM mission_entity"
add="SELECT * FROM mission_entity WHERE mission_id = %s"

#Insert invoice
invoice="INSERT INTO `invoices` (`inv_no`, `inv_date_time`, `inv_bill_to`, `inv_mission_dept`, `inv_it_contact`, `inv_mission_contact`, `inv_amount`) VALUES (%s, NOW(), %s, %s, %s, %s, %s);"
inv_itm= "INSERT INTO `invoice_items` (`quantity`, `description`, `unit_price`, `total_price`, `inv_no`) VALUES (%s, %s, %s, %s, %s)"

#Delete
delete_details="DELETE FROM `invoice_items` WHERE inv_no = %s"
delete_invoice="DELETE FROM `invoices` WHERE inv_no = %s"

#Query Mission Entities
entities= "SELECT * FROM mission_entity"
newEntity = "INSERT INTO `mission_entity` (`mission_id`, `mission_name`, `mission_addr`) VALUES (%s, %s, %s);"

#Update
update = "UPDATE `inventory` SET `flag` = %s WHERE (`itm_servtag` = %s);"

