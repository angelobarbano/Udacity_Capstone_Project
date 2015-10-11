
import webapp2
import jinja2
import os
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


class Post(ndb.Model):
    author = ndb.StringProperty(indexed=True)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class CommentHandler(Handler):
    def get(self):
        wall_name = self.request.get('wall_name',DEFAULT_WALL)
        posts_query = Post.query(ancestor = wall_key(wall_name)).order(-Post.date)
        posts =  posts_query.fetch()
        self.render("wall.html", posts= posts, wall_name= urllib.quote_plus(wall_name))

class PostWall(Handler):
    def post(self):
        wall_name = self.request.get('wall_name',DEFAULT_WALL)
        post = Post(parent= wall_key(wall_name))
        post.author = self.request.get('author')
        post.content = self.request.get('content')
        
        if post.content == '' or post.author == '':
            self.redirect('/blank')
        else:
            post.put()
            self.redirect('/comment')

class InvalidHandler(Handler):
    def get(self):
        self.render("blank.html")
        

app = webapp2.WSGIApplication([('/', MainHandler), ('/notes', NoteHandler), ('/comment', CommentHandler), ('/sign', PostWall)
, ('/new', New_notesHandler),('/blank', InvalidHandler)], debug=True)
