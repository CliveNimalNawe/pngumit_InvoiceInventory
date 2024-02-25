'''
Main Flask app for the PNGUM IT Inventory System Created By Clive Nawe
'''
from flask import Flask, redirect, render_template, flash, url_for, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from user import User
from database_initializer import initialize_database
from data_fetch import DataFetcher
from query import qty_query, id_query, names, inventory, delete_details, delete_invoice, entities, newEntity, update, itemCatalog, newItem
import bcrypt as hash
from routes.route_generatePDF import routeGeneratePDF_bp as generatePDF
import logging

# Configure logging to write messages to a file
logging.basicConfig(filename='example.log', level=logging.DEBUG)


def create_app():
    app = Flask(__name__)
    bcrypt = Bcrypt(app)
    app.register_blueprint(generatePDF)

    #generate better key later
    app.secret_key = 'your_secret_key'
    login_manager = LoginManager(app)

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
            db_conn = app.config['database']
            data_fetcher = DataFetcher(database=db_conn)

            # Retrieve the hashed password for the user
            stored_hashed_password, salt = data_fetcher.fetch_hashed_password(username)

            if stored_hashed_password and salt:
                byte_password=bytes.fromhex(stored_hashed_password)
                byte_salt=bytes.fromhex(salt)
                # Hash the user-entered password with the stored salt
                hashed_password = hash.hashpw(password.encode('utf-8'), byte_salt)
                # Verify the hashed password using Flask-Bcrypt
                if hashed_password == byte_password:
                    user = User(username)
                    login_user(user)
                    fnameLname = data_fetcher.fetch_row(names % username)
                    session['userName'] = fnameLname[0] + ' ' + fnameLname[1]
                    #print(current_user.id)
                    return redirect(url_for('home'))
                else:
                    error_message = 'Invalid username or password'
                    return render_template('login.html', error=error_message)
            else:
                error_message = 'Invalid username'
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

    @app.route("/inventory-page")
    @login_required
    def inventory_page():
        db_connection = app.config['database']
        data_fetcher = DataFetcher(database=db_connection)
        # You can fetch other user data as needed
        inventorydata=data_fetcher.fetch_data(inventory)
        return render_template("inventory.html", inventory=inventorydata)

    @app.route("/change-password-page")
    @login_required
    def change_password_page():
        test= session['userName']
        return render_template("change_password.html", Username=test)

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
        db_connection = app.config['database']
        data_fetcher = DataFetcher(database=db_connection)
        # You can fetch other user data as needed
        entitydata=data_fetcher.fetch_data(entities)
        return render_template("customer.html", customers=entitydata)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for('home'))

    #Endpoint to return the Entity Details to drop-down menu
    @app.route('/mission-entity-details', methods=['POST'])
    @login_required
    def mission_entity_details():
        mission_data=session['entityDetails']
        selected_id = request.json['id']
        item_data = next((item for item in mission_data if item['id'] == selected_id), None)
        return jsonify(item_data)

    @app.route('/cancel')
    def cancel():
        db_conn = app.config['database']
        data_fetcher = DataFetcher(database=db_conn)
        data=[session['inv']]
        s1=data_fetcher.delete_data(delete_details, data)
        s2=data_fetcher.delete_data(delete_invoice, data)
        print(s1)
        print(s2)
        return redirect(url_for('invoice_page'))

    @app.route('/add-customer', methods=['GET', 'POST'])
    @login_required
    def add_customer():
        if request.method == 'POST':
            # Collect the necessary information from the form
            id = request.form.get('mission_id')
            entity = request.form.get('mission_entity')
            address = request.form.get('address')
            db_conn = app.config['database']
            data_fetcher = DataFetcher(database=db_conn)
            data=(id, entity, address)
            #Save reponse from database entry
            result=data_fetcher.insert_data(newEntity, data)    
            print(id, entity, address)
            return redirect(url_for('customer_page'))

        return render_template('input.html')

    @app.route('/update-flag', methods=['POST'])
    @login_required
    def update_flag():
        try:
            # Get data from the request (assumes it's sent as JSON)
            data = request.get_json()
            flag = data['flag']
            servTag = data['id']
            updatedata=(flag, servTag)
            print("huh", updatedata)
            db_conn = app.config['database']
            data_fetcher = DataFetcher(database=db_conn)
            result = data_fetcher.update_data(update, updatedata)
            print(result)
            return jsonify({'success': 'Flag updated successfully'}), 200

        except Exception as e:
            print("The error", e)
            return jsonify({'error': str(e)}), 500
        
    @app.route('/change-password', methods=['POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_new_password = request.form['confirm_new_password']
            db_conn = app.config['database']
            data_fetcher = DataFetcher(database=db_conn)
            username=current_user.id
            # Retrieve the hashed password for the user
            hex_stored_password, hex_stored_salt = data_fetcher.fetch_hashed_password(username)
            stored_password = bytes.fromhex(hex_stored_password)
            stored_salt=bytes.fromhex(hex_stored_salt)
            hashed_current_password= hash.hashpw(current_password.encode('utf-8'), stored_salt)

            # Check if the current password matches the user's actual password
            if stored_password != hashed_current_password:
                flash('Incorrect current password', 'error')
            elif new_password != confirm_new_password:
                flash('New passwords do not match', 'error')
            else:
                # Hash the new password before updating it
                salt = hash.gensalt()
                hex_salt=salt.hex()
                hashed_password = hash.hashpw(new_password.encode('utf-8'), salt)
                hex_hashed_password=hashed_password.hex()
                update_password="UPDATE `it_stock_db`.`users` SET `password` = %s, `salt` = %s WHERE (`username` = %s);"
                data=(hex_hashed_password, hex_salt, username)
                data_fetcher.update_data(update_password, data)

                # Save the updated user to the database
                #db.session.commit()
                flash('Password updated successfully', 'success')
                return redirect(url_for('change_password_page'))

        return redirect(url_for('change_password_page'))

    @app.route('/catalog-page')
    @login_required
    def catalog_page():
        db_connection = app.config['database']
        data_fetcher = DataFetcher(database=db_connection)
        # You can fetch other user data as needed
        entitydata=data_fetcher.fetch_data(itemCatalog)
        return render_template("catalog.html", customers=entitydata)

    @app.route('/add-item', methods=['GET', 'POST'])
    @login_required
    def add_item():
        if request.method == 'POST':
            # Collect the necessary information from the form
            item_name = request.form.get('item_name')
            date_stocked = request.form.get('date_stocked')
            brand = request.form.get('brand')
            model = request.form.get('model')
            price = request.form.get('price')
            total_ordered = request.form.get('ordered')
            description = request.form.get('description')
            current_total = total_ordered
            db_conn = app.config['database']
            data_fetcher = DataFetcher(database=db_conn)
            data=(item_name, date_stocked, brand, model, price, description, current_total, total_ordered)
            #Save reponse from database entry
            result=data_fetcher.insert_data(newItem, data)
            #print(result)    
            return redirect(url_for('catalog_page'))

        return render_template('input.html')
    @app.route('/upload_csv')
    @login_required
    def upload_csv():
        success="True"
        return success
    
    return app

if __name__ == '__main__':
    app=create_app()
    app.run(host='0.0.0.0', debug = True)