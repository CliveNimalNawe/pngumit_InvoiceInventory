from flask import Flask, render_template

app = Flask(__name__)

@app.route('/confirm')
def confirm():
    # Sample data for demonstration purposes
    item_name = "Laptop"
    item_quantity = 2
    item_price = 1000

    # Pass the variables to the template
    return render_template('confirm.html', item_name=item_name, item_quantity=item_quantity, item_price=item_price)
