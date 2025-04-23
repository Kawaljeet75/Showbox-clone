from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            'C:/Users/kawal/Projects/movie-booking/movie_booking.db',
            timeout=10,
            check_same_thread=False
        )
        g.db.row_factory = sqlite3.Row
    return g.db

# Create tables
def init_db():
    conn = get_db()

    # Users table
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );''')

    # Movies detail table
    conn.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        showtime TEXT,
        genre TEXT,
        rating REAL,
        poster_url TEXT
    );''')

    # Bookings table
    conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        movie_id INTEGER,
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    );''')

    # Seats table
    conn.execute('''CREATE TABLE IF NOT EXISTS seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        seat_number TEXT,
        is_booked INTEGER DEFAULT 0,
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    );''')

    conn.commit()

# Seat automation functions
def add_seats_for_movie(movie_id, total_seats=30):
    """
    This function automatically generates seat numbers (e.g., A1, A2, ..., C10)
    and inserts them into the `seats` table for a given movie.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Generate seat numbers (A1 to C10)
    for row in ['A', 'B', 'C']:
        for i in range(1, 11):  # 1 to 10 for seats 1 to 10
            seat_code = f"{row}{i}"  # For example: A1, A2, B1, B2, etc.
            cursor.execute('''
                INSERT INTO seats (movie_id, seat_number, is_booked)
                VALUES (?, ?, ?)
            ''', (movie_id, seat_code, 0))  # 0 means the seat is not booked yet

    conn.commit()

def add_seats_for_all_movies():
    """
    This function adds seats for all movies in the `movies` table.
    It will automatically add seats for every movie using their movie_id.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Fetch all movie IDs from the movies table
    cursor.execute('SELECT id FROM movies')
    movie_ids = cursor.fetchall()

    # Add seats for each movie
    for movie_id_tuple in movie_ids:
        movie_id = movie_id_tuple[0]
        add_seats_for_movie(movie_id)  # Call the function to add seats for this movie

    conn.close()

# Call init_db() within app context
with app.app_context():
    init_db()

# Automatically close DB connection after each request
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Home page (movie listing)
@app.route('/movies')
def movies():
    # Optional: Uncomment if you want to restrict this page to logged-in users only
    # if 'user' not in session:
    #     return redirect(url_for('login'))

    search_query = request.args.get('q', '').strip()

    conn = get_db()
    if search_query:
        # Case-insensitive search using LIKE on title or genre
        query = "SELECT * FROM movies WHERE title LIKE ? OR genre LIKE ?"
        movies = conn.execute(query, ('%' + search_query + '%', '%' + search_query + '%')).fetchall()
    else:
        movies = conn.execute('SELECT * FROM movies').fetchall()

    return render_template('movies.html', movies=movies)


# Movie Detail Page
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    if 'user' not in session:
        return redirect(url_for('login'))

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


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        if user:
            session['user'] = username
            return redirect(url_for('movies'))
        return "Invalid credentials!"
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('movies'))



# Cinema Selection 
@app.route('/select_cinema', methods=['GET', 'POST'])
def select_cinema():
    if request.method == 'POST':
        movie_id = request.form['movie_id']
        selected_cinema = request.form['cinema_id']
        
        # Store cinema selection in session or database
        session['cinema_id'] = selected_cinema

        return redirect(url_for('select_language', movie_id=movie_id))
    return render_template('select_cinema.html', movie_id=movie_id)



@app.route('/booking/<int:movie_id>')
def booking_page(movie_id):
    # Connect to the database
    conn = sqlite3.connect('C:/Users/kawal/Projects/movie-booking/movie_booking.db')
    cursor = conn.cursor()

    # Get movie info
    cursor.execute("SELECT id, title, genre, rating, description, poster_url FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()

    if not movie:
        return "Movie not found", 404

    conn.close()

    # Convert to dictionary so it's easy to use in template
    movie_dict = {
        'id': movie[0],
        'title': movie[1],
        'genre': movie[2],
        'rating': movie[3],
        'description': movie[4],
        'poster_url': movie[5]
    }

    # Render the booking page
    return render_template('booking.html', movie=movie_dict)


# Booked movie
@app.route('/book-movie', methods=['POST'])
def book_movie():
    movie_id = request.form['movie_id']
    seat_number = request.form['seat_number']
    cinema = request.form['cinema']
    language = request.form['language']
    date = request.form['date']
    showtime = request.form['showtime']

    # Save the booking (you can improve this later)
    conn = sqlite3.connect('C:/Users/kawal/Projects/movie-booking/movie_booking.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO seats (movie_id, seat_number, is_booked) VALUES (?, ?, 1)", (movie_id, seat_number))
    conn.commit()
    conn.close()

    return f"✅ Booking confirmed for seat {seat_number} at {cinema} ({language}) on {date} at {showtime}!"

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    if 'user' not in session:
        return redirect(url_for('login'))

    movie_id = request.form.get('movie_id')
    showtime = request.form.get('showtime')
    selected_seats = request.form.get('selected_seats')  # e.g. "A1,A2,A3"
    cinema = request.form.get('cinema')
    language = request.form.get('language')
    date = request.form.get('date')

    if not selected_seats:
        return "No seats selected!", 400

    seat_list = selected_seats.split(',')

    conn = get_db()
    cursor = conn.cursor()

    for seat in seat_list:
        # Check if already booked
        cursor.execute('''
            SELECT is_booked FROM seats WHERE movie_id=? AND seat_number=? LIMIT 1
        ''', (movie_id, seat))
        existing = cursor.fetchone()
        if existing and existing['is_booked'] == 1:
            return f"Seat {seat} already booked!", 400

        # Mark seat as booked
        cursor.execute('''
            INSERT OR REPLACE INTO seats (movie_id, seat_number, is_booked)
            VALUES (?, ?, 1)
        ''', (movie_id, seat))

    # Optional: Save into bookings table (you can expand this later)
    cursor.execute('''
        INSERT INTO bookings (user, movie_id)
        VALUES (?, ?)
    ''', (session['user'], movie_id))

    conn.commit()
    conn.close()

    return render_template('success.html', seats=seat_list, movie_id=movie_id, showtime=showtime, cinema=cinema, language=language, date=date)


# My bookings
@app.route('/my-bookings')
def my_bookings():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    bookings = conn.execute('''
        SELECT movies.title, movies.showtime 
        FROM bookings 
        JOIN movies ON bookings.movie_id = movies.id 
        WHERE bookings.user = ?
    ''', (session['user'],)).fetchall()

    return render_template('bookings.html', bookings=bookings)

@app.route('/')
def home():
    return redirect(url_for('movies'))

if __name__ == '__main__':
    app.run(debug=True)
