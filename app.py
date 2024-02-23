from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime 
import mysql.connector
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='template')
app.secret_key = 'your_secret_key' 
CORS(app)

def get_database_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Execute SQL script to create the database and table
def execute_sql_script(file_path, cursor):
    try:
        with open(file_path, 'r') as file:
            sql_script = file.read()
            queries = sql_script.split(';')

            for query in queries:
                if query.strip():
                    cursor.execute(query)

            db_connection.commit()

        print(f"SQL script executed successfully: {file_path}")

    except Exception as e:
        print(f"Error executing SQL script {file_path}: {e}")

# Connect to the database using a context manager
with get_database_connection() as db_connection, db_connection.cursor() as cursor:

    execute_sql_script('/Users/rahuln/S-3/Python/PrimeHotels/website/db.sql', cursor)

@app.route('/')
def main_page():
    # Check if the user is logged in
    if 'user_id' in session:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        return render_template('index.html', username=None)

@app.route('/logout')
def logout():
    # Clear the session data
    session.pop('user_id', None)
    session.pop('username', None)
    
    return redirect(url_for('main_page'))

@app.route('/login.html', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        try:
            admin_username = 'admin'
            admin_password = 'admin123'

            if username == admin_username and password == admin_password:
                print('Admin logged in')
                session['user_id'] = 1  
                session['username'] = admin_username
                return redirect(url_for('admin_page'))
            
            else:
                # Connect to the database within the context manager
                with get_database_connection() as db_connection, db_connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                    user = cursor.fetchone()

                    if user:
                        session['user_id'] = user[0]
                        session['username'] = user[1]

                        redirect_url = request.args.get('redirect_url', '/')
                        return redirect(redirect_url)
                    else:
                        
                        return jsonify({'success': False, 'message': 'Invalid credentials'})
        except mysql.connector.Error as err:
            print(err)
            return jsonify({'success': False, 'message': f'Error during login: {err}'})

    else:
        return render_template('login.html')


# Add a new route for the admin page
@app.route('/admin')
def admin_page():
    if session.get('user_id') is None or session.get('username') != 'admin':
        return redirect(url_for('login'))

    username = session['username']
    return render_template('admin.html', username=username)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Connect to the database within the context manager
            with get_database_connection() as db_connection, db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    return jsonify({'success': False, 'message': 'Username or email already exists'})
                else:
                    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                                   (username, email, password))
                    db_connection.commit()

                    session['user_id'] = cursor.lastrowid
                    session['username'] = username

                    return redirect(url_for('login'))

        except mysql.connector.Error as err:
            print(err)
            return jsonify({'success': False, 'message': f'Error during signup: {err}'})

    return render_template('signup.html')

@app.route('/page1')
def page1():
    
    if 'user_id' in session:
        username = session['username']
        return render_template('page1.html', username=username)
    else:
        return redirect('/login')

@app.route('/booking.html')
def customer():
    if 'user_id' in session:
        return render_template('booking.html')
    else:
        return redirect(url_for('login'))

@app.route('/submit_reservation', methods=['POST', 'GET'])
def submit_reservation():
    if request.method == 'POST':
        # Get user_id from the session
        if 'user_id' in session:
            user_id = session['user_id']
        else:
            return jsonify({'success': False, 'message': 'User not logged in'})

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        troom = request.form.get('troom')
        bed = request.form.get('bed')

        nroom = int(request.form.get('nroom'))
        cin = datetime.strptime(request.form.get('cin'), '%Y-%m-%dT%H:%M')
        cout = datetime.strptime(request.form.get('cout'), '%Y-%m-%dT%H:%M')

        try:
            with get_database_connection() as db_connection, db_connection.cursor() as cursor:
                room_price = get_room_price(troom)
                total_cost = nroom * room_price 

                cursor.execute("""
                    INSERT INTO Booking (UserID, FirstName, LastName, Email, Phone, RoomType, BeddingType, NumberOfRooms, CheckInDate, CheckOutDate, TotalCost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, fname, lname, email, phone, troom, bed, nroom, cin, cout, total_cost))

                booking_id = cursor.lastrowid

                db_connection.commit()
                session['booking_id'] = booking_id

                return render_template('transaction.html', success=True, message='Reservation successful', total_cost=total_cost)
        except mysql.connector.Error as err:
            print(err)
            return jsonify({'success': False, 'message': f'Error during reservation: {err}'})

    return render_template('booking.html')


def get_room_price(room_type):
    room_prices = {'Superior Room': 320, 'Deluxe Room': 220, 'Guest House': 180, 'Single Room': 150}
    return room_prices.get(room_type, 0)  




@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    if request.method == 'POST':
        # Logic to get the user_id and booking_id from the session
        if 'user_id' in session and 'booking_id' in session:
            user_id = session['user_id']
            booking_id = session['booking_id']
        else:
            return jsonify({'success': False, 'message': 'User not logged in or no booking ID in session'})

        cursor = None 

        try:
            with get_database_connection() as db_connection:
                cursor = db_connection.cursor()

                # Fetch the total cost from the Booking table based on booking_id
                cursor.execute("SELECT TotalCost FROM Booking WHERE BookingID = %s", (booking_id,))
                total_cost_row = cursor.fetchone()

                if total_cost_row is not None:
                    total_cost = total_cost_row[0]

                    amount = total_cost  # Use the total_cost as the amount for payment
                    person_name = request.form.get('person_name')
                    card_number = request.form.get('card_number')
                    expiry_date = request.form.get('expiry_date')
                    cvv = request.form.get('cvv')

                    try:
                        # Insert the payment details into the Transaction table with the same user_id and booking_id
                        cursor.execute("""
                            INSERT INTO Transaction (UserID, BookingID, Amount, CardNumber, ExpiryDate, CVV)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (user_id, booking_id, amount, card_number, expiry_date, cvv))

                        db_connection.commit()

                        # Redirect to a success page using the PRG pattern
                        return redirect(url_for('payment_success'))
                    except mysql.connector.Error as err:
                        print(err)
                        return jsonify({'success': False, 'message': f'Error during payment: {err}'})
                else:
                    return jsonify({'success': False, 'message': 'TotalCost not found for BookingID'})
        except mysql.connector.Error as err:
            print(err)
            return jsonify({'success': False, 'message': f'Error: {err}'})
        finally:
            if cursor:
                cursor.close()
                
# Route for displaying payment success page
@app.route('/payment_success')
def payment_success():
    return render_template('userprofile.html')


@app.route('/userprofile.html')
def userprofile():
    # Check if the user is logged in
    if 'user_id' in session:
        return render_template('userprofile.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/api/user/details')
def get_user_details():
    if 'user_id' in session:
        user_id = session['user_id']
        with get_database_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
            user_details = cursor.fetchall()
            return jsonify(user_details)
    else:
        return jsonify([])

@app.route('/api/user/booking-details')
def get_booking_details():
    if 'user_id' in session:
        user_id = session['user_id']
        with get_database_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT BookingID, UserID, FirstName, LastName, Email, Phone, RoomType, BeddingType, NumberOfRooms, 
                       CheckInDate, CheckOutDate, TotalCost
                FROM Booking
                WHERE UserID = %s
            """, (user_id,))
            booking_details = cursor.fetchall()
            return jsonify(booking_details)
    else:
        return jsonify([])

@app.route('/api/user/transaction-details')
def get_transaction_details():
    if 'user_id' in session:
        user_id = session['user_id']
        with get_database_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT TransactionID, UserID, Amount, CardNumber, ExpiryDate, CVV
                FROM Transaction
                WHERE UserID = %s
            """, (user_id,))
            transaction_details = cursor.fetchall()
            return jsonify(transaction_details)
    else:
        
        return jsonify([])
    

@app.route('/api/user/all-users')
def get_all_users():
    if 'user_id' in session:
        with get_database_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("SELECT id, username, email FROM users")
            user_details = cursor.fetchall()
            return jsonify(user_details)
    else:
        return jsonify([])
    
    
@app.route('/api/user/all-bookings')
def get_all_bookings():
    with get_database_connection() as db_connection:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT BookingID, UserID, FirstName, LastName, Email, Phone, RoomType, BeddingType, NumberOfRooms, 
                   CheckInDate, CheckOutDate, TotalCost
            FROM Booking
        """)
        booking_details = cursor.fetchall()
        return jsonify(booking_details)

@app.route('/api/user/all-transactions')
def get_all_transactions():
    with get_database_connection() as db_connection:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT *
            FROM Transaction 
        """)
        transaction_details = cursor.fetchall()
        return jsonify(transaction_details)



@app.route('/api/user/change-password', methods=['POST'])
def change_password():
    if 'user_id' in session:
        user_id = session['user_id']

        # Use request.get_json() to retrieve JSON data
        data = request.get_json()

        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        with get_database_connection() as db_connection:
            cursor = db_connection.cursor()

            # Fetch the hashed old password from the database
            cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            stored_password_hash = cursor.fetchone()

            # Check if the old password matches the one in the database
            if stored_password_hash and check_password_hash(stored_password_hash[0], old_password):
                # Update the password in the database
                hashed_new_password = generate_password_hash(new_password, method='sha256')
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_password, user_id))
                db_connection.commit()

                return jsonify({"message": "Password changed successfully"})
            else:
                return jsonify({"error": "Invalid old password"}), 400
    else:
        return jsonify({"error": "User not authenticated"}), 401


    
if __name__ == '__main__':
    app.run(debug=True, port=5500)
