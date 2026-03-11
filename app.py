from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import boto3
from boto3.dynamodb.conditions import Attr

app = Flask(__name__)
app.secret_key = 'testkey'

@app.context_processor
def inject_now():
    return {'datetime': datetime}

# ---------- AWS DynamoDB Connection ----------
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

users_table = dynamodb.Table('users')
bookings_table = dynamodb.Table('bookings')

# ---------- Helper ----------
def is_logged_in():
    return 'user_id' in session


# ---------- Routes ----------

@app.route('/')
def index():
    return render_template('index.html')


# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        # Check if email exists
        response = users_table.scan(
            FilterExpression=Attr('email').eq(email)
        )

        if response['Items']:
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        user_id = int(datetime.now().timestamp())

        users_table.put_item(
            Item={
                'id': user_id,
                'name': full_name,
                'email': email,
                'password': hashed_password
            }
        )

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        response = users_table.scan(
            FilterExpression=Attr('email').eq(email)
        )

        if response['Items']:

            user = response['Items'][0]

            if check_password_hash(user['password'], password):

                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']

                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('home1'))

        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():

    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ---------- HOME ----------
@app.route('/home1')
def home1():

    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))

    trending_movies = [
        {"title": "COURT", "genre": "Action, Drama", "image": url_for('static', filename='images/court.jpg')},
        {"title": "MAD", "genre": "Action, Historical", "image": url_for('static', filename='images/mad.jpg')},
        {"title": "ROBINHOOD", "genre": "Action, Thriller", "image": url_for('static', filename='images/robinhood.jpg')},
        {"title": "PRESENCE", "genre": "Action, Drama", "image": url_for('static', filename='images/presence.jpg')},
    ]

    return render_template('home1.html', movies=trending_movies)


# ---------- SEARCH ----------
@app.route('/search_results', methods=['GET'])
def search_results():

    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip()
    language = request.args.get('language', '').strip()
    city = request.args.get('city', '').strip()

    all_movies = [

        {"title": "Pushpa: The Rise", "genre": "Action, Drama", "price": 190,
         "image": url_for('static', filename='images/pushpa.jpg'), "language": "Telugu"},

        {"title": "RRR", "genre": "Action, Historical", "price": 220,
         "image": url_for('static', filename='images/rrr.jpg'), "language": "Telugu"},

        {"title": "Baahubali 2: The Conclusion", "genre": "Action, Fantasy", "price": 220,
         "image": url_for('static', filename='images/baahubali2.jpg'), "language": "Telugu"},

        {"title": "Sita Ramam", "genre": "Romance, Drama", "price": 190,
         "image": url_for('static', filename='images/sitaramam.jpg'), "language": "Telugu"},

        {"title": "Bimbisara", "genre": "Action, Fantasy", "price": 175,
         "image": url_for('static', filename='images/bimbisara.jpg'), "language": "Telugu"},

        {"title": "Karthikeya 2", "genre": "Mystery, Thriller", "price": 175,
         "image": url_for('static', filename='images/karthikeya2.jpg'), "language": "Telugu"},

        {"title": "COURT", "genre": "Action, Drama",
         "image": url_for('static', filename='images/court.jpg')},

        {"title": "MAD", "genre": "Action, Historical",
         "image": url_for('static', filename='images/mad.jpg')},

        {"title": "ROBINHOOD", "genre": "Action, Thriller",
         "image": url_for('static', filename='images/robinhood.jpg')},

        {"title": "PRESENCE", "genre": "Action, Drama",
         "image": url_for('static', filename='images/presence.jpg')}
    ]

    filtered_movies = all_movies

    if query:
        filtered_movies = [m for m in filtered_movies if query.lower() in m['title'].lower()]

    if language:
        filtered_movies = [m for m in filtered_movies if m.get('language', '').lower() == language.lower()]

    return render_template('search_results.html',
                           movies=filtered_movies,
                           query=query,
                           language=language,
                           city=city)


# ---------- BOOKING PAGE ----------
@app.route('/b1/<movie_title>/<theater_name>/<price>')
def b1(movie_title, theater_name, price):

    if not is_logged_in():
        flash('Please log in to book tickets.', 'warning')
        return redirect(url_for('login'))

    movie_details = {

        'title': movie_title.replace('_', ' '),
        'theater': theater_name.replace('_', ' '),
        'price_per_ticket': float(price),
        'location': 'Mirajkar Cinemas, Attapur, Hyderabad',

        'date_options': [
            'Mon, Apr 14', 'Tue, Apr 15', 'Wed, Apr 16',
            'Thu, Apr 17', 'Fri, Apr 18', 'Sat, Apr 19', 'Sun, Apr 20'
        ],

        'time_options': [
            '10:00 AM', '12:30 PM', '03:15 PM', '06:00 PM', '09:00 PM'
        ],

        'seats_layout': {
            'A': list(range(1,11)),
            'B': list(range(1,11)),
            'C': list(range(1,11)),
            'D': list(range(1,11)),
            'E': list(range(1,11))
        }
    }

    return render_template('b1.html', movie=movie_details)


# ---------- BOOK TICKETS ----------
@app.route('/tickets', methods=['POST'])
def tickets_submission():

    if not is_logged_in():
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    movie_title = request.form['movie_title']
    theater_name = request.form['theater_name']

    selected_date = request.form.get('selected_date')
    selected_time = request.form.get('selected_time')

    seats_json = request.form.get('selected_seats', '')
    selected_seats = json.loads(seats_json) if seats_json else []

    total_amount = float(request.form['total_amount'])

    full_name = request.form['full_name']
    phone_number = request.form['phone_number']
    payment_method = request.form['payment_method']

    if not selected_date or not selected_time or not selected_seats:
        flash('Please select date, time and seats.', 'error')
        return redirect(url_for('home1'))

    booking_id = f"MVM-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    new_booking = {

        'booking_id': booking_id,
        'user_id': session.get('user_id'),
        'user_name': full_name,
        'movie_title': movie_title,
        'theater_name': theater_name,
        'date': selected_date,
        'time': selected_time,
        'seats': selected_seats,
        'amount_paid': total_amount,
        'payment_method': payment_method,
        'booking_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    bookings_table.put_item(Item=new_booking)

    flash('Tickets booked successfully!', 'success')

    return render_template('tickets.html', booking=new_booking)


# ---------- ABOUT ----------
@app.route('/about')
def about():

    if not is_logged_in():
        return redirect(url_for('login'))

    return render_template('about.html')


# ---------- CONTACT ----------
@app.route('/contact_us')
def contact_us():

    if not is_logged_in():
        return redirect(url_for('login'))

    return render_template('contact_us.html')


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)