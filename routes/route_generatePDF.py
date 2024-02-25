# This route file is being used to organize all of the routes that generate PDFs
from flask import Blueprint, jsonify, render_template, session, Response, request, url_for, flash, redirect, current_app
from flask_login import LoginManager, login_required, current_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import json, decimal, os, datetime
from data_fetch import DataFetcher
from query import items, mission, lastInv, invoice, allQuotes, allInv, inv_itm, delete_details, delete_invoice, inv_basic, inv_details, add, insertQuotation, insertQuoteDetails, lastQuote, delete_qDetails, delete_qEntry, delete_quotation, allQuotedItems, quotationInfo, itemCatalog, updateComment,totalCostQuotedItems, getQNumber
import logging
routeGeneratePDF_bp=Blueprint('route_generatePDF', __name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Create a formatter and attach it to the console handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

def totalCost(quotationNumber):
    data_fetcher=DataFetcher(current_app.config['database'])
    data_fetcher.update_data(totalCostQuotedItems, (quotationNumber, quotationNumber))
    return "success?"

@routeGeneratePDF_bp.route("/quote-page")
@login_required
def quote():
    data_fetcher = DataFetcher(database=current_app.config['database'])
    quotations = data_fetcher.fetch_data(allQuotes)

    data=data_fetcher.fetch_data(items)
    data1=data_fetcher.fetch_data(mission)

    formatted_data=[]
    for item in data1:
        mission_data = {
            'id' : item[0], 'name' : item[1], 'address' : item[2]

        }
        formatted_data.append(mission_data)
        dump = json.dumps(formatted_data)
        json_string=json.loads(dump)

        session['entityDetails']= json_string
    return render_template('quote.html', quotations = quotations, data=data, data1=json_string, Uname=current_user.id)

@routeGeneratePDF_bp.route("/invoice-page")
@login_required
def invoice_page():
    #Get the database connection from flask's g object
    db_connection = current_app.config['database']

    data_fetcher = DataFetcher(database=db_connection)

    # You can fetch other user data as needed
    data=data_fetcher.fetch_data(items)
    data1=data_fetcher.fetch_data(mission)
    invoice=data_fetcher.fetch_row(lastInv)
    ainv = data_fetcher.fetch_data(allInv)

    if invoice == None:
        final_str="IT0000"
    
    else:

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
    return render_template("invoice.html", data=data, data1=json_string, Uname=current_user, allInvoices=ainv, inv=final_str)

@routeGeneratePDF_bp.route('/preview-quotation', methods=['GET', 'POST'])
@login_required
def preview_quotation():
    if request.method == 'POST':
        # Collect the necessary information from the form
        session['qIT'] = request.form.get('it_contact')
        session['qContact'] = request.form.get('contact_person')
        session['qEntity']= request.form.get('mission_entity')
        session['qDept'] = request.form.get('mission_dept')
        session['qAdd']=request.form.get('address')
        # ... collect other details
        description = []
        price=[]
        quantities = []
        total_price = []
        items = []
        itemids = []
        # Iterate over the items in the data
        for item in request.form:
            # Check if the field ID ends with '_checkbox'
            if item.endswith('_input'):
                # Extract the ID without the '_checkbox' suffix
                field_id = item[:-6]

                # Retrieve the value of the checkbox
                value = request.form.get(item)
                value1= request.form.get(f"{field_id}_price")
                value2= request.form.get(f"{field_id}_id")
                # Retrieve the value of the corresponding quantity field
                quantity = request.form.get(f"{field_id}_quantity")
                if quantity and quantity.strip():
                
                    # Append the values to the respective lists
                    uitems = {'description' : value, 'price' : value1, 'quantity': quantity, 'itemids' :value2}
                    items.append(uitems)
                    dump = json.dumps(items)
                    json_string=json.loads(dump)
                    description.append(value)
                    price.append(value1)
                    quantities.append(quantity)
                    itemids.append(value2)
        total_cost = 0
        for x, y in zip(price, quantities):
            decX=decimal.Decimal(x)
            intY=int(y)
            results= decX * intY
            total_price.append(results)
        
        for item in total_price:
            total_cost += item

        session['totalprice'] = total_price
        session['totalcost'] = total_cost
        session['dlist'] = json_string
        session['dateToday'] = datetime.date.today().strftime("%d/%m/%Y")

        #entry=invoice_entry()
        # Render the preview template with the collected datapython
        return render_template('quotation_preview.html')
    
    return render_template('input.html')

#This route handles AJAX request from quote.html. It facilates the data retrival for the pop-up modal
@routeGeneratePDF_bp.route('/get-quoted-items', methods=['POST'])
@login_required
def get_quotedItems():
    quotationNo=request.form.get('id')
    quotationNo=(quotationNo,)

    with DataFetcher(current_app.config['database']) as data_fetcher:
        try:
            catalog = data_fetcher.fetch_data(itemCatalog)
        except Exception as e:
            logger.error(f"Error during catalog: {e}")
        try:
            quotedItems = data_fetcher.fetch_data(allQuotedItems, quotationNo)
            #logger.info(f"Quoted Items: {quotedItems}")
        except Exception as e:
            logger.error(f"Error during Quoted Items: {e}")
        try:
            quotation = data_fetcher.fetch_row(quotationInfo, quotationNo)
            #logger.info(f"Quotation:{quotation}")
        except Exception as e:
            logger.error(f"Error during quotation: {e}")
            raise

    formatQuotedItems= [{'data': list(row)} for row in quotedItems]
    return jsonify(qItems=formatQuotedItems, qNo=quotationNo, quote=quotation, catalog=catalog)

@routeGeneratePDF_bp.route('/preview-invoice', methods=['GET', 'POST'])
@login_required
def preview_invoice():
    if request.method == 'POST':
        # Collect the necessary information from the form
        session['inv'] = request.form.get('inv_no')
        session['it'] = request.form.get('it_contact')
        session['missContact'] = request.form.get('contact_person')
        session['bill']= request.form.get('mission_entity')
        session['dept'] = request.form.get('mission_dept')
        session['add']=request.form.get('address')
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

        session['totalprice'] = total_price
        session['totalcost'] = total_cost
        session['dlist'] = json_string
        session['dateToday'] = datetime.date.today().strftime("%d/%m/%Y")

        # entry=invoice_entry()
        # Render the preview template with the collected datapython
        return render_template('invoice_preview.html')

    return render_template('input.html')

@routeGeneratePDF_bp.route('/quotation-entry')
@login_required
def quote_entry():
    comments=""
    missContact =  session['qContact']
    itContact = session['qIT']
    billTo= session['qEntity']
    dept= session['qDept']
    db_conn = current_app.config['database']
    data_fetcher = DataFetcher(database=db_conn)
    data=(billTo, dept,  missContact, itContact, session['totalcost'], comments)
    #Save reponse from database entry
    entry_result=data_fetcher.insert_data(insertQuotation, data)
    
    #Upon succesfull entry, insert quote details into database
    if entry_result== True:
        try:
            quote=data_fetcher.fetch_row(lastQuote)
            quotationNo=quote[0]

            for item in session['dlist']:
                quantity = item['quantity']
                price = item['price']
                itemID = item['itemids']
                totalPrice=decimal.Decimal(price)*int(quantity)

                # SQL query to insert data into the database
                data = (quotationNo, itemID, quantity, price, totalPrice)
                success=data_fetcher.insert_data(insertQuoteDetails, data)

                if success != True:
                    data_fetcher.delete_data(delete_qDetails, quotationNo)
                    data_fetcher.delete_data(delete_quotation, quotationNo)

        except Exception as e:
        # Handle the exception, log it, or take appropriate action
            db_conn.connection.rollback()
            print("Exception occurred during transaction:", str(e))
        finally:
            db_conn.close()
        return redirect(url_for('route_generatePDF.quote'))
    else:
        flash('There was an error when inserting into the database!')
        return redirect(url_for('route_generatePDF.quote'))

@routeGeneratePDF_bp.route('/invoice-entry')
@login_required
def invoice_entry():
    
    invNo = session['inv']
    missContact =  session['missContact']
    itContact = session['it']
    billTo= session['bill']
    dept= session['dept']
    cost = session['totalcost'] 
    db_conn = current_app.config['database']
    data_fetcher = DataFetcher(database=db_conn)
    data=(invNo, billTo, dept, itContact, missContact, cost)
    #Save reponse from database entry
    entry_result=data_fetcher.insert_data(invoice, data)
    
    #Upon succesfull entry, download invoice pdf
    if entry_result== True:
        try:
            
            for item in session['dlist']:
                
                description = item['description']
                unit_price = item['price']
                total_price = str(float(item['price']) * int(item['quantity']))  # Calculate total price
                quantity = item['quantity']

                # SQL query to insert data into the database
                data = (quantity, description, unit_price, total_price, session['inv'])
                success=data_fetcher.insert_data(inv_itm, data)
                    
                if success != True:
                    data_fetcher.delete_data(delete_details, [session['inv']])
                    data_fetcher.delete_data(delete_invoice, [session['inv']])

        except Exception as e:
        # Handle the exception, log it, or take appropriate action
            db_conn.connection.rollback()
            print("Exception occurred during transaction:", str(e))
        finally:
            db_conn.close()
        return success
    else:
        flash('There was an error when inserting into the database!')
        return redirect(url_for('route_generatePDF.invoice_page'))

@routeGeneratePDF_bp.route('/download-pdf/<string:inv>')
@login_required
def download_pdf(inv):
    db_conn = current_app.config['database']
    data_fetcher = DataFetcher(database=db_conn)
    inv_basics=data_fetcher.fetch_row(inv_basic, [inv])
    inv_dets=data_fetcher.fetch_data(inv_details, [inv])
    session['inv'], date, session['bill'], session['dept'], session['it'], session['missContact'], total = inv_basics
    address=data_fetcher.fetch_row(add, [session['bill']])
    session['add']= address[2]
    session['totalcost'] = str(total)
    session['dateToday'] = date.strftime("%d/%m/%Y")
    session['dlist']=[]
    session['totalprice']=[]

    for item in inv_dets:
        item_dict = {
        'description': item[2],
        'price': str(item[3]),
        'quantity': str(item[1]),
         }
        
        session['dlist'].append(item_dict)
        session['totalprice'].append(str(item[4]))
    print(session['totalprice'])
    return generate_pdf()

@routeGeneratePDF_bp.route('/download-quote-pdf/<string:quote>')
@login_required
def download_quote_pdf(quote):
    with DataFetcher(current_app.config['database']) as data_fetcher:
        quote_details=data_fetcher.fetch_row(quotationInfo, [quote])
        quoted_items=data_fetcher.fetch_data(allQuotedItems, [quote])

    quotationNo, date, session['bill'], session['dept'], session['missContact'], session['it'], total, session['comments'] = quote_details
    address=data_fetcher.fetch_row(add, (session['bill'],))
    session['inv']=str(quotationNo).zfill(6)
    session['add']=address[2]
    session['totalcost']= str(total)
    session['dateToday'] = date.strftime("%d/%m/%y")
    session['dlist']=[]
    session['totalprice']=[]
    

    for item in quoted_items:
        item_dict={
            'itemCode': str(item[2]),
            'description':item[7]+" "+item[6]+" - "+item[8],
            'price': str(item[4]),
            'quantity': str(item[3])
        }
        session['dlist'].append(item_dict)
        session['totalprice'].append(str(item[5]))

    return generate_pdf()


@routeGeneratePDF_bp.route('/generate-pdf')
@login_required
def generate_pdf():

        filename = "IT_Invoice_"+session['inv']
        # Create a byte stream to hold the PDF content
        buffer = BytesIO()
        
        # Create a canvas to draw on
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        height = 550
        c.setFont('Helvetica', 10)
        x = 40*0.75
        y = 700

        image_path = os.path.join(current_app.root_path, 'static', 'images', 'sda_logo.jpg')
        c.setFillColor('#EC7C30')
        c.rect(255, 752, 330, 15, fill=True, stroke=False)
        c.setFillColor('#EC7C30')
        c.rect(255, 700, 330, 15, fill=True, stroke=False)
        c.drawImage(image_path, x, y, width=280*0.75, height=90*0.75)
        c.setFillColor('#39383D')
        c.rect(255, 715, 330, 37, fill=True, stroke=False)
        c.setFillColor('white')
        c.drawString(375, 755, 'PNGUM IT Department')
        c.drawString(258, 740, 'P. O. BOX 86, LAE 411, MP')
        c.drawString(258, 730, 'Papua New Guinea')
        c.drawString(258, 720, 'Memorial Avenue')
        c.drawString(255, 705, 'Coronation Drive, Memorial Drive, Lae, Papua New Guinea Union Mission')
        c.drawString(395, 740, 'Phone: 675 - 472 1488')
        c.drawString(395, 730, 'Fax: 675 - 472 1873')
        c.drawString(395, 720, 'Email: pngumitorders@adventist.org.pg')

        c.setFont('Helvetica', 12)
        c.setFillColor('black')
        c.drawString(40*0.75, 670, 'Bill To:')
        c.drawString(260, 670, 'QUOTE NO:')
        c.drawString(260, 650, 'Date: '+session['dateToday'])
        c.drawString(40, 560, 'Mission Contact: '+session['missContact'].title())
        c.drawString(40, 540, 'IT Contact: '+session['it'])
        c.setFillColor('red')
        c.drawString(350, 670, session['inv'])

        text_box_width = 200
        text_box_height = 70
        font_color='black'
        font_size = 12
        # Sample text to draw
        text = session['add']

        c.setFillColor('#e0e0eb')
        c.rect(40, 490, 532, 25, fill=True, stroke=False)


        # Draw a rectangle to serve as the text box background
        c.rect(40*0.75, 590, text_box_width, text_box_height)

        text_object = c.beginText(42, 590 + text_box_height - 40)
        text_object.setFont("Helvetica", font_size)
        text_object.setFillColor(font_color)

        # Split the text into words
        words = text.split()

        # Loop through the words and add them to the text object while wrapping the lines
        line = ""
        for word in words:
            if text_object.getX() + c.stringWidth(line + word) <= 40*0.75 + text_box_width:
                # Add the word to the current line
                line += word + " "
            else:
                # Move to the next line and start a new line
                text_object.textLine(line)
                line = word + " "

        # Add the last line to the text object
        text_object.textLine(line)

        # Draw the text object on the canvas
        c.drawText(text_object)
        c.drawString(42, 640, session['bill']+' - '+session['dept'] )

        c.line(40, 515, 572, 515)

        #Format list for table data
        data = [['Quantity', 'Item Code','Description', 'Unit Price', 'Total Price']]
        for index, item in enumerate(session['dlist']):
            item_code=item['itemCode']
            description = item['description'].title()
            price = 'PGK '+item['price']
            quantity = item['quantity']
            total_price = 'PGK '+session['totalprice'][index] if index < len(session['totalprice']) else ""
            data.append([quantity,item_code, description, price, total_price])

        # Set font size and leading for the table
        font_size = 10
        leading = 20

        # Define the position of the top-left corner of the table
        x = 40
        y = 500

        # Define the cell widths for each column
        column_widths = [60, 60, 230, 90, 90]

        # Draw the table headers
        c.setFont("Helvetica-Bold", font_size)
        for i, header in enumerate(data[0]):
            c.drawString(x + sum(column_widths[:i]), y-2, header)

        # Draw the table data
        c.setFont("Helvetica", font_size)
        for i, row in enumerate(data[1:], start=1):
            for j, cell in enumerate(row):
                c.drawString(x + sum(column_widths[:j]), y - (i * leading)-5, cell)

                if i == len(data) - 1 and j == len(row)-2:
                    c.drawString(x + sum(column_widths[:j]), y - (i * leading)-30, "Total Cost:")
                    c.line(x + sum(column_widths[:j]), y - (i * leading)-35, 570, y - (i * leading)-35)
                elif i == len(data) - 1 and j == len(row)-1:
                    c.drawString(x + sum(column_widths[:j]), y - (i * leading)-30, 'PGK '+session['totalcost'])
                else:
                    pass
                
        #Draw the horizontal lines for the table
        c.setStrokeColor('#e0e0eb')
        for i in range(len(data)):
            c.line(x, y - (i * leading)-10, x + sum(column_widths), y - (i * leading)-10)

        # Draw the vertical lines for the table
        #for i, width in enumerate(column_widths, start=1):
            #c.line(x + sum(column_widths[:i]), y+10, x + sum(column_widths[:i]), (y - (len(data) * leading))+12)

        c.setFillColor('black')
        c.rect(40*0.75, 125, 80, 25)
        c.rect(40*0.75, 85, 80, 40)
        c.rect(40*0.75, 40*0.75, 80, 55)
        c.rect(110, 125, 315, 25)
        c.rect(110, 85, 315, 40)
        c.rect(110, 65, 315, 20)
        c.rect(110, 45, 315, 20)
        c.rect(110, 40*0.75, 315, 55)
        c.setFillColor('#FCFCCC')
        c.rect(450, 40*0.75, 132, 120, fill=True, stroke=False)

        #Create a text object to wrap comment text in box
        max_width=330
        c.setFillColor('black')
        text_object=c.beginText(120, 110)
        words=session['comments'].split()
        line=""

        for word in words:
            if c.stringWidth(line+word)<=max_width:
                line+=word+" "
            else:
                text_object.textLine(line)
                line= word + " "

        text_object.textLine(line)
        c.drawText(text_object)
        c.setFontSize(12)
        c.drawString( 40, 135, "Payment")
        c.drawString( 40, 110, "Comments:")
        c.drawString( 40, 65, "A/C Name:")
        c.drawString(120, 70, "Westpac Lae - PNGUM of SDA Account # 2700-839-001")
        c.drawString(120, 50, "BSP – PNGUM of SDA Account # 1000-981-825")

        c.drawString( 460, 130, "Office Use Only")


        # Save the canvas contents
        c.save()
        # Reset the buffer position to the beginning
        buffer.seek(0)

        # Create a Flask Response with the PDF content
        response = Response(buffer, content_type='application/pdf')
        response.headers['Content-Disposition'] = f'attachment; filename={filename}.pdf'
        
        return response


@routeGeneratePDF_bp.route('/amend-remove-item', methods=['POST'])
@login_required
def amend_remove_item():
    qItemID=request.form.get('id')
    data_fetcher=DataFetcher(current_app.config['database'])
    qNo=data_fetcher.fetch_row(getQNumber, (qItemID,))
    data_fetcher.delete_data(delete_qEntry, (qItemID,))
    totalCost(qNo[0])
    message="success"
    return jsonify(response=message)

@routeGeneratePDF_bp.route('/amend-add-item', methods=['POST'])
@login_required
def amend_add_item():
    quotationNumber = request.form['quoteToEdit2']
    itemCode = request.form['selectDropdown']
    price = request.form['priceField']
    quantity = request.form['quantity']
    itemTotal = float(price) * float(quantity)
    data = (quotationNumber, itemCode, quantity, price, itemTotal)
    db_conn = current_app.config['database']
    data_fetcher=DataFetcher(db_conn)
    data_fetcher.insert_data(insertQuoteDetails, data)
    totalCost(quotationNumber)
    return "success"


@routeGeneratePDF_bp.route('/edit-comment', methods=['POST'])
@login_required
def edit_comment():
    comment = request.form['quotationComments']
    quote = request.form['quoteToEdit']
    data = (comment, quote)
    db_conn = current_app.config['database']
    data_fetcher = DataFetcher(database=db_conn)
    data_fetcher.update_data(updateComment, data)
    return "success"