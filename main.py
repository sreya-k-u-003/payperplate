from flask import Flask, render_template, request, redirect, url_for,jsonify
import mysql.connector

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
def get_db_connection():

    try:
        connection = mysql.connector.connect(host='localhost', port='5048', user='root', password='',
                                             database='pay_per_plate')

        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route('/', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #print(type(username))
        #print(username)
        connection = get_db_connection()

        if connection:

            cur = connection.cursor()


            try:
                # Check if the user exists
                cur.execute('SELECT * FROM users WHERE uid = %s', (username,))
                data = cur.fetchone()
                #print(data)


                if data==None:

                    amount = 500  # Assuming an initial wallet balance
                    cur.execute("INSERT INTO users (uid, password) VALUES (%s, %s)",
                                (username, password))
                    connection.commit()
                    cur.execute("INSERT INTO wallet (uid, balance) VALUES (%s, %s)",
                                (username, amount))
                    connection.commit()

                    cur.close()
                    connection.close()

                # Move the users function call outside the try block
                    users(username)
                    #print('success')

                elif username==data[0] and password!=data[1]:
                    #print("success")

                    return render_template('login.html')

                # Redirect to the home page after successful login or signup
                return redirect(url_for('home', username=username))

            except mysql.connector.Error as err:
                print(err)

    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    username=request.args.get('username')


    return render_template('home.html', username=username)

@app.route('/history', methods=['GET'])
def history():
    username = request.args.get('username')
    connection = get_db_connection()

    if connection:
        cur = connection.cursor()


        # Fetch selected items from the 'history' table (replace 'history' with your actual history table name)
        cur.execute("SELECT Date,item_name  FROM {}".format(username))
        selected_items = cur.fetchall()
        cur.close()
        connection.close()

        return render_template('order.html', username=username, selected_items=selected_items)

@app.route('/food', methods=['GET', 'POST'])
def food():

    connection = get_db_connection()

    if connection:
        cur = connection.cursor()

        if request.method == 'GET':
            cur=connection.cursor()
            cur.execute("SELECT item_id, name,price FROM menu")
            menu_items = cur.fetchall()
            username = request.args.get('username')
            cur.execute('SELECT balance FROM wallet WHERE uid = %s', (username,))

            balance = cur.fetchone()

            cur.close()
            connection.close()

            return render_template('food.html', menu_items=menu_items, username=username, balance=balance)
        elif request.method == 'POST':
            try:
                data = request.json

                # Get data from the JSON body
                total_amount = data.get('totalAmount')
                username = data.get('username')
                selected_dishes = data.get('selected_dishes')

                connection = get_db_connection()

                if connection:
                    cur = connection.cursor()

                # Assuming you have a database connection named `conn`
                    with connection.cursor() as cur:
                        for dish in selected_dishes:
                            item_id = dish.get('item_id')
                            item_name = dish.get('item_name')
                            price = dish.get('price')

                            # Insert selected item into the database
                            cur.execute(
                                "INSERT INTO {} (item_id, item_name, Date, amount) VALUES (%s, %s, CURDATE(), %s)".format(username),
                                (item_id, item_name, price)
                            )
                    #print('sucess')

                    # Commit the changes
                    connection.commit()

                    cur.close()
                    connection.close()

                return jsonify(success=True, message="Order saved successfully")

            except Exception as e:
                return jsonify(success=False, message=str(e))




def users(name):
    try:
        connection = get_db_connection()

        if connection:
            cur = connection.cursor()

            #print('Inside users function')
            cur.execute('SHOW TABLES')
            tables_data =cur.fetchall()
            #print(tables_data)

            table_exists = any(name in i[0] for i in tables_data)

            if not table_exists:
                cur.execute('CREATE TABLE {} (item_id int, item_name VARCHAR(20), Date DATE, amount INT)'.format(name))
                connection.commit()

                cur.close()
                connection.close()
                return 'success'
            else:
                cur.close()
                connection.close()
                return 'Already present'

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return str(err)

#works
@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        data = request.json

        # Get data from the JSON body
        total_amount = data.get('totalAmount')
        username = data.get('username')
        connection = get_db_connection()

        if connection:
            cur = connection.cursor()

            # Update the wallet table with the new balance
            # Assuming you have a 'wallet' table with 'username' and 'balance' columns
            update_query = "UPDATE wallet SET balance = balance - %s WHERE uid = %s"
            cur.execute(update_query, (total_amount, username))
            connection.commit()

            cur.close()
            connection.close()

            # You can perform additional actions here (e.g., updating transaction history)

            return jsonify({'success': True})

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Error processing payment'})



@app.route('/wallet_amount', methods=['GET'])
def wallet_amount():
    try:
        connection = get_db_connection()
        if connection:
            cur = connection.cursor()

            cur = connection.cursor()
            username = request.args.get('username')
            cur.execute('SELECT balance FROM wallet WHERE uid = %s', (username,))

            balance = cur.fetchone()

            cur.close()
            connection.close()


        return render_template('wallet.html', username=username, balance=balance)

    except Exception as e:
        return str(e)
@app.route('/logout')
def logout():
    # Your logout logic here
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)
