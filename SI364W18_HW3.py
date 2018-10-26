## SI 364 - Winter 2018
## HW 3

####################
## Import statements
####################

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import re

############################
# Application configurations
############################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string from si364'
## TODO 364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME
## Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
## Provided:
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/sindhgirHW3"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################

db = SQLAlchemy(app) # For database use

#########################
#########################
######### Everything above this line is important/useful setup,
## not problem-solving.##
#########################
#########################

#########################
##### Set up Models #####
#########################

## TODO 364: Set up the following Model classes, as described, with the respective fields (data types).

## The following relationships should exist between them:
# Tweet: User - Many:One
# - Tweet
class Tweet (db.Model):
    __tablename__= "tweets"
    tweetId = db.Column (db.Integer, primary_key=True)
    tweetText = db.Column (db.String (280))
    user_id = db.Column (db.Integer, db.ForeignKey("users.userId"))
    def __repr__(self):
        return "{} (ID: {})".format(self.tweetText, self.tweetId)

#- User
class User (db.Model):
    __tablename__= "users"
    userId = db.Column (db.Integer, primary_key=True)
    userUsername = db.Column (db.String (64), unique= True)
    userDisplay_name = db.Column (db.String (124))
    usertweet_relationship = db.relationship ("Tweet", backref = "User")
    def __repr__(self):
        return "{} | ID: {}".format(self.userUsername, self.userId)
# ---- Line to indicate relationship between Tweet and User tables (the 1 user: many tweets relationship)

########################
##### Set up Forms #####
########################

# TODO 364: Fill in the rest of the below Form class so that someone running this web app will be able to fill in information about tweets they wish existed to save in the database:

# HINT: Check out index.html where the form will be rendered to decide what field names to use in the form class definition

class UserTweetsForm(FlaskForm):
    text=StringField ("Enter text:", validators=[Required(280)])
    username=StringField ("Enter user name:", validators=[Required(64)])
    display_name=StringField ("Enter display name:", validators=[Required()])
    submit=SubmitField ("Submit")

#TODO 364: Set up custom validation for this form such that:

    def validate_username(self,field):
        username = field.data 
        if username [0] == "@":
            raise ValidationError ("Twitter username cannot start with an @ sign")

    def validate_display_name(self, field):
        displaydata = field.data 
        if len (displaydata.split(" ")) < 2:
            raise ValidationError ("Display name must be at least 2 words")

#TODO 364: Make sure to check out the sample application linked in the readme to check if yours is like it!

###################################
##### Routes & view functions #####
###################################

## Error handling routes - PROVIDED

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#############
## Main route
#############

## TODO 364: Fill in the index route as described.

# A template index.html has been created and provided to render what this route needs to show -- YOU just need to fill in this view function so it will work.
# Some code already exists at the end of this view function -- but there's a bunch to be filled in.
## HINT: Check out the index.html template to make sure you're sending it the data it needs.
## We have provided comment scaffolding. Translate those comments into code properly and you'll be all set!

# NOTE: The index route should:
# - Show the Tweet form.
# - If you enter a tweet with identical text and username to an existing tweet, it should redirect you to the list of all the tweets and a message that you've already saved a tweet like that.
# - If the Tweet form is entered and validates properly, the data from the form should be saved properly to the database, and the user should see the form again with a message flashed: "Tweet successfully saved!"
# Try it out in the sample app to check against yours!

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserTweetsForm()
    num_tweets=len(Tweet.query.all())
    if form.validate_on_submit():
        username=form.username.data
        text=form.text.data 
        display_name=form.display_name.data

        user = User.query.filter_by(userUsername=username).first()
        if not user: 
            user=User(userUsername=username, userDisplay_name=display_name)
            db.session.add(user)
            db.session.commit()  

        check_tweet = Tweet.query.filter_by(tweetText=text,user_id=user.userId).first()
        if check_tweet:  
            flash("Tweet exists")
            return redirect(url_for("see_all_tweets"))
        else: 
            text_userid=Tweet(tweetText=text, user_id=user.userId)
            db.session.add(text_userid)
            db.session.commit() 
            flash ("Tweet is successfully added")
            return redirect(url_for("index"))

#PROVIDED: If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html',form=form, num_tweets=num_tweets) 
#TODO 364: Add more arguments to the render_template invocation to send data to index.html

@app.route('/all_tweets')
def see_all_tweets():
    all_tweets=[]
    alltweets_query= Tweet.query.all()
    for x in alltweets_query:
        userid_from_tweet = x.user_id
        user_row = User.query.filter_by(userId=userid_from_tweet).first()
        userrow_username = user_row.userUsername
        all_tweets.append((x.tweetText, userrow_username))
    return render_template ("all_tweets.html", all_tweets=all_tweets)

# #TODO 364: Fill in this view function so that it can successfully render the template all_tweets.html, which is provided.
# #HINT: Careful about what type the templating in all_tweets.html is expecting! It's a list of... not lists, but...
# #HINT #2: You'll have to make a query for the tweet and, based on that, another query for the username that goes with it...

@app.route('/all_users')
def see_all_users():
    allusers_query = User.query.all()
    return render_template ("all_users.html", users=allusers_query)

# # TODO 364
# # Create another route (no scaffolding provided) at /longest_tweet with a view function get_longest_tweet (see details below for what it should do)

# # TODO 364
# # Create a template to accompany it called longest_tweet.html that extends from base.html.
# # use regular expression pattern matching to find the 

@app.route ('/longest_tweet')
def get_longest_tweet():
    longesttweet_query = Tweet.query.all()
    longestother_query = User.query.all()
    longest_tweet = ""
    longest_tweet_length = 0
    temp_tweet  = ""
    newlongest_tweet = ""
    for x in longesttweet_query:
        userid_from_tweet = x.user_id
        temp_tweet = x.tweetText
        temp_tweet = temp_tweet.replace(" ", "")
        if len(temp_tweet) > longest_tweet_length:
            longest_tweet_length = len(temp_tweet) 
            newlongest_tweet = temp_tweet
            user_row = User.query.filter_by(userId=userid_from_tweet).first()
            user_row_username = user_row.userUsername
            user_row_displayname = user_row.userDisplay_name
    return render_template ("longest_tweet.html", newlongest_tweet = newlongest_tweet, username = user_row_username, displayname = user_row_displayname)

#NOTE:
# This view function should compute and render a template (as shown in the sample application) that shows the text of the tweet currently saved in the database which has the most NON-WHITESPACE characters in it, and the username AND display name of the user that it belongs to.
# NOTE: This is different (or could be different) from the tweet with the most characters including whitespace!
# Any ties should be broken alphabetically (alphabetically by text of the tweet). HINT: Check out the chapter in the Python reference textbook on stable sorting.
# Check out /longest_tweet in the sample application for an example.

# HINT 2: The chapters in the Python reference textbook on:
# - Dictionary accumulation, the max value pattern
# - Sorting
#may be useful for this problem!

if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual