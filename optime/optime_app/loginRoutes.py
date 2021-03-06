from .app import *
import string
import random
import smtplib
from optime_app.API.instance import config
import urllib

smtp_server = smtplib.SMTP_SSL(host="smtp.gmail.com")

############### HOME/LOGIN ###############
@app.route('/index')
@app.route('/')
def index():
    """
    Serve the home page, which displays the users personal and shopping tasks
    """

    if g.user is None:
        return render_template('index.html')
    elif not g.user["validated"]:
        return redirect(url_for("validate"))
    else:
        return render_template('tasks.html', tasks=g.user['items'],
                               shoppingTasks=g.user['shoppingTasks'],
                               number=g.user['phone_number'],
                               lentasks=len(g.user['items']),
                               allProducts=getAllProducts(),
                               allStores=getAllStores(),
                               lenshoppingtasks=len(g.user['shoppingTasks']))


@app.route('/update_settings', methods=("POST",))
@login_required
def update_settings():
    """
    Update the user's phone number in the database for task notification purposes
    """

    phone_number = request.form.get("phone_number")
    if phone_number is None:
        return "No phone number given"
    else:
        phone_number = "".join(char for char in phone_number)

        if len(phone_number) != 10 or not phone_number.isdigit():
            return "phone number is invalid"

        db = get_db()
        db.users.update_one({"_id": g.user["_id"]}, {
                            "$set": {"phone_number": phone_number}})
        return redirect(url_for('index'))
"""
@app.route('/auth/reset', methods=['GET', 'POST'])
def reset():
    #When user forget the password, invoke this commands
    #Forgot password request here
    #invoke command forgot_password(email, code)
    #code generated same wat as for register
    code = 1
"""
@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    """
    Register a user based on a username, password, email address, and location
    """

    error = None
    if request.method == 'POST':
        print('Getting post request for register')
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        lat = request.form['lat']
        lon = request.form['lon']

        db = get_db()

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif db.users.find_one({'email': email}):
            error = 'A user with that email is already registered'
        elif db.users.find_one({'username': username}):
            error = 'A user with username {} is already registered.'.format(
                username)

        if error is None:
            password_hash = generate_password_hash(password)
            chars = string.ascii_letters + string.digits + string.punctuation
            code = urllib.parse.quote(''.join(random.choice(chars) for i in range(32)), safe='')
            db.users.insert_one(
                {'username': username,
                 'email': email,
                 'lat': lat,
                 'lon': lon,
                 'password': password_hash,
                 'items': [],
                 'shoppingTasks': [],
                 'phone_number': '',
                 'code': code,
                 'validated': False
                 })
            send_verification_email(email, code)
            return redirect(url_for('login', error="Check your email to verify your account"))
        else:
            print(error)

    return render_template('register.html', error=error)

def send_verification_email(email, code):
    gmail_user = config.GMAIL_USER
    gmail_password = config.GMAIL_PASSWORD
    link = f"{config.WEBSITE_LINK}/auth/validate?code={code}"
    subject = "Email confirmation"
    body_text = (f"Please confirm your email for Optime by following "
                 f"this link: {link}")
    email_text = (f"From: {gmail_user}\nTo: {email}\nSubject: {subject}"
                  f"\n\n\n{body_text}")
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(gmail_user, email, email_text)


def forgot_password(email, code):
    gmail_user = config.GMAIL_USER
    gmail_password = config.GMAIL_PASSWORD
    link = f"{config.WEBSITE_LINK}/auth/reset?code={code}"
    subject = "Reset Password"
    body_text = (f"Click the following link to reset your password: {link}")
    email_text = (f"From: {gmail_user}\nTo: {email}\nSubject: {subject}"
                  f"\n\n\n{body_text}")
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(gmail_user, email, email_text)


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """
    Validate that the user inputted the correct information, login the user
    """

    print('Getting request for login')
    error = None
    print("Gettingreqf")
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        db = get_db()
        print(f"lat:{lat}, lon:{lon}")

        user = db.users.find_one({'email': email})
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        elif lat == "" or lon == "":
            error = 'Please allow location access'
        if error is None:
            session.clear()
            session['user_id'] = str(user['_id'])
            session['location'] = (lat, lon)
            newLat = {"$set": {"lat": lat}}
            newLon = {"$set": {"lon": lon}}
            db.users.update_one({'email': email}, newLat)
            db.users.update_one({'email': email}, newLon)

            if "next" in request.args:
                return redirect(request.args["next"])
            else:
                return redirect(url_for('index'))

        flash(error)

    next_url = request.args.get('next')
    if next_url is not None:
        form_action = url_for('login', next=next_url)
    else:
        form_action = url_for('login')
    return (render_template('login.html', error=error,
                            form_action=form_action), 200)



@app.before_request
def load_logged_in_user():
    """
    Initialize the user's session
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().users.find_one({"_id": ObjectId(user_id)})
        print("Logged in user")


@app.route('/auth/logout')
def logout():
    """
    Logout the user
    """
    session.clear()
    return redirect(url_for('index'))

@app.route('/auth/validate')
@only_login_required
def validate():
    """
    Validate email address
    """
    code = request.args.get("code")
    if g.user["validated"]:
        next_url = request.args.get("next")
        if next_url:
            return redirect(next_url)
        else:
            return redirect(url_for('index'))
    elif code is None:
        return render_template("login.html",
                               error="Follow the link provided in your "
                                     "verification email.")
    else:
        unescaped_code = urllib.parse.unquote(g.user["code"])
        if unescaped_code == code:
            db = get_db()
            db.users.update_one({"_id": g.user["_id"]}, {"$set": {"validated": True}})
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            else:
                return redirect(url_for('index'))
        else:
            print(code)
            print(unescaped_code)
            return render_template("login.html",
                                   error="The code provided was incorrect. "
                                         "Make sure that the url was "
                                         "copied correctly.")
@app.route("*")
def page404():
    print("ya so like")
    #return render_template("404page.html")
