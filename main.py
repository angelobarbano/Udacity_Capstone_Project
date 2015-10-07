
import webapp2
import jinja2
import os
import cgi
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t=JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
	def get(self):
	    self.render("welcome.html")

class NoteHandler(Handler):
    def get(self):
        self.render("index.html")

class New_notesHandler(Handler):
    def get(self):
        self.render("new_notes.html")

DEFAULT_WALL = 'Public'

def wall_key(wall_name=DEFAULT_WALL):
    return ndb.Key('Wall', wall_name)

class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Post(ndb.Model):
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class CommentHandler(Handler):
    def get(self):
        wall_name = self.request.get('wall_name',DEFAULT_WALL)
        
        posts_query = Post.query(ancestor = wall_key(wall_name)).order(-Post.date)
        posts =  posts_query.fetch()
        
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        
       
        
        self.render("wall.html", user=user, posts= posts, wall_name= urllib.quote_plus(wall_name), url= url, url_linktext= url_linktext)

class PostWall(Handler):
    def post(self):
        wall_name = self.request.get('wall_name',DEFAULT_WALL)
        post = Post(parent=wall_key(wall_name))
        if users.get_current_user():
            post.author = Author(
            identity=users.get_current_user().user_id(),
            name=users.get_current_user().nickname(),
            email=users.get_current_user().email())
        else:
            post.author = Author(
            name='anonymous@anonymous.com',
            email='anonymous@anonymous.com')


        post.content = self.request.get('content')
        post.put()
        self.redirect('/comment')

app = webapp2.WSGIApplication([('/', MainHandler), ('/notes', NoteHandler), ('/comment', CommentHandler), ('/sign', PostWall)
, ('/new', New_notesHandler)], debug=True)
