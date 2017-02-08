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

from google.appengine.ext import db

# jinja setup
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# core class to handle page creation and display
class MainHome(Handler):
    def get(self):
        self.render("blog.html")

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
            self.redirect("/")
        else:
            error = "<strong>Error:</strong> We can't create a post without a post title <u>and</u> post content. Please try again."
            self.render_newpost(title, post, error)

class EachPost(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    creation = db.DateTimeProperty(auto_now_add = True)

class FullPost(Handler):
    pass

app = webapp2.WSGIApplication([
    ('/', MainHome),
    ('/newpost', NewPost),
    ('/fullpost', FullPost)
], debug=True)
