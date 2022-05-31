#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm, Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
 


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:mungaifahm1@localhost:5432/project_fyyur'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120)) 
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column("genres", db.ARRAY (db.String), nullable=False)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
      return f'<Venue ID: {self.id}, name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY (db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.Boolean, default=False)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    show = db.relationship('Show', backref='artists', lazy=True)



    def __repr__(self):
      return f'<Artist ID: {self.id}, name: {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ ='shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id =db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id =db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.Date, nullable=False)

def __repr__(self):
  return f'<Show ID: {self.id}, artist_id{self.artist_id}, venue_id{self.venue_id}>'



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
  artists = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  areas = db.session.query(Venue.id, Venue.city, Venue.name, Venue.state).distinct(Venue.id, Venue.city, Venue.state)

  data = []
  upcoming_shows= []

  for area in areas:    
        upcoming_query = db.session.query(Show).join(Venue).filter(Show.artist_id == Artist.id).filter(Show.start_time > datetime.now()).all()
        upcoming_shows.append(upcoming_query)
        venue_unit = {
            "id": area.id,
            "name": area.name,
            "upcoming_shows_count": len(upcoming_shows)
        } 
        venue_location = {
          'city':area.city,
          'state':area.state,
          'venues': [venue_unit] }
        data.append(venue_location)
  return render_template('pages/venues.html', areas=data);
    

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  #query venue class for the search term
  search_result = Venue.query.filter(Venue.name.ilike('%'+search_term+'%', '')).all()
  count = len(search_result)
  data =[]

  for venue in search_result:
        venue_unit = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(str
             (Show.query.filter(Venue.id == venue.id) .filter(Show.start_time > datetime.now()))
            )
        }
        data.append(venue_unit)

        response= {
          "count":count,
          "data": data
        }
  

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  retrievevenue = Venue.query.get(venue_id)
  error=False

  try:

    # get past shows
      past_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
      past_shows = []
      for show in past_query:
        past_shows.append({
          'artist_id': show.artists.id,
          'artist_name': show.artists.name,
          'artist_image_link': show.artists.image_link,
          'start_time':show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
           })


        # get future shows
      upcoming_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()
      upcoming_shows = []
      for show in upcoming_query:
            upcoming_shows.append({
            'artist_id': show.artists.id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time':show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

            })
            
      data={
                "id": retrievevenue.id,
                "name": retrievevenue.name,
                "genres":retrievevenue.genres,
                "address": retrievevenue.address,
                "city":retrievevenue.city,
                "state": retrievevenue.state,
                "phone": retrievevenue.phone,
                "website": retrievevenue.website,
                "facebook_link": retrievevenue.facebook_link,
                "seeking_talent": retrievevenue.seeking_talent,
                "seeking_description":retrievevenue.seeking_description,
                "image_link": retrievevenue.image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows)
            }
  except:
    print(sys.exc_info())
    
  if error:
    flash('ERROR!!')
  else:
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  
 
    error = False
    form = VenueForm()

    try:

        if form.validate_on_submit():
          newVenue = Venue(

            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data)
          db.session.add(newVenue)
          db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('error has occured')
    finally:
        db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] +' was successfully listed!')
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    venue = Venue.query.filter_by(venue_id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return venue

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data= Artist.query.with_entities(Artist.id, Artist.name).limit(3).all()



  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  #query atist class for the search term
  if search_term:
    search_result = Artist.query.filter(Artist.name.ilike('%'+search_term+'%', '')).all()
    count = len(search_result)

  data =[]

  for artist in search_result:
        artist_unit = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(str
             (Show.query.filter(Artist.id == artist.id) 
             .filter(Show.start_time > datetime.now()))
            )
        }
        data.append(artist_unit)

        response= {
          "count":count,
          "data": data
        }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  

  retrieveartist = Artist.query.get(artist_id)
  error=False

  try:

    # get past shows
      past_query = db.session.query(Show).join(Artist).filter(Show.venue_id==artist_id).filter(Show.start_time < datetime.now()).all()
      past_shows = []
      for show in past_query:
        past = {
          'venue_id': show.venues.id,
          'venue_name': show.venues.name,
          'venue_image_link': show.venues.image_link,
          'start_time':show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
           }
        past_shows.append(past)


        # get future shows
      upcoming_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()
      upcoming_shows = []
      for show in upcoming_query:
        upcoming={

          'venue_id': show.venues.id,
          'venue_name': show.venues.name,
          'venue_image_link': show.venues.image_link,
          'start_time':show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
           }
           
        upcoming_shows.append(upcoming)
            
      data={
                "id": retrieveartist.id,
                "name": retrieveartist.name,
                "city": retrieveartist.city,
                "state": retrieveartist.state,
                "phone": retrieveartist.phone,
                "genres": retrieveartist.genres,
                "image_link": retrieveartist.image_link,
                "facebook_link": retrieveartist.facebook_link,
                "website": retrieveartist.website,
                "seeking_venue": retrieveartist.seeking_venue,
                "seeking_description": retrieveartist.seeking_description,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": len(past_shows),
                "upcoming_shows_count": len(upcoming_shows)
            }

  except:
    print(sys.exc_info())
    
  if error:
    flash('ERROR!!')

  else:
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  artists={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genre,
    "city": artist.city,
    "state": artist.state,
    "phone":artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artists=artists)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  
 
    error = False
    form = ArtistForm()

    try:
        if form.validate_on_submit():
          newArtist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data)
          db.session.add(newArtist)
          db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
       
    finally:
        db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] +' was successfully listed!')
    else:
       flash('error has occured')


  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #query db for all shows
  shows = Show.query.all()

  data = []

  #display the shows

  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venues.name,
      'artist_id': show.artist_id,
      'artist_name': show.artists.name,
      'artist_image_link': show.artists.image_link,
      'start_time': str(show.start_time)

    })

    

  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  #TODO: insert form data as a new Show record in the db, instead

  form = ShowForm()

  try:
        if form.validate_on_submit():

          newShow = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
          )

          db.session.add(newShow)
          db.session.commit()
          flash('Succesfully Listed Show')
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
  finally:
        db.session.close()
        return render_template('pages/home.html')


  # on successful db insert, flash success
    #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
