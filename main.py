import tempfile

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
from test import login
from add_face import signUp
import os
from file_encryption import encrypt_file, decrypt_file, generate_key
from dotenv import load_dotenv

load_dotenv()
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS').split(',')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'some_secret_key'


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_upload_dir(username):
    return os.path.join(app.config['UPLOAD_FOLDER'], username)


def ensure_user_upload_dir_exists(username):
    user_upload_dir = get_user_upload_dir(username)
    if not os.path.exists(user_upload_dir):
        os.makedirs(user_upload_dir)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'POST':
        username = request.form.get('username')
        if username and login(username):
            ensure_user_upload_dir_exists(username)
            session['username'] = username
            return render_template('welcome.html', username=username, filenames=get_uploaded_filenames(username))
        else:
            return render_template('login.html', error="Sorry, you are not authorized!")
    else:
        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup_user():
    if request.method == 'POST':
        name = request.form['name']
        signUp(name)
        return render_template('index.html', name=name)
    else:
        # Handle GET request (show sign-up form)
        return render_template('signup.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def welcome():
    if 'username' in session:
        username = session['username']
        filenames = get_uploaded_filenames(username)
        return render_template('welcome.html', username=username, filenames=filenames)
    else:
        return redirect(url_for('login_user'))  # Redirect if not logged in


@app.route('/upload', methods=['POST'])
def upload_file():
    username = request.form.get('username')
    # if 'file' not in request.files:
    #     return redirect(request.url)
    # file = request.files['file']
    # if file.filename == '':
    #     return redirect(request.url)
    # if file:
    #     username = request.form.get('username')
    #     user_upload_dir = get_user_upload_dir(username)
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(user_upload_dir, filename))
    #     return redirect(url_for('login_user', username=username))  # Redirect to welcome page
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_upload_dir = get_user_upload_dir(username)
        file.save(os.path.join(user_upload_dir, filename))

        if ENCRYPTION_KEY:
            encrypt_file(os.path.join(user_upload_dir, filename), ENCRYPTION_KEY)
            os.remove(os.path.join(user_upload_dir, filename))

        return redirect(url_for('login_user', username=username))
    else:
        return "Error: File type not allowed."


def get_uploaded_filenames(username):
    user_upload_dir = get_user_upload_dir(username)
    if os.path.exists(user_upload_dir):
        return [f for f in os.listdir(user_upload_dir) if os.path.isfile(os.path.join(user_upload_dir, f))]
    else:
        return []


@app.route('/delete/<username>/<filename>', methods=['GET'])
def delete_file(username, filename):
    user_upload_dir = get_user_upload_dir(username)
    file_path = os.path.join(user_upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    # return redirect(url_for('index'))
    return redirect(url_for('login_user', username=username))


@app.route('/download/<username>/<filename>')
def download_file(username, filename):
    user_upload_dir = get_user_upload_dir(username)
    encrypted_filepath = os.path.join(user_upload_dir, filename)
    if not ENCRYPTION_KEY:
        print("Error: ENCRYPTION_KEY not found in environment variables.")
        return "Error: Encryption key not found."
    try:
        if filename.endswith('.encrypted'):
            filename = filename[:-10]  # Remove the '.encrypted' suffix
        decrypt_file(encrypted_filepath, ENCRYPTION_KEY)
        decrypted_filename = filename[:-10] if filename.endswith('.encrypted') else filename
        decrypted_filepath = os.path.join(user_upload_dir, decrypted_filename)
        print("Decrypted file path:", decrypted_filepath)
        if os.path.exists(decrypted_filepath):
            return send_from_directory(user_upload_dir, decrypted_filename, as_attachment=True)
        else:
            print("Decrypted file not found.")
            return "Decrypted file not found."
    except Exception as e:
        print(f"Error decrypting file: {e}")
        return "Error decrypting file."

# @app.route('/download/<username>/<filename>')
# def download_file(username, filename):
#     user_upload_dir = get_user_upload_dir(username)
#     encrypted_filepath = os.path.join(user_upload_dir, filename)
#
#     if not ENCRYPTION_KEY:
#         return "Error: Encryption key not found.", 400  # Bad Request
#
#     try:
#         if filename.endswith('.encrypted'):
#             filename = filename[:-10]  # Remove the '.encrypted' suffix
#
#         with tempfile.TemporaryDirectory() as temp_dir:
#             decrypted_filepath = os.path.join(temp_dir, filename)
#             decrypt_file(encrypted_filepath, decrypted_filepath)
#
#             if os.path.exists(decrypted_filepath):
#                 return send_from_directory(temp_dir, filename, as_attachment=True)
#             else:
#                 return "Error: Decrypted file not found.", 500  # Internal Server Error
#
#     except Exception as e:
#         print(f"Error decrypting file: {e}")
#         return "Error: An error occurred during decryption.", 500  # Internal Server Error


@app.route('/logout')
def logout_user():
    # Clear session
    session.pop('username', None)
    # Redirect to the home page or any other desired page after logout
    return redirect(url_for('index'))


if __name__ == "__main__":
    if not ENCRYPTION_KEY:
        print("Warning: ENCRYPTION_KEY not set. Files will not be encrypted.")
    if not ENCRYPTION_KEY:
        print("Error: ENCRYPTION_KEY not found in environment variables.")
    else:
        print("ENCRYPTION_KEY:", ENCRYPTION_KEY)
    app.run(debug=True)
