from flask import Flask, render_template, redirect, request, session, url_for, flash
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta  # To set session lifetime

app = Flask(__name__)

# Set the secret key to manage session cookies
app.secret_key = "secret_key"  # Replace this with a more secure key

# Session to expire in 3 hours for testing purposes
app.permanent_session_lifetime = timedelta(hours=3)

# Configure the database
global_db = SQL("sqlite:///global.db")
ed_db = SQL("sqlite:///education.db")

# Create users table if it doesn't exist
global_db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, hash TEXT)")

@app.route("/")
def home():
    return render_template("home.html", field_name="SARTHI HUB")


@app.route("/govtScheme")
def govtScheme():
    authenticated = "user_id" in session
    return render_template("govtScheme.html", login_req = True, authenticated=authenticated, field_name="Government Schemes")

@app.route("/con")
def con():
    return render_template("Contact.html")


@app.route("/ag_s")
def  ag_s():
    return render_template("Allservice.html")


@app.route("/healthcare")
def healthcare():
    authenticated = "user_id" in session
    return render_template("healthcare.html", login_req = True, authenticated=authenticated, field_name="Healthcare")

@app.route("/agriculture")
def agri():
    authenticated = "user_id" in session
    return render_template("agriculture.html", login_req = True,authenticated=authenticated, field_name="Agriculture")

# Subpage features
@app.route("/gov_faq")
def gov_faq():
    return render_template("gov_scheme_faq.html")


@app.route("/agf")
def agf():
    return render_template("agriculture_guidance.html")

@app.route("/hgf")
def hgf():
    return render_template("medical_faq.html")



# agriculture chatbot
@app.route("/agri_chatbot")
def ag_chat():
    return render_template("agri_chatbot.html")

# faq career
@app.route("/career")
def careeer():
    return render_template("career_guidance.html")


# consultation
@app.route("/consultation")
def reg():
    authenticated = "user_id" in session
    return render_template("registration_form.html", button="Apply for consultation", authenticated=authenticated)


# bed booking
@app.route("/book_bed")
def bed():
    authenticated = "user_id" in session
    return render_template("registration_form.html", button="Apply for bed", authenticated=authenticated)






""" Education sector """

@app.route("/education")
def education():
    authenticated = "user_id" in session
    return render_template("education/education.html", login_req = True, authenticated=authenticated, field_name="Education materials")


# Subpage features
@app.route("/cgf")
def cgf():
    return render_template("carrier_guidance_faq.html")


# Login route
@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Login for students 
        if user_type == 'student':
            # Query the database to find the student with matching email
            student = ed_db.execute("SELECT * FROM students WHERE email = ?", email)

            # Check if student exists and if the password is correct
            if len(student) == 1 and check_password_hash(student[0]['password_hash'], password):
                # Login successful, create session
                session['user_id'] = student[0]['id']
                session['user_type'] = 'student'
                flash('Logged in successfully as Student!', 'success')
                return redirect('/education') # redirect to the education home 
            else:
                flash('Invalid email or password. Please try again.', 'danger')

        # Login for teachers
        elif user_type == 'teacher':
            # Query the database to find the teacher with matching email
            teacher = ed_db.execute("SELECT * FROM teachers WHERE email = ?", email)

            # Check if teacher exists and if the password is correct
            if len(teacher) == 1 and check_password_hash(teacher[0]['password_hash'], password):
                # Login successful, create session
                session['user_id'] = teacher[0]['id']
                session['user_type'] = 'teacher'
                flash('Logged in successfully as Teacher!', 'success')
                return redirect('/teacher_dashboard')  # Redirect to the education home
            else:
                flash('Invalid email or password. Please try again.', 'danger')


    return render_template('education/education_login.html', user_type=user_type)

    
# Registration route
@app.route('/register/<user_type>', methods=['GET', 'POST'])
def register(user_type):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        if user_type == 'student':
            # Insert student into the students table
            ed_db.execute("INSERT INTO students (name, email, password_hash) VALUES (?, ?, ?)",
                          name, email, hashed_password)

            flash('Student registration successful! You can now log in.', 'success')

        elif user_type == 'teacher':
            field = request.form.get('field')  # primary, secondary, skills
            class_specialization = request.form.get('class_specialization')  # free-text for class
            subject_specialization = request.form.get('subject_specialization')  # free-text for subject
            experience = request.form['experience']

            # Insert teacher into the teachers table
            ed_db.execute("""
                INSERT INTO teachers (name, email, password_hash, experience, field, class_specialization, subject_specialization)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, 
            name, email, hashed_password, experience, field, class_specialization, subject_specialization)

            flash('Teacher registration successful! You can now log in.', 'success')

        return redirect(url_for('login', user_type=user_type))

    return render_template('education/education_register.html', user_type=user_type)


# logout route
@app.route('/logout')
def logout():
    # Clear the session data to log out the user
    session.clear()
    return redirect('/education')  # Default redirect to student login page


# teacher dashboard route
@app.route('/teacher_dashboard', methods=['GET'])
def teacher_dashboard():
    teacher_id = session.get('user_id')

    teacher_name = ed_db.execute("select name from teachers where id = ?;", teacher_id)
    
    # Fetch filter parameters
    class_filter = request.args.get('class')
    subject_filter = request.args.get('subject')
    unit_filter = request.args.get('unit')

    # Base query for fetching teacher's content
    query = """
        SELECT c.id AS class_id, c.class_name, s.subject_name, u.unit_name, t.topic_name, 
               ct.video_path, ct.pdf_path, ct.id, ct.updated_at
        FROM content ct
        JOIN topic t ON ct.topic_id = t.id
        JOIN unit u ON t.unit_id = u.id
        JOIN class c ON u.class_id = c.id
        JOIN subject s ON c.subject_id = s.id
        WHERE ct.teacher_id = ?
    """
    params = [teacher_id]

    # Add filters dynamically to the query
    if class_filter:
        query += " AND c.id = ?"
        params.append(class_filter)
    if subject_filter:
        query += " AND s.id = ?"
        params.append(subject_filter)
    if unit_filter:
        query += " AND u.id = ?"
        params.append(unit_filter)

    # Add order by clause for updated_at
    query += " ORDER BY ct.updated_at DESC"

    # Execute the query with filters applied
    contents = ed_db.execute(query, tuple(params))

    # Fetch all classes, subjects, and units for filters (use distinct to avoid duplicates)
    classes = ed_db.execute("SELECT DISTINCT id, class_name FROM class")
    subjects = ed_db.execute("SELECT DISTINCT id, subject_name FROM subject")
    units = ed_db.execute("SELECT DISTINCT id, unit_name FROM unit")

    return render_template('education/teacher_dashboard.html', field_name=teacher_name[0]["name"], contents=contents, classes=classes, subjects=subjects, units=units)


# add content route
@app.route('/add_content', methods=['GET', 'POST'])
def add_content():
    # Handle the POST request (form submission)
    if request.method == 'POST':
        # Get the form data
        content_title = request.form.get('content_title')
        content_description = request.form.get('content_description')
        video_path = request.form.get('video_path')
        pdf_path = request.form.get('pdf_path')
        subject_id = request.form.get('subject_id')
        class_id = request.form.get('class_id')
        unit_id = request.form.get('unit_id')
        topic_id = request.form.get('topic_id')
        teacher_id = session.get('user_id')
        
        # Insert new subject, class, unit, or topic if needed
        if request.form.get('new_subject'):
            subject_name = request.form.get('new_subject')
            subject_id = ed_db.execute('INSERT INTO subject (subject_name) VALUES (?)', subject_name)

        if request.form.get('new_class'):
            class_name = request.form.get('new_class')
            class_id = ed_db.execute('INSERT INTO class (class_name, subject_id) VALUES (?, ?)', class_name, subject_id)

        if request.form.get('new_unit'):
            unit_name = request.form.get('new_unit')
            unit_id = ed_db.execute('INSERT INTO unit (unit_name, class_id) VALUES (?, ?)', unit_name, class_id)

        if request.form.get('new_topic'):
            topic_name = request.form.get('new_topic')
            topic_id = ed_db.execute('INSERT INTO topic (topic_name, unit_id) VALUES (?, ?)', topic_name, unit_id)

        # Insert the new content into the content table
        ed_db.execute('''
            INSERT INTO content (content_title, content_description, video_path, pdf_path, topic_id, teacher_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', content_title, content_description, video_path, pdf_path, topic_id, teacher_id)

        # Flash message and redirect after successful content addition
        flash("Content added successfully!")
        return redirect(url_for('teacher_dashboard'))

    # Handle the GET request (display the form)
    data = ed_db.execute('''
        SELECT s.id as subject_id, s.subject_name, 
               c.id as class_id, c.class_name,
               u.id as unit_id, u.unit_name,
               t.id as topic_id, t.topic_name
        FROM subject s
        LEFT JOIN class c ON s.id = c.subject_id
        LEFT JOIN unit u ON c.id = u.class_id
        LEFT JOIN topic t ON u.id = t.unit_id
    ''')

    # Parse the result to group subjects, classes, units, and topics appropriately
    subjects, classes, units, topics = {}, {}, {}, {}
    for row in data:
        subjects[row['subject_id']] = row['subject_name']
        classes[row['class_id']] = row['class_name']
        units[row['unit_id']] = row['unit_name']
        topics[row['topic_id']] = row['topic_name']

    return render_template('education/add_content.html', subjects=subjects, classes=classes, units=units, topics=topics)


# delete content route
@app.route('/delete_content/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    if 'user_id' not in session:
        return redirect('/login')

    # Delete content from the database
    ed_db.execute("DELETE FROM content WHERE id = ?", (content_id,))
    flash('Content deleted successfully.', 'success')
    return redirect('/teacher_dashboard')


if __name__ == "__main__":
    app.run(debug=True)
