from flask import Flask, redirect, render_template, url_for, request, make_response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from user import User
from database_initializer import initialize_database
from data_fetch import DataFetcher
from query import qty_query, sold_query, id_query, creds, items, mission, names, lastInv, invoice, allInv, inventory
import json
from reportlab.pdfgen import canvas
import decimal

app = Flask(__name__)

#generate better key later
app.secret_key = 'your_secret_key'
login_manager = LoginManager(app)

global_data=None

@app.before_request
def initialize():
    initialize_database(app)
    

@login_manager.user_loader
def load_user(user_id):
    db_connection=app.config['database']
    data_fetcher = DataFetcher(database=db_connection)
    user_data=data_fetcher.fetch_row(id_query % {'userID': (user_id)})
    
    if user_data:
        return User(user_data[0])
    return None

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

def protected_route():
    if current_user.is_authenticated:
        return render_template('/')
    else:
        return redirect(url_for('login'))
        

@app.route('/login', methods=['GET', 'POST'])
def login():
     
    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            params = {'uname': username,'pass': password}
            db_conn = app.config['database']
            data_fetcher = DataFetcher(database=db_conn)
            user_creds=data_fetcher.fetch_row(creds % params)

            if user_creds:
                user= User(user_creds[0])
                login_user(user)
                fnameLname= data_fetcher.fetch_row(names % username)
                global userNames
                userNames = fnameLname[0] + ' ' + fnameLname[1]
                return redirect(url_for('home'))
            else:
                error_message = 'Invalid username or password'
                return render_template('login.html', error=error_message)
    else:
        return render_template('login.html')
    
@app.route("/")
@login_required
def home():

    #Get the database connection from flask's g object
    db_connection = app.config['database']

    data_fetcher = DataFetcher(database=db_connection)

    data=data_fetcher.fetch_data(qty_query)

    return render_template('home.html', data=data)
  
@app.route("/invoice-page")
@login_required
def invoice_page():
    #Get the database connection from flask's g object
    db_connection = app.config['database']

    data_fetcher = DataFetcher(database=db_connection)

    
        # You can fetch other user data as needed


    data=data_fetcher.fetch_data(items)
    data1=data_fetcher.fetch_data(mission)
    invoice=data_fetcher.fetch_row(lastInv)
    ainv = data_fetcher.fetch_data(allInv)

    # Extract the invoice value from the tuple
    index = 0
    for i, char in enumerate(invoice[0]):
        if char.isdigit():
            index = i
            break

# Split the integer and string parts
    string_part = invoice[0][:index]
    integer_part = invoice[0][index:]
    num2 = "0001"
    desired_length = 4

    # Convert the numbers to integers for addition
    num1_int = int(integer_part)
    num2_int = int(num2)

    # Perform the addition
    result_int = num1_int + num2_int

    # Convert the result back to string and pad with zeroes up to the desired length
    result_str = str(result_int).zfill(desired_length)
    final_str = string_part+result_str

    formatted_data=[]
    for item in data1:
        mission_data = {
            'id' : item[0], 'name' : item[1], 'address' : item[2]

        }
        formatted_data.append(mission_data)
        dump = json.dumps(formatted_data)
        json_string=json.loads(dump)


        global global_data 
        global_data= json_string
   
    return render_template("invoice.html", data=data, data1=json_string, Uname=current_user, inv=final_str, allInvoices=ainv )
  
@app.route("/inventory-page")
@login_required
def inventory_page():
    db_connection = app.config['database']
    data_fetcher = DataFetcher(database=db_connection)
    # You can fetch other user data as needed
    inventorydata=data_fetcher.fetch_data(inventory)
    return render_template("inventory.html", inventory=inventorydata)

@app.route("/profile-page")
@login_required
def profile_page():
    return render_template("profile.html")

@app.route("/help-page")
@login_required
def help_page():
    return render_template("help.html")

@app.route("/report-page")
@login_required
def report_page():
    return render_template("report.html")

@app.route("/notification-page")
@login_required
def notification_page():
    return render_template("notification.html")

@app.route("/item-page")
@login_required
def item_page():
    return render_template("item.html")
  
@app.route("/customer-page")
@login_required
def customer_page():
    return render_template("customer.html")

@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for('home'))

@app.route('/preview-invoice', methods=['GET', 'POST'])
def preview_invoice():
    if request.method == 'POST':
        # Collect the necessary information from the form
        invNo = request.form.get('inv_no')
        itContact = request.form.get('it_contact')
        missContact = request.form.get('contact_person')
        billTo= request.form.get('mission_entity')
        dept = request.form.get('mission_dept')
        address=request.form.get('address')
        # ... collect other details
        description = []
        price=[]
        quantities = []
        total_price = []
        items = []
        # Iterate over the items in the data
        for item in request.form:
            # Check if the field ID ends with '_checkbox'
            if item.endswith('_input'):
                # Extract the ID without the '_checkbox' suffix
                field_id = item[:-6]

                # Retrieve the value of the checkbox
                value = request.form.get(item)
                value1= request.form.get(f"{field_id}_price")
                # Retrieve the value of the corresponding quantity field
                quantity = request.form.get(f"{field_id}_quantity")
                if quantity and quantity.strip():
                
                    # Append the values to the respective lists
                    uitems = {'description' : value, 'price' : value1, 'quantity': quantity}
                    items.append(uitems)
                    dump = json.dumps(items)
                    json_string=json.loads(dump)
                    description.append(value)
                    price.append(value1)
                    quantities.append(quantity)
        total_cost = 0
        for x, y in zip(price, quantities):
            decX=decimal.Decimal(x)
            intY=int(y)
            results= decX * intY
            total_price.append(results)
        
        for item in total_price:
            total_cost += item
        # Render the preview template with the collected data
        return render_template('preview.html', it=itContact, bill=billTo, add=address, missContact=missContact, dept=dept, sel=description, price=price, qua= quantities, inv=invNo, totalprice=total_price, totalcost=total_cost, items=items, dlist=json_string)

    return render_template('input.html')

@app.route('/generate-invoice')
def generate_invoice():
    # Create a new PDF document
    filename = 'generated_pdf.pdf'
    pdf_path = f"extra/{filename}"

    # Create a canvas object to draw on the PDF
    pdf_canvas = canvas.Canvas(pdf_path)

    # Draw some text on the PDF
    pdf_canvas.drawString(100, 700, "Hello, this is a generated PDF!")

    # Save the canvas contents to the file
    pdf_canvas.showPage()  # Add a page break
    pdf_canvas.save()

    # Create a response with the PDF file
    response = make_response(open(pdf_path, 'rb').read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'

    return response

@app.route('/mission-entity-details', methods=['POST'])
def mission_entity_details():
    global global_data
    mission_data=global_data
    selected_id = request.json['id']

    item_data = next((item for item in mission_data if item['id'] == selected_id), None)
    return jsonify(item_data)

@app.route('/invoice-entry', methods=['POST'])
def invoice_entry():
    
    invNo = request.form.get('inv')
    missContact = request.form.get('missContact')
    itContact = request.form.get('it')
    billTo= request.form.get('bill')
    dept= request.form.get('dept')
    cost = request.form.get('cost')
    db_conn = app.config['database']
    data_fetcher = DataFetcher(database=db_conn)
    data=(invNo, billTo, dept, itContact, missContact, cost)
    data_fetcher.insert_data(invoice, data)
    
    return redirect(url_for('invoice_page'))

if__name__ = '__main__'

app.run(host='0.0.0.0', debug = True)

