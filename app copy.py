# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json # Used for debugging/viewing data in JSON format [1]

app = Flask(__name__)
app.secret_key = 'testkey' 
# IMPORTANT: Change this to a strong, random key in production [1]

@app.context_processor
def inject_now():
    """
    Makes the datetime module available in all templates as 'datetime'.
    This resolves the 'datetime' is undefined error in base.html.
    """
    return {'datetime': datetime}

# --- Temporary In-Memory Storage (for local development only) --- [1]
# This data will reset every time you restart the app.
users = [] # List to store registered user dictionaries [1]
bookings = [] # List to store all ticket bookings [1]
booking_counter = 1 # A simple ID counter for bookings [1]

# --- Helper function to check if user is logged in ---
def is_logged_in():
    return 'user_id' in session

# --- Routes (Functions linked to URLs) ---

@app.route('/')
def index():
    """
    Handles the landing page.
    Renders index.html, which is the initial page with 'YOUR CINEMA EXPERIENCE'.
    """
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles user registration.
    GET: Displays the signup form (register.html).
    POST: Processes the registration form submission [1].
    """
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists [1]
        for user in users:
            if user['email'] == email:
                flash('Email already registered. Please log in or use a different email.', 'error')
                return redirect(url_for('signup'))

        # Hash the password for security [1]
        hashed_password = generate_password_hash(password)

        # Generate a simple ID for the new user (for temporary storage)
        new_user_id = len(users) + 1
        
        # Store user details in the temporary 'users' list [1]
        users.append({
            'id': new_user_id,
            'name': full_name,
            'email': email,
            'password': hashed_password # Storing hashed password [1]
        })
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login')) # Redirect to login after successful registration [1]
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    GET: Displays the login form (login.html) [1].
    POST: Validates user credentials [1].
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_found = None
        for user in users:
            if user['email'] == email:
                user_found = user
                break
        
        # Check if the email exists and password is correct [1]
        if user_found and check_password_hash(user_found['password'], password):
            # Save user info in session [1]
            session['user_id'] = user_found['id']
            session['user_name'] = user_found['name']
            session['user_email'] = user_found['email']
            flash(f'Welcome back, {user_found["name"]}!', 'success')
            return redirect(url_for('home1')) # Redirect to home after login
        else:
            flash('Invalid email or password. Please try again.', 'error') # Flash an "Invalid" message [1]
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Logs out the user by removing their session data [1].
    """
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out.', 'info') # Flash a message [1]
    return redirect(url_for('index')) # Redirect to homepage [1]

@app.route('/home1')
def home1():
    """
    Displays the main home page after a user logs in [1].
    Requires user to be logged in.
    """
    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login')) # Redirect to login if not logged in [1]
    
    # Placeholder for movies (in a real app, this would come from a database)
    trending_movies = [
       {"title": "COURT", "genre": "Action, Drama", "image": url_for('static', filename='images/court.jpg')}, # CORRECTED
        {"title": "MAD", "genre": "Action, Historical", "image": url_for('static', filename='images/mad.jpg')}, # CORRECTED
        {"title": "ROBINHOOD", "genre": "Action, Thriller", "image": url_for('static', filename='images/robinhood.jpg')}, # CORRECTED
        {"title": "PRESENCE", "genre": "Action, Drama", "image": url_for('static', filename='images/presence.jpg')}, # CORRECTED
    ]
    return render_template('home1.html', movies=trending_movies)

@app.route('/search_results', methods=['GET'])
def search_results():
    """
    Displays movie search results.
    """
    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))
        
    query = request.args.get('query', '')
    language = request.args.get('language', '')
    city = request.args.get('city', '')

    # Placeholder for search logic (in a real app, query a database)
    # For now, let's just return some sample movies
    all_movies = [
        {"title": "Pushpa: The Rise", "genre": "Action, Drama", "price": 190, "image": "https://via.placeholder.com/150/FF5733/FFFFFF?text=Pushpa", "language": "Telugu"},
        {"title": "RRR", "genre": "Action, Historical", "price": 220, "image": "https://via.placeholder.com/150/33FF57/FFFFFF?text=RRR", "language": "Telugu"},
        {"title": "Baahubali 2: The Conclusion", "genre": "Action, Fantasy", "price": 220, "image": "https://via.placeholder.com/150/3357FF/FFFFFF?text=Baahubali", "language": "Telugu"},
        {"title": "Sita Ramam", "genre": "Romance, Drama", "price": 190, "image": "https://via.placeholder.com/150/FF33D1/FFFFFF?text=Sita+Ramam", "language": "Telugu"},
        {"title": "Bimbisara", "genre": "Action, Fantasy", "price": 175, "image": "https://via.placeholder.com/150/D1FF33/FFFFFF?text=Bimbisara", "language": "Telugu"},
        {"title": "Karthikeya 2", "genre": "Mystery, Thriller", "price": 175, "image": "https://via.placeholder.com/150/33FFD1/FFFFFF?text=Karthikeya+2", "language": "Telugu"},
    ]

    # Simple filtering based on query, language, city (highly simplified)
    filtered_movies = [
        movie for movie in all_movies 
        if query.lower() in movie['title'].lower() or 
           language.lower() == movie['language'].lower() or
           not (query or language or city) # Show all if no filter
    ]
    
    return render_template('search_results.html', movies=filtered_movies, query=query, language=language, city=city)

@app.route('/b1/<movie_title>/<theater_name>/<price>', methods=['GET'])
def b1(movie_title, theater_name, price):
    """
    Displays the booking form page (b1.html) [1].
    Only accessible if logged in [1].
    Movie details are passed via URL.
    """
    if not is_logged_in():
        flash('Please log in to book tickets.', 'warning')
        return redirect(url_for('login'))
        
    # In a real app, you'd fetch movie/theater details from a database
    # For this example, we're using the passed URL parameters.
    movie_details = {
        'title': movie_title.replace('_', ' '),
        'theater': theater_name.replace('_', ' '),
        'price_per_ticket': float(price),
        'location': 'Mirajkar Cinemas, Attapur, Hyderabad', # Example
        'date_options': ['Mon, Apr 14', 'Tue, Apr 15', 'Wed, Apr 16', 'Thu, Apr 17', 'Fri, Apr 18', 'Sat, Apr 19', 'Sun, Apr 20'],
        'time_options': ['10:00 AM', '12:30 PM', '03:15 PM', '06:00 PM', '09:00 PM'],
        'seats_layout': { # Example seat layout
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
    """
    Accepts POST data after selecting seats and confirms the booking [1].
    Creates a new booking and adds it to the temporary 'bookings' list [1].
    """
    global booking_counter # Needed to modify the global counter
    if not is_logged_in():
        flash('Please log in to complete your booking.', 'warning')
        return redirect(url_for('login'))

    movie_title = request.form['movie_title']
    theater_name = request.form['theater_name']
    selected_date = request.form['selected_date']
    selected_time = request.form['selected_time']
    selected_seats_str = request.form.get('selected_seats', '') # Get selected seats string
    selected_seats = json.loads(selected_seats_str) if selected_seats_str else [] # Parse JSON string to list
    total_amount = float(request.form['total_amount'])
    full_name = request.form['full_name']
    phone_number = request.form['phone_number']
    payment_method = request.form['payment_method'] # e.g., 'Cash on Delivery'

    # Generate a unique booking ID [1]
    booking_id = f"MVM-{datetime.now().strftime('%Y%m%d')}-{booking_counter}"
    booking_counter += 1

    # Create a new booking dictionary [1]
    new_booking = {
        'booking_id': booking_id,
        'user_id': session.get('user_id'),
        'user_name': full_name, # Storing for ticket display
        'movie_title': movie_title,
        'theater_name': theater_name,
        'date': selected_date,
        'time': selected_time,
        'seats': selected_seats,
        'amount_paid': total_amount,
        'payment_method': payment_method,
        'booking_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Store booking timestamp [1]
    }
    
    # Add booking to the temporary 'bookings' list [1]
    bookings.append(new_booking)
    
    flash('Your tickets have been successfully booked! Enjoy the show!', 'success')
    return render_template('tickets.html', booking=new_booking) # Display confirmation in tickets.html [1]

@app.route('/about')
def about():
    """
    Displays the About Us page [1]. Requires user to be logged in.
    """
    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    """
    Displays the Contact Us page [1]. Requires user to be logged in.
    """
    if not is_logged_in():
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('contact_us.html')


# --- Running the Flask App --- [1]
if __name__ == '__main__':
    # When debug=True, the server will reload automatically on code changes [1]
    # and provide a debugger in the browser if errors occur.
    app.run(debug=True)
    # The app will run on http://localhost:5000 [1]