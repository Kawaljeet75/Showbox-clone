from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, render_template_string, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Token generator
serializer = URLSafeTimedSerializer(app.secret_key)

def generate_reset_token(email):
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email


# Email Configuration (use your real Gmail info or app password)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kawaljeetparmar203@gmail.com'
app.config['MAIL_PASSWORD'] = 'gyab mzvv cbvm rzup'  # Use App Password if 2FA is on
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

# Connect to database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('C:/Users/kawal/Projects/movie-booking/database/movie_booking.db',
            timeout=10,
            check_same_thread=False
        )
        g.db.row_factory = sqlite3.Row
    return g.db


# Automatically close DB connection after each request
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize schema from schema.sql
def init_db():
    """Read schema.sql and create any missing tables/indexes."""
    db = get_db()
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Call init_db() within app context
with app.app_context():
    init_db()


# Homepage 
@app.route('/movies')
def movies():
    # if 'user' not in session:
    #     return redirect(url_for('login'))

    db = get_db()

    # Fetch the list of cities from the cities table
    cursor = db.execute('SELECT id, name FROM cities')
    cities = cursor.fetchall()

    # Fetch the list of genres from the genres table
    genre_cursor = db.execute('SELECT id, name FROM genres')
    genres = genre_cursor.fetchall()

    # Get search query, city filter, and genre filter from the URL (if present)
    search_query = request.args.get('q', '').strip()
    city_id = request.args.get('city_id', None)  # Fetch selected city_id from URL
    genre_name = request.args.get('genre', None)  # Fetch selected genre_id from URL

    # Build the query dynamically based on the filters
    query = """
        SELECT * FROM movies
        WHERE title LIKE ?
    """
    params = ('%' + search_query + '%',)

    # Add city filter if specified
    if city_id:
        # query += " AND city_id = ?"
        # params += (city_id,)
        pass

    # Add genre filter if specified
    if genre_name:
        query += " AND genre LIKE ?"
        params += ('%' + genre_name + '%',)
        query += " LIMIT 10"

    # Execute the query with dynamic parameters
    movies = db.execute(query, params).fetchall()

    return render_template('movies.html', cities=cities, genres=genres, movies=movies, search_query=search_query, city_id=city_id, genre_name=genre_name)

# All Movies List 
def get_all_movies():
    conn = sqlite3.connect('C:/Users/kawal/Projects/movie-booking/database/movie_booking.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies')
    movies = cursor.fetchall()
    conn.close()
    return movies
 
@app.route('/all-movies')
def all_movies():
    movies = get_all_movies()
    return render_template('allmovies.html', movies=movies)

# Movie Detail Page
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    # if 'user' not in session:
    #     return redirect(url_for('login'))

    conn = get_db()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()

    if not movie:
        return "Movie not found", 404

    # Convert sqlite3.Row to a regular dictionary
    movie = dict(movie)

    # Embed URL handling
    trailer_url = movie.get('trailer_url', '')
    if "watch?v=" in trailer_url:
        movie['embed_url'] = trailer_url.replace("watch?v=", "embed/")
    else:
        movie['embed_url'] = trailer_url

    return render_template('movie_detail.html', movie=movie)

# sign up logic 
@app.route('/ajax-register', methods=['POST'])
def ajax_register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    conn = get_db()

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'})

    hashed_password = generate_password_hash(password)

    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()

        # Fetch new user from DB
        new_user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        print("Fetched user:", new_user)

        if new_user:
            session['user'] = new_user['username']
            session['user_id'] = new_user['id']
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to fetch user after registration'})
        
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or email already exists'})


# login route 
@app.route('/ajax-login', methods=['POST'])
def ajax_login():
    identifier = request.form['identifier']  # can be username or email
    password = request.form['password']
    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (identifier, identifier)
    ).fetchone()

    if user and check_password_hash(user['password'], password):
        session['user'] = user['username']  # or user['id']
        session['user_id'] = user['id']
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

# forgot password logic 
@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    email = request.form['email']
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user:
        token = generate_reset_token(email)
        reset_url = url_for('movies', _external=True) + f"?reset_token={token}"
        msg = Message("Password Reset Request", recipients=[email])
        msg.body = f'''Hi,

To reset your password, click the following link:

{reset_url}

If you did not request this, please ignore this email.
'''
        mail.send(msg)  # Indentation fixed here
        return jsonify({"status": "success", "message": "Reset link sent to your email."})
    else:  # Indentation fixed here
        return jsonify({"status": "fail", "message": "Email not found."})


# reset route 
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        if request.method == 'POST':
            return jsonify({"status": "error", "message": "Invalid or expired token."}), 400
        return render_template_string('<div>Invalid or expired token.</div>')

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            return jsonify({"status": "error", "message": "Passwords do not match."}), 400

        hashed_password = generate_password_hash(new_password)
        conn = get_db()
        conn.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
        conn.commit()
        return jsonify({"status": "success", "message": "Password reset successful."})

    # Render the reset modal HTML only (partial)
    return render_template('partials/reset_modal.html', token=token)


# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('movies'))


# Utility functions
def get_movie(movie_id):
    conn = sqlite3.connect('C:/Users/kawal/Projects/movie-booking/database/movie_booking.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cur.fetchone()
    conn.close()
    return movie


# Load seat layout based on bookings
def load_seat_layout(movie_id, show_date, show_time, rows=8, cols=18):
    # Build an empty grid
    layout = []
    for r in range(rows):
        row_label = chr(65 + r)  # 'A','B',...
        layout.append([
            {'seat_no': f"{row_label}{c+1}"}
            for c in range(cols)
        ])

    # Fetch already-booked seats for that slot
    db = get_db()
    booked_rows = db.execute(
        'SELECT seat_no FROM bookings '
        'WHERE movie_id=? AND show_date=? AND show_time=?',
        (movie_id, show_date, show_time)
    ).fetchall()
    taken = {row['seat_no'] for row in booked_rows}

    # Annotate each seat
    for row in layout:
        for seat in row:
            seat['status'] = 'taken' if seat['seat_no'] in taken else 'available'

    return layout

@app.route('/booking/<int:movie_id>', methods=['GET', 'POST'])
def booking_page(movie_id):
    db = get_db()

    # Fetch movie details
    movie_row = db.execute(
        'SELECT * FROM movies WHERE id=?', (movie_id,)
    ).fetchone()
    if not movie_row:
        flash('Movie not found.', 'error')
        return redirect(url_for('movies'))
    movie = dict(movie_row)

    # Build 7 days for the date picker
    today = datetime.today().date()
    all_dates = [{
        'display_day': (today + timedelta(days=i)).strftime('%a'),
        'display_date': (today + timedelta(days=i)).strftime('%d').lstrip('0'),
        'value': (today + timedelta(days=i)).isoformat()
    } for i in range(7)]

    # Define showtimes
    showtimes = ['10:00', '13:00', '16:00', '19:00', '21:00']

    # Handle form submission
    if request.method == 'POST':
        d = request.form.get('date')
        t = request.form.get('showtime')
        seats = request.form.getlist('seats')
        if not (d and t and seats):
            flash('Select date, time & at least one seat.', 'error')
            return redirect(request.url)

        try:
            with db:
                for s in seats:
                    db.execute(
                        'INSERT INTO bookings(movie_id, show_date, show_time, seat_no, booked_at) '
                        'VALUES (?, ?, ?, ?, ?)',
                        (movie_id, d, t, s, datetime.now(timezone.utc).isoformat())
                    )
        except sqlite3.IntegrityError:
            flash('Some seats just got booked—try choosing again.', 'error')
            return redirect(request.url)

        # Redirect with chosen slot in query string
        return redirect(url_for(
            'confirm_booking',
            movie_id=movie_id,
            date=d,
            time=t,
            seats=','.join(seats)
        ))


    # Determine which slot to display: from query or defaults
    # chosen_date = request.args.get('date')         
    # chosen_time = request.args.get('time')


    # Layout defaults: used only to fetch seat_layout
    # layout_date = chosen_date or request.args.get('date') or all_dates[0]['value']
    # layout_time = chosen_time or request.args.get('time') or showtimes[0]

    # Try getting selected date/time from query string; fallback to defaults
    layout_date = request.args.get('date') or all_dates[0]['value']
    layout_time = request.args.get('time') or showtimes[0]

    seat_layout = load_seat_layout(movie_id, layout_date, layout_time)

    # Render with everything the template needs
    return render_template(
        'booking.html',
        movie=movie,
        dates=all_dates,
        showtimes=showtimes,
        seat_layout=seat_layout,
        chosen_date=layout_date,
        chosen_time=layout_time
    )

@app.route('/booking/<int:movie_id>/confirm')
def confirm_booking(movie_id):
    db = get_db()
    movie = db.execute(
        'SELECT title FROM movies WHERE id=?', (movie_id,)
    ).fetchone()

    selected_date = request.args.get('date')
    selected_time = request.args.get('time')
    seats = request.args.get('seats', '').split(',')

    return render_template(
        'confirmation.html',
        movie=movie,
        date=selected_date,
        time=selected_time,
        seats=seats
    )

@app.route('/')
def home():
    return redirect(url_for('movies'))

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)

