from flask import Flask, request, redirect, render_template, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

#Note: the connection string after :// contains the following info:
#
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'hoursewhisperralphsoupgoose'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(250))
    body = db.Column(db.String(10000))
   
    
    def __init__(self, blog_title, body):
        self.blog_title = blog_title
        self.body = body
        
            

@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    if blogs:
        return render_template('blog.html', blogs = blogs)
    else:
        flash("Get it started, make a new post")    
        return render_template('newpost.html')        


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
            #return redirect('/blog?id={}'.format(new_blog.id)) 
            return render_template('blog.html', new_blog = new_blog)
    else:     
        return render_template('newpost.html',title="Blog posts" )

@app.route('/individual_post', methods=['GET','POST'])
def individual_post():
    link = int(request.args.get('id'))
    blogger = Blog.query.get(link)
    
    #return redirect('/individual_post?id={}'.format(link))
    return render_template('individual_post.html', blogger=blogger)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    

    blogs = Blog.query.all()

    return render_template('blog.html', blogs=blogs)


@app.route('/delete-entry', methods=['POST'])
def delete_entry():

    blog_id = int(request.form['blog-id'])
    body = Blog.query.get(blog_id)
    blog_title = Blog.query.get(blog_id)

    db.session.delete(blog_title)
    db.session.delete(body)
    db.session.commit()

    return redirect('/blog')

def post_verify(text):
    if text != "":
        return True
    else:
        return False

if __name__ == '__main__':
    app.run()
