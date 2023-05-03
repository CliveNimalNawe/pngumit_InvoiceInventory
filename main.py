from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')
  
@app.route("/invoice-page")
def invoice_page():
    return render_template("invoice.html")
  
@app.route("/inventory-page")
def inventory_page():
    return render_template("inventory.html")

@app.route("/profile-page")
def profile_page():
    return render_template("profile.html")

@app.route("/help-page")
def help_page():
    return render_template("help.html")

@app.route("/report-page")
def report_page():
    return render_template("report-page.html")

@app.route("/notification-page")
def notification_page():
    return render_template("notification.html")

@app.route("/item-page")
def item_page():
    return render_template("item.html")
  
@app.route("/item-page")
def customer_page():
    return render_template("item.html")



if__name__ = '__main__';
app.run(host='0.0.0.0', debug = True)

