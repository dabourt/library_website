# test Ci 
import traceback

try:
    from flask import Flask, request, render_template, redirect, url_for, session, flash
    import json
    import os
    import requests

    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    DB_SERVER_URL = "http://lib-db-cluster-svc:5000/data"
    #  DB_SERVER_URL = "http://192.168.1.24:5000/data" # for testing on local machine


    AUTH_USERNAME = os.getenv("LIB_DB_USERNAME")
    AUTH_PASSWORD = os.getenv("LIB_DB_PASSWORD")
    
    # Custom test to check if a book is in the borrowed books list
    @app.template_test('contains')
    def contains_test(borrowed_books, title):
        return title in borrowed_books

    # Load or initialize the database
    def load_books():
        response = requests.get(f"{DB_SERVER_URL}/books.json", auth=(AUTH_USERNAME, AUTH_PASSWORD))
        if response.status_code == 200:
            return response.json()
        return []

    def save_books(books):
        requests.post(f"{DB_SERVER_URL}/books.json", json=books, auth=(AUTH_USERNAME, AUTH_PASSWORD))

    def load_users():
        response = requests.get(f"{DB_SERVER_URL}/users.json", auth=(AUTH_USERNAME, AUTH_PASSWORD))
        if response.status_code == 200:
            return response.json()
        return []

    def save_users(users):
        requests.post(f"{DB_SERVER_URL}/users.json", json=users, auth=(AUTH_USERNAME, AUTH_PASSWORD))

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/books')
    def book_list():
        books = load_books()
        users = load_users()
        return render_template('books.html', books=books, users=users)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/add_book', methods=['GET', 'POST'])
    def add_book():
        # Ensure only admin users can access this route
        if 'username' not in session or not session.get('is_admin'):
            flash('You do not have permission to access this page.')
            return redirect(url_for('home'))

        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            available = request.form['available'] == 'true'

            books = load_books()
            books.append({'title': title, 'author': author, 'available': available})
            save_books(books)

            return redirect(url_for('book_list'))

        return render_template('add_book.html')

    @app.route('/search_books', methods=['GET'])
    def search_books():
        query = request.args.get('query', '').lower()
        books = load_books()
        users = load_users()
        results = [book for book in books if query in book['title'].lower() or query in book['author'].lower()]
        return render_template('search_books.html', results=results, users=users)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            is_admin = request.form.get('is_admin') == 'true'
            admin_password = request.form.get('admin_password')

            # Validate admin password
            if is_admin and admin_password != 'admin123':
                flash('Invalid admin password!')
                return render_template('register.html')

            users = load_users()
            if any(user['username'] == username for user in users):
                flash('Username already exists!')
                return render_template('register.html')
            
            new_user = {'username': username, 'password': password}
            if is_admin:
                new_user['is_admin'] = True
            
            users.append(new_user)
            save_users(users)

            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            next_page = request.form.get('next')

            users = load_users()
            user = next((user for user in users if user['username'] == username and user['password'] == password), None)
            if user:
                session['username'] = username
                session['is_admin'] = user.get('is_admin', False)
                return redirect(url_for('home'))
            else:
                error = 'Invalid credentials! Please try again.'
                return render_template('login.html', next=request.args.get('next'), error=error)

        return render_template('login.html', next=request.args.get('next'))

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        session.pop('is_admin', None)
        return redirect(url_for('home'))

    @app.route('/borrow_book/<title>', methods=['POST'])
    def borrow_book(title):
        if 'username' not in session:
            flash('You need to be logged in to borrow a book. Please <a href="' + url_for('login') + '">log in</a> or register.')
            return redirect(url_for('search_books'))
        
        books = load_books()
        users = load_users()
        for book in books:
            if book['title'] == title and book['available']:
                book['available'] = False
                save_books(books)
                for user in users:
                    if user['username'] == session['username']:
                        if 'borrowed_books' not in user:
                            user['borrowed_books'] = []
                        user['borrowed_books'].append(title)
                        save_users(users)
                        break
                break
        return redirect(url_for('book_list'))

    @app.route('/return_book/<title>', methods=['POST'])
    def return_book(title):
        if 'username' not in session:
            return redirect(url_for('login', next=url_for('return_book', title=title)))
        
        books = load_books()
        users = load_users()
        for book in books:
            if book['title'] == title and not book['available']:
                book['available'] = True
                save_books(books)
                for user in users:
                    if user['username'] == session['username']:
                        if 'borrowed_books' in user and title in user['borrowed_books']:
                            user['borrowed_books'].remove(title)
                            save_users(users)
                            break
                break
        return redirect(url_for('book_list'))

    @app.route('/remove_book/<title>', methods=['POST'])
    def remove_book(title):
        if 'username' not in session or not session.get('is_admin'):
            flash('You do not have permission to perform this action.')
            return redirect(url_for('home'))

        books = load_books()
        books = [book for book in books if book['title'] != title]
        save_books(books)

        users = load_users()
        for user in users:
            if 'borrowed_books' in user and title in user['borrowed_books']:
                user['borrowed_books'].remove(title)
        save_users(users)

        return redirect(url_for('book_list'))

    @app.route('/user')
    def user_page():
        if 'username' not in session:
            flash('You need to be logged in to view your profile. Please <a href="' + url_for('login') + '">log in</a> or register.')
            return redirect(url_for('login'))
        
        users = load_users()
        user = next((user for user in users if user['username'] == session['username']), None)
        if user:
            borrowed_books = user.get('borrowed_books', [])
            return render_template('user.html', username=user['username'], borrowed_books=borrowed_books)
        else:
            return redirect(url_for('home'))

    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('home'))

    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=5000)  # Use localhost address

except Exception as e:
    print("Error while importing 'app':")
    traceback.print_exc()
