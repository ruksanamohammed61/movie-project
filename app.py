# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'testkey' 

@app.context_processor
def inject_now():
    return {'datetime': datetime}

# --- Temporary In-Memory Storage (for local development only) --- [1]
users = [] 
bookings = [] 
booking_counter = 1 

def is_logged_in():
    return 'user_id' in session

# --- Routes (Functions linked to URLs) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        for user in users:
            if user['email'] == email:
                flash('Email already registered. Please log in or use a different email.', 'error')
                return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password)
        new_user_id = len(users) + 1
        
        users.append({
            'id': new_user_id,
            'name': full_name,
            'email': email,
            'password': hashed_password 
        })
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login')) 
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_found = None
        for user in users:
            if user['email'] == email:
                user_found = user
                break
        
        if user_found and check_password_hash(user_found['password'], password):
            session['user_id'] = user_found['id']
            session['user_name'] = user_found['name']
            session['user_email'] = user_found['email']
            flash(f'Welcome back, {user_found["name"]}!', 'success')
            return redirect(url_for('home1')) 
        else:
            flash('Invalid email or password. Please try again.', 'error') 
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out.', 'info') 
    return redirect(url_for('index')) 

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

@app.route('/search_results', methods=['GET'])
def search_results():
    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))
        
    query = request.args.get('query', '').strip() # .strip() to remove leading/trailing whitespace
    language = request.args.get('language', '').strip()
    city = request.args.get('city', '').strip()

    # --- Start of FIXES for search_results ---

    # 1. Ensure all_movies uses static image paths or placeholder if no image exists
    all_movies = [
        {"title": "Pushpa: The Rise", "genre": "Action, Drama", "price": 190, "image": url_for('static', filename='images/pushpa.jpg'), "language": "Telugu"},
        {"title": "RRR", "genre": "Action, Historical", "price": 220, "image": url_for('static', filename='images/rrr.jpg'), "language": "Telugu"},
        {"title": "Baahubali 2: The Conclusion", "genre": "Action, Fantasy", "price": 220, "image": url_for('static', filename='images/baahubali2.jpg'), "language": "Telugu"},
        {"title": "Sita Ramam", "genre": "Romance, Drama", "price": 190, "image": url_for('static', filename='images/sitaramam.jpg'), "language": "Telugu"},
        {"title": "Bimbisara", "genre": "Action, Fantasy", "price": 175, "image": url_for('static', filename='images/bimbisara.jpg'), "language": "Telugu"},
        {"title": "Karthikeya 2", "genre": "Mystery, Thriller", "price": 175, "image": url_for('static', filename='images/karthikeya2.jpg'), "language": "Telugu"},
        {"title": "COURT", "genre": "Action, Drama", "image": url_for('static', filename='images/court.jpg')},
        {"title": "MAD", "genre": "Action, Historical", "image": url_for('static', filename='images/mad.jpg')},
        {"title": "ROBINHOOD", "genre": "Action, Thriller", "image": url_for('static', filename='images/robinhood.jpg')},
        {"title": "PRESENCE", "genre": "Action, Drama", "image": url_for('static', filename='images/presence.jpg')},
    ]

    # 2. Refine filtering logic for clarity and accuracy
    # Start with all movies and filter them down
    filtered_movies = all_movies 

    # If any search criteria are provided, apply filters
    if query or language or city:
        # Filter by title if query is present
        if query:
            filtered_movies = [movie for movie in filtered_movies if query.lower() in movie['title'].lower()]
        
        # Filter by language if language is selected
        if language:
            filtered_movies = [movie for movie in filtered_movies if language.lower() == movie['language'].lower()]
        
        # Add city filtering if needed later, but it's not in your current movie data
        # if city:
        #     filtered_movies = [movie for movie in filtered_movies if city.lower() in movie.get('city', '').lower()]
    
    # --- End of FIXES for search_results ---
    
    return render_template('search_results.html', movies=filtered_movies, query=query, language=language, city=city)

@app.route('/b1/<movie_title>/<theater_name>/<price>', methods=['GET'])
def b1(movie_title, theater_name, price):
    if not is_logged_in():
        flash('Please log in to book tickets.', 'warning')
        return redirect(url_for('login'))
        
    movie_details = {
        'title': movie_title.replace('_', ' '),
        'theater': theater_name.replace('_', ' '),
        'price_per_ticket': float(price),
        'location': 'Mirajkar Cinemas, Attapur, Hyderabad', 
        'date_options': ['Mon, Apr 14', 'Tue, Apr 15', 'Wed, Apr 16', 'Thu, Apr 17', 'Fri, Apr 18', 'Sat, Apr 19', 'Sun, Apr 20'],
        'time_options': ['10:00 AM', '12:30 PM', '03:15 PM', '06:00 PM', '09:00 PM'],
        'seats_layout': { 
            'A': [1,2,3,4,5,6,7,8,9,10],
            'B': [1,2,3,4,5,6,7,8,9,10],
            'C': [1,2,3,4,5,6,7,8,9,10],
            'D': [1,2,3,4,5,6,7,8,9,10],
            'E': [1,2,3,4,5,6,7,8,9,10]
        }
    }
    return render_template('b1.html', movie=movie_details)

@app.route('/tickets', methods=['POST'])
def tickets_submission():
    global booking_counter
    if not is_logged_in():
        flash('Please log in to complete your booking.', 'warning')
        return redirect(url_for('login'))

    movie_title = request.form['movie_title']
    theater_name = request.form['theater_name']
    selected_date = request.form.get('selected_date') # Use .get() for safety
    selected_time = request.form.get('selected_time') # Use .get() for safety
    selected_seats_str = request.form.get('selected_seats', '')
    selected_seats = json.loads(selected_seats_str) if selected_seats_str else []
    total_amount = float(request.form['total_amount'])
    full_name = request.form['full_name']
    phone_number = request.form['phone_number']
    payment_method = request.form['payment_method']

    # --- Server-side validation for booking ---
    if not selected_date or not selected_time or not selected_seats:
        flash('Please select a date, time, and at least one seat to complete your booking.', 'error')
        # Redirect back to the booking page for the same movie
        return redirect(url_for('b1', 
                                movie_title=movie_title.replace(' ', '_'), 
                                theater_name=theater_name.replace(' ', '_'), 
                                price=str(total_amount/len(selected_seats) if selected_seats else 0))) # Approximate price
    # --- End server-side validation ---

    booking_id = f"MVM-{datetime.now().strftime('%Y%m%d')}-{booking_counter}"
    booking_counter += 1

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

    bookings.append(new_booking)
    flash('Your tickets have been successfully booked! Enjoy the show!', 'success')
    return render_template('tickets.html', booking=new_booking)

@app.route('/about')
def about():
    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('contact_us.html')

if __name__ == '__main__':
    app.run(debug=True)