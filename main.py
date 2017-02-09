#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import jinja2
import os
import datetime

# import the database functionality
from google.appengine.ext import db

# jinja setup
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

# function to engage pagination
def get_posts(limit, offset):
    pass

# nice Handler snippet to make displaying template pages significantly easier and cleaner
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# class to handle the main page creation and display
class MainHome(Handler):
    def get(self):
        allPosts = db.GqlQuery("SELECT * FROM EachPost ORDER BY creation DESC LIMIT 5")
        # disabled for now, until we can figure out how to manipulate this one section
        # for post in allPosts:
        #     if len(post.post) > 150:
        #         post.post[:150] + '...'
        #         visiWhat = "block"
        #     else:
        #         visiWhat = "none"
        # -- visiSpan = visiWhat also removed from render, so it doesn't break
        self.render("blog.html", post_list = allPosts)

# class to handle new post creation and error checking
class NewPost(Handler):
    def render_newpost(self, title = "", post = "", error = ""):
        self.render("newpost.html", title = title, post = post, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            x = EachPost(title = title, post = post)
            x.put()
            id = x.key().id()
            self.redirect("/blog/{}".format(str(id)))
        else:
            error = "<strong>Error:</strong> We can't create a post without a post title <u>and</u> post content. Please try again."
            self.render_newpost(title, post, error)

# class to handle writing new posts into the database, and time stamping them
class EachPost(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    creation = db.DateTimeProperty(auto_now_add = True)

# class to display each individual (full) post on it's own page, if the user chooses to do so
class FullPost(webapp2.RequestHandler):
    def get(self, id):
        thisPost = EachPost.get_by_id(int(id))
        x = jinja_env.get_template("fullpost.html")
        if thisPost:
            postContent = x.render(thisPost = thisPost)
            self.response.write(postContent)
        else:
            error = "<strong>Error:</strong> Sorry, this post does not seem to exist. Please try again."
            postContent = x.render(post = "", title = "", error = error)
            self.response.write(postContent)


# this makes the magic happen. Just kidding, it makes unicorns cry.
app = webapp2.WSGIApplication([
    ('/', MainHome),
    ('/blog', MainHome),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', FullPost)
], debug=True)
