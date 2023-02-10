import sqlite3
import logging
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
class DATABASE: 
    def __init__(self):
        self.DATABASE_NAME = 'database.db'
        self.connection_counter = 0

    # Function to get a database connection.
    # This function connects to database with the name `database.db`
    def get_db_connection(self):
        connection = sqlite3.connect(self.DATABASE_NAME)
        connection.row_factory = sqlite3.Row
        self.connection_counter = self.connection_counter + 1
        return connection

    # Function to close a database connection.
    def close_db_connection(self, connection):
        connection.close()
        self.connection_counter = self.connection_counter - 1

    # Function to get a post using its ID
    def get_post(self,post_id):
        connection = self.get_db_connection()
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                            (post_id,)).fetchone()
        self.close_db_connection(connection)
        return post

    # Function to get a post count
    def get_counters(self):
        connection = self.get_db_connection()
        cursor = connection.execute('SELECT * FROM posts')
        post_counter = len (cursor.fetchall())
        connection_counter = self.connection_counter
        self.close_db_connection(connection)
        return post_counter, connection_counter

# Function to print LOG message
def print_log(msg):
    sys.stdout.write(msg + "\n")
    app.logger.info(msg)

# Function to print ERROR LOG message
def print_error_log(msg):
    sys.stderr.write(msg + "\n")
    app.logger.warning(msg)

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
db = DATABASE()

# Define the main route of the web application 
@app.route('/')
def index():
    connection = db.get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    db.close_db_connection
    print_log('The homepage has been retrieved.')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = db.get_post(post_id)
    if post is None:
      print_error_log('Post not found!')  
      return render_template('404.html'), 404
    else:
      print_log('The <<' + post['title'] + '>> post has been retrieved.' )  
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    print_log('The about webpage has been retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = db.get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            db.close_db_connection
            print_log('The <<' + title + '>> post has been created successfully.' )
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the Healthcheck endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response = json.dumps({
            "result" : "OK - healthy"
        }),
        status = 200,
        mimetype = 'application/json'
    )
    print_log('Healthz request successful')
    return response

# Define the Metrics endpoint
@app.route('/metrics')
def metrics():
    post_counter, connection_counter = db.get_counters()
    response = app.response_class(
        response = json.dumps(
            {
                "status" : "success",
                "data" : 
                {
                    "post_count" : post_counter,
                    "db_connection_count" : connection_counter
                }
            }
        ),
        status = 200,
        mimetype = 'application/json'
    )
    print_log('Metrics request successfull.')
    return response

# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
        # filename="app.log")
    app.run(host='0.0.0.0', port='3111')
