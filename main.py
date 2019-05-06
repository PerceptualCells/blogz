from flask import Flask, request, redirect, render_template, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

#Note: the connection string after :// contains the following info:

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'uptightmongooserunsfar'



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_title = db.Column(db.String(250))
    body = db.Column(db.String(10000))
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
   
    
    def __init__(self, owner, blog_title, body):
        self.owner = owner
        self.blog_title = blog_title
        self.body = body
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), unique=True)
    pseudo_name = db.Column(db.String(35))
    hashed_pass = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, name, pseudo_name, hashed_pass):
        self.name = name
        self.pseudo_name = pseudo_name
        self.hashed_pass = hashed_pass


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'singleuser']
    if request.endpoint not in allowed_routes and 'id' not in session:
        return redirect('/login')

@app.route('/singleuser', methods=['GET'])
def singleuser():
    link = int(request.args.get('id'))
    blogger = User.query.get(link)

    return render_template('singleuser.html', blogger = blogger)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        body = request.form['plaintext']

        if post_verify(blog_title) == False and post_verify(body) == True:
            flash("Missing blog title")
            return render_template('newpost.html',title="Blog posts" )

        elif post_verify(blog_title) == True and post_verify(body) == False:
            flash("Missing blog body")
            return render_template('newpost.html',title="Blog posts" )

        elif post_verify(blog_title) == False and post_verify(body) == False:
            flash("Empty post, You need a title and a body to post here.")    
            return render_template('newpost.html',title="Blog posts" )

        else:        
            new_blog = Blog(blog_title, body)
        
            db.session.add(new_blog)
            db.session.commit()
            holder = Blog.query.get(new_blog.id)
             
            return render_template('newpost.html', new_blog = new_blog)
    else:     
        return render_template('newpost.html',title="Blog posts" )

@app.route('/individual_post', methods=['GET','POST'])
def individual_post():
    link = int(request.args.get('id'))
    blogger = Blog.query.get(link)

    return render_template('individual_post.html', blogger=blogger)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    use = session['id']

    blogs = Blog.query.filter_by(owner_id=use).all()

    return render_template('blog.html', blogs=blogs)

'''
@app.route('/delete-entry', methods=['POST'])
def delete_entry():

    blog_id = int(request.form['blog-id'])
    body = Blog.query.get(blog_id)
    blog_title = Blog.query.get(blog_id)

    db.session.delete(blog_title)
    db.session.delete(body)
    db.session.commit()

    return redirect('/blog')
'''
@app.route('/signup', methods=['POST', 'GET'])  
def signup():

    if request.method == 'POST':
        name = request.form['name']
        pseudo_name = request.form['pseudo_name']
        hashed_pass = request.form['hashed_pass']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(name=name).first()
        if not existing_user:
            new_user = User(name, pseudo_name, hashed_pass)
            db.session.add(new_user)
            db.session.commit()
            session['id'] = id
            return redirect('/')

        else:
            # TODO - user better response messaging
            flash("This user name already exists... womp womp")
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        hashed_pass = request.form['hashed_pass']
        user = User.query.filter_by(name=name).first()
        if user and user.hashed_pass == hashed_pass:
            session['id'] = id
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout', methods=['POST',])
def logout():

    del session['id']
    return redirect('/')

            

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    #if users:
    return render_template('index.html', users = users)
    #else:
    #    flash("Get it started, be the first & make a new account")    
    #    return render_template('register.html')        


def post_verify(text):
    if text != "":
        return True
    else:
        return False
'''
def validate(usr_name, password1, password2):
    
    #initial simple validation, confirm base requirments...
    #check user name and password fields  then check e-mail
    #error messages
    usr_error = ""
    p_error = ""
    p2_error = ""
    
    # Validate Username
    if usr_name == password1:
        usr_error = "your username and password may not be the same"
        p_error= "your username and password may not be the same"

    
        
    if not length(usr_name):
        usr_error = "Your username is too long or too short"

    if  not usr_name.isalnum():
        usr_error = "You have invalid characters in your username"

    if not space(usr_name):
        usr_error = "you have spaces in your username"

    if not has_val(usr_name):
        usr_error = "The username field cannot be blank :}"
    # Validate Password
    

    if password1 != password2:
        p_error = "Your passwords must match"
        p2_error = "Your passwords must match"

    if not space(password1):
        p_error = "passwords cannot have spaces"
   
    if not length(password1):
        p_error = "password length outside of range (3 < password < 20)"
    

    if not password1.isalnum():
        p_error = "you have unaccepable symbols in your password"

    if not has_val(password1) or not has_val(password2):
        p_error ="You have left a necessary field blank"    

    # validate username
    if has_val(email):
        if not email_chk(email):
            email_error = "this is not a valid email address"
    else:
        email_error = ""    


    #TEST RETURN
    if usr_error=="" and p_error == "" and p2_error == "" and email_error == "":
        #return render_template("welcome.html",
        #   user_name = usr_name)

        return True
    else:
        flash(p_error, name_error, p2_error, usr_error)
        return render_template("signup.html", usr_error = usr_error,
            p_error = p_error,
            user_name = usr_name,
            e_error = email_error,
            p2_error = p2_error)    

def has_val(text):
    if text == "" or text.strip() == "":
        return False
    else:
        return True    

def space(text):
    sp = " "
    if sp not in text:
        return True
    else:
        return False

def length(text):
    if len(text) >= 3 and len(text) <= 20:
        return True
    else:
        return False

def email_chk(text):
    if space(text) and length(text):
        if "@" in text and "." in text:
            return True
    else:
        return False            
'''
if __name__ == '__main__':
    app.run()
