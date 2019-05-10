from flask import Flask, request, redirect, render_template, session, flash
#from datetime import datetime
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
    #pub_date = db.Column(db.DateTime, nullable=False,
    #    default=datetime.utcnow)
   
    
    def __init__(self, owner, blog_title, body):
        self.owner = owner
        self.blog_title = blog_title
        self.body = body
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(35), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    #if 'id' in session and request.endpoint is 'login':
    #    msg = 'already logged in'

    allowed_routes =['login', 'blog', 'individual_post', 'signup', 'index']    
    if request.endpoint not in allowed_routes and 'id' not in session:
        return redirect('/login')


@app.route('/singleuser', methods=['GET'])
def singleuser():
    
    link = int(request.args.get('id'))
    blogger = User.query.get(link)

    return render_template('singleuser.html', blogger = blogger, sess=session.get('id',''))

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    

    if request.method == 'POST':
        own = session['id']
        owner_id = User.query.get(own)
        blog_title = request.form['title']
        body = request.form['body']

        if post_verify(blog_title) == False and post_verify(body) == True:
            flash("Missing blog title")
            return render_template('newpost.html',title="Blog posts" )

        elif post_verify(blog_title) == True and post_verify(body) == False:
            flash("Missing blog body")
            return render_template('newpost.html',title="Blog posts" )

        elif post_verify(blog_title) == False and post_verify(body) == False:
            flash("Empty post, You need a title and a body to post here.")    
            return render_template('newpost.html',title="Blog posts", sess=session.get('id',''))

        else:        
            new_blog = Blog(owner_id, blog_title, body)
            db.session.add(new_blog)
            db.session.commit()
            holder = Blog.query.get(new_blog.id)
             
            return render_template('newpost.html', new_blog = new_blog, sess=session.get('id',''))
    else:     
        return render_template('newpost.html',title="Blog posts", sess=session.get('id',''))

@app.route('/individual_post', methods=['GET','POST'])
def individual_post():
   


    link = int(request.args.get('id'))
    blogger = Blog.query.get(link)

    return render_template('individual_post.html', blogger=blogger, sess=session.get('id',''))


@app.route('/blog', methods=['POST', 'GET'])
def blog():
      
    
    blogs = Blog.query.all()

    return render_template('blog.html', blogs=blogs, sess=session.get('id',''))

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
    usr_error = ""
    p_error = ""
    p2_error = ""


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data
        # - check for blank values
        # - check for lengths
        # - check for spaces

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            # TODO - user better response messaging
            usr_error = "This user name already exists... womp womp"
            return render_template('signup.html', usr_error = usr_error, sess=session.get('id',''))
        # call out this error first    

        if has_val(username) or has_val(password) or has_val(verify):
                usr_error = "a necessary field has been left blank"
                return render_template('signup.html', usr_error = usr_error, sess=session.get('id',''))    
        # make sure that the fields are all filled second       

                   
        if len(username) <= 3:
            usr_error = "Username must be longer than 3 characters"
    
        if username == password:
            p_error = "your password cannot be the same as a username"

        if password != verify:
            p2_error = "your passwords do not match"
        if len(password) <= 3:
            p_error = "passwords must be longer than 3 characters"            

                
        if p_error == "" and p2_error == "" and usr_error == "":    
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['id'] = new_user.id
            return redirect('/newpost')
        else:
            return render_template('signup.html', usr_error = usr_error, p_error = p_error, p2_error = p2_error, sess=session.get('id',''))
    

    return render_template('signup.html', sess=session.get('id',''))


@app.route('/login', methods=['POST','GET'])
def login():
    error = ""
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user.username == username and user.password == password:
            session['id'] = user.id
            flash("Logged in")
            return redirect('/newpost')
        else:
            error = 'Username or password is incorrect or user does not exist'
            return render_template('login.html', error = error)

    return render_template('login.html', sess=session.get('id',''))

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['id']
    return redirect('/')

            

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    #if users:
    return render_template('index.html', users = users, sess=session.get('id',''))
    #else:
    #    flash("Get it started, be the first & make a new account")    
    #    return render_template('register.html')        


def post_verify(text):
    if text != "":
        return True
    else:
        return False


def has_val(text):
    if text == "" or text.strip() == "":
        return True
    else:
        return False    

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

        

if __name__ == '__main__':
    app.run()
