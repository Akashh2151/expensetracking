# import datetime
from bson import ObjectId
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import re
import pymongo
import stripe

from datetime import datetime,timedelta



app = Flask(__name__, static_url_path="", static_folder="templates")
stripe.api_key = "sk_test_51NbMLVSG44qBbRcphKhLEwUjHNMODNzZhTOOGVcD5MvOb0doqjqoTBnldg5qLzBcUp5xb6M3WsKtMaKz2MR028q100aTjHUgHP"
YOUR_DOMAIN = "http://localhost:5000"
app = Flask(__name__,template_folder="templates")

app.secret_key = 'a'
  
# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['ExpenseDB']  # Replace with your MongoDB database name

# Define MongoDB collections for your data
register_collection = db['register']
expenses_collection = db['expenses']
limits_collection = db['limits']

# mysql = MySQL(app)

# Custom Jinja2 filter to format datetime
@app.template_filter('strftime')
def _jinja2_filter_datetime(dt, fmt=None):
    if dt is None:
        return ''
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'  # Default format
    return dt.strftime(fmt)

 
#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")


@app.route("/")
def add():
    return render_template("home.html")



@app.route('/plan', methods=['GET', 'POST'])
def plan():
    # Your handling code here
    return render_template('plan.html')

 



@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username already exists in MongoDB
        existing_account = register_collection.find_one({'username': username})
        if existing_account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Name must contain only characters and numbers!'
        else:
            # Create a new document for registration in MongoDB
            new_account = {
                'username': username,
                'email': email,
                'password': password
            }
            register_collection.insert_one(new_account)
            msg = 'You have successfully registered!'
            return render_template('signup.html', msg=msg)

    return render_template('signup.html', msg=msg)       
        
 
        
 #LOGIN--PAGE
    
@app.route("/signin")
def signin():
    return render_template("login.html")
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user document by username and password in MongoDB
        user = register_collection.find_one({'username': username, 'password': password})
        
        if user:
            session['loggedin'] = True
            session['id'] = str(user['_id'])  # Assuming '_id' is the unique identifier in MongoDB
            session['username'] = user['username']
            return redirect('/home')
        else:
            msg = 'Incorrect username / password!'

    return render_template('login.html', msg=msg)


       





#ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense', methods=['POST'])
def addexpense():
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']

    # Create a new expense document in MongoDB
    expenses_collection.insert_one({
        'userid': session['id'],
        'date': date,
        'expensename': expensename,
        'amount': amount,
        'paymode': paymode,
        'category': category
    })

    return redirect("/display")


@app.route("/display")
def display():
    if 'username' not in session or 'id' not in session:
        return redirect('/login')  # Redirect to login if user is not logged in

    user_id = session['id']

    expenses = expenses_collection.find({'userid': user_id}).sort('date', -1)
    # Sort by date in descending order (latest expenses first)

    return render_template('display.html', expense=expenses)






@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete(id):
    if 'username' not in session or 'id' not in session:
        return redirect('/login')  # Redirect to login if user is not logged in

    if request.method == 'POST':
        try:
            object_id = ObjectId(id)  # Convert id to ObjectId
            result = expenses_collection.delete_one({'_id': object_id, 'userid': session['id']})

            if result.deleted_count > 0:
                print('Deleted successfully')
            else:
                print('Expense not found or not authorized to delete')

        except Exception as e:
            print('Error:', str(e))
            return "Error occurred while deleting the expense"

    return redirect("/display")

# ... (other routes) ...


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if 'username' not in session or 'id' not in session:
        return redirect('/login')  # Redirect to login if the user is not logged in

    user_id = session['id']

    try:
        # Find the expense document by ID and user ID
        expense = expenses_collection.find_one({'_id': ObjectId(id), 'userid': user_id})

        if expense:
            if request.method == 'GET':
                return render_template('edit.html', expense=expense)
            elif request.method == 'POST':
                # Handle the POST request to update the expense
                date_str = request.form['date']
                expensename = request.form['expensename']
                amount = float(request.form['amount'])
                paymode = request.form['paymode']
                category = request.form['category']

                # Convert the date string to a datetime object
                date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

                # Update the expense document in MongoDB
                result = expenses_collection.update_one(
                    {'_id': ObjectId(id), 'userid': user_id},
                    {
                        '$set': {
                            'date': date_obj,
                            'expensename': expensename,
                            'amount': amount,
                            'paymode': paymode,
                            'category': category
                        }
                    }
                )

                if result.modified_count > 0:
                    print('Expense updated successfully')
                    return redirect('/display')
                else:
                    print('Expense not found or not authorized to edit')
                    return "Expense not found or not authorized to edit", 404
        else:
            return "Expense not found", 404
    except Exception as e:
        print('Error fetching or updating expense:', str(e))
        return "Error occurred while fetching or updating the expense"



@app.route('/update/<id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        paymode = request.form['paymode']
        category = request.form['category']

        # Create a dictionary with the updated data
        updated_data = {
            'date': date,
            'expensename': expensename,
            'amount': amount,
            'paymode': paymode,
            'category': category
        }

        # Update the expense document in MongoDB
        expenses_collection.update_one({'_id': ObjectId(id)}, {'$set': updated_data})

        print('Successfully updated')
        return redirect("/display")
      

          
           
           
        
@app.route('/limit', methods=['GET'])
def limit():
    if 'username' not in session or 'id' not in session:
        return redirect('/login')  # Redirect to login if the user is not logged in

    return render_template('limit.html')

@app.route("/limitn")
def limitn():
    if 'username' not in session or 'id' not in session:
        return redirect('/login')  # Redirect to login if the user is not logged in

    current_limit = get_user_monthly_limit(session['id'])
    return render_template("limit.html", y=current_limit)

            
        
@app.route("/limitnum", methods=['POST'])
def limitnum():
    if 'username' not in session or 'id' not in session:
        return redirect('/login')  # Redirect to login if the user is not logged in

    if request.method == "POST":
        number_str = request.form['number']
        
        try:
            number = float(number_str)
        except ValueError:
            return "Invalid monthly limit. Please enter a valid number.", 400
        
        # Insert or update the monthly limit in the 'limits' collection
        limits_collection.update_one(
            {'userid': session['id']},
            {'$set': {'limitss': number}},
            upsert=True
        )
        
        # Check if the user has exceeded the monthly limit
        total_expenses = get_total_monthly_expenses(session['id'])
        
        if total_expenses is None:
            total_expenses = 0.0
        else:
            total_expenses = float(total_expenses)
        
        if total_expenses > number:
            return "You have exceeded your monthly limit."
        
        return redirect('/limitn')




        
        
        

def get_user_monthly_limit(user_id):
    limit_doc = limits_collection.find_one({'userid': user_id}, sort=[("_id", -1)])
    return limit_doc['limitss'] if limit_doc else 0

def get_total_monthly_expenses(user_id):
    # Calculate the total expenses for the current month
    # You should adjust this query to match your database structure
    total_expenses = expenses_collection.aggregate([
        {
            '$match': {
                'userid': user_id,
                'date': {
                    '$gte': datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                    '$lt': datetime.now().replace(day=1, month=datetime.now().month + 1, hour=0, minute=0, second=0, microsecond=0),
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$amount'}
            }
        }
    ])

    return total_expenses.next()['total'] if total_expenses.alive else 0







# REPORTS
@app.route("/today")
def today():
    user_id = session['id']
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Convert today to a string in the same format as your date strings in MongoDB
    today_str = today.strftime('%Y-%m-%dT%H:%M')

    # Calculate the next day to compare with
    next_day = today + timedelta(days=1)
    next_day_str = next_day.strftime('%Y-%m-%dT%H:%M')

    # Fetch expenses for the current day
    expense_cursor = expenses_collection.find({
        'userid': user_id,
        'date': {'$gte': today_str, '$lt': next_day_str}
    }).sort('date', pymongo.DESCENDING)

    total = 0
    category_totals = {}

    for x in expense_cursor:
        total += float(x['amount'])  # Convert the 'amount' to a float for addition
        category = x['category']
        category_totals[category] = category_totals.get(category, 0) + float(x['amount'])

    return render_template("today.html", expenses=expense_cursor, total=total, category_totals=category_totals)




@app.route("/month")
def month():
    user_id = session['id']
    
    # Get the first day of the current month
    today = datetime.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Convert the first day of the month to a string
    first_day_str = first_day_of_month.strftime('%Y-%m-%dT%H:%M')

    # Calculate the first day of the next month to use as the upper limit
    next_month = today.replace(month=today.month + 1, day=1)
    first_day_of_next_month = next_month.replace(hour=0, minute=0, second=0, microsecond=0)
    first_day_of_next_month_str = first_day_of_next_month.strftime('%Y-%m-%dT%H:%M')

    # Fetch expenses for the current month
    expense_cursor = expenses_collection.find({
        'userid': user_id,
        'date': {'$gte': first_day_str, '$lt': first_day_of_next_month_str}
    }).sort('date', pymongo.DESCENDING)

    total = 0
    category_totals = {}

    for x in expense_cursor:
        total += float(x['amount'])  # Convert the 'amount' to a float for addition
        category = x['category']
        category_totals[category] = category_totals.get(category, 0) + float(x['amount'])

    return render_template("month.html", expenses=expense_cursor, total=total, category_totals=category_totals)


         
@app.route("/year")
def year():
    user_id = session['id']
    
    # Get the first day of the current year
    today = datetime.now()
    first_day_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Convert the first day of the year to a string
    first_day_str = first_day_of_year.strftime('%Y-%m-%dT%H:%M')

    # Calculate the first day of the next year to use as the upper limit
    next_year = today.replace(year=today.year + 1, month=1, day=1)
    first_day_of_next_year = next_year.replace(hour=0, minute=0, second=0, microsecond=0)
    first_day_of_next_year_str = first_day_of_next_year.strftime('%Y-%m-%dT%H:%M')

    # Fetch expenses for the current year
    expense_cursor = expenses_collection.find({
        'userid': user_id,
        'date': {'$gte': first_day_str, '$lt': first_day_of_next_year_str}
    }).sort('date', pymongo.DESCENDING)

    total = 0
    category_totals = {}

    for x in expense_cursor:
        total += float(x['amount'])  # Convert the 'amount' to a float for addition
        category = x['category']
        category_totals[category] = category_totals.get(category, 0) + float(x['amount'])

    return render_template("year.html", expenses=expense_cursor, total=total, category_totals=category_totals)


#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')



# return success.html page for nikita
@app.route('/success.html')
def success():
    return render_template('success.html')

# return cancel.html page  for nikita
@app.route('/cancel.html')
def cancel():
    return render_template('cancel.html')

# paymentgetway itergrastion for nikita
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1Nko6SSG44qBbRcpLDlSieCb',
                    'quantity': 1
                }
            ],
            mode="subscription",
   
            success_url = YOUR_DOMAIN + "/success.html",
            cancel_url = YOUR_DOMAIN + "/cancel.html"

        )

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

        

if __name__ == "__main__":
    app.run(debug=True)