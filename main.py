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
import time
import math
from google.appengine.ext import db

# jinja setup
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

# function to engage pagination
def get_posts(limit, offset):
    pass
    # get the count of all available posts
    # set the limit to 5 results per page
    # figure out what page we're currently on (to set the offset)
    # set the offset to show the pertinent posts
    # pass the page #s (current and total) to the render engine
    # pass the posts to the render engine
    # render the page and footer pagination as necessary

# nice Handler to make displaying template pages easier and cleaner
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# class to handle the creation and display of the main and addtl blog page(s)
class MainHome(Handler):
    def get(self):
        thisPage = int(self.request.get('page', default_value="1"))
        page_offset = 5 * (thisPage - 1)
        queryString = "SELECT * FROM EachPost ORDER BY creation DESC LIMIT 5 OFFSET " + str(page_offset)
        allPosts = db.GqlQuery(queryString)
        allSubs = allPosts.count()
        pageCount = allSubs // 5 + (allSubs % 5 > 0)
        if pageCount < 1:
            pageCount = 1
        error = ""
        if thisPage > pageCount:
            thisPage = 0
            pageCount = 0
            error = "We're sorry, this page does not exist. Please try again."
        self.render("blog.html", post_list = allPosts, allSubs = allSubs, curPg = thisPage, allPg = pageCount, error = error)

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
            time.sleep(1)
            self.redirect("/blog/{}".format(str(id)))
        else:
            error = "<strong>Error:</strong> We can't create a post without a post title <u>and</u> post content. Please try again."
            self.render_newpost(title, post, error)

# class to handle writing new posts into the database, and time stamping them
class EachPost(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    creation = db.DateTimeProperty(auto_now_add = True)

# class to display each individual (full) post on it's own page
class FullPost(Handler):
    def get(self, id):
        thisPost = EachPost.get_by_id(int(id))
        if thisPost:
            self.render("fullpost.html", thisPost = thisPost, error="")
        else:
            error = "We're sorry, this post does not exist. Please try again."
            self.render("fullpost.html", thisPost = "", title = "", post = "", creation = "", error = error)


# this makes unicorns cry. Just kidding, it makes the magic happen.
app = webapp2.WSGIApplication([
    ('/', MainHome),
    ('/blog', MainHome),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', FullPost)
], debug=True)
