#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
from datetime import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# logging.getLogger(__name__).addHandler(logging.NullHandler())

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(JSON)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))

    shows = db.relationship('Show', back_populates="venue", lazy=True)
    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.seeking_talent}>'


class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(JSON)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show',  back_populates="artist", lazy=True)
    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    venue =  db.relationship('Venue',  back_populates="shows", lazy=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    artist =  db.relationship('Artist',  back_populates="shows", lazy=True)
    start_time = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []
  for distinctCityVenue in Venue.query.distinct(Venue.city):
    app.logger.info('city = ' + str(distinctCityVenue.city))
    cityVenues = Venue.query.filter_by(city=distinctCityVenue.city).order_by('name').all()
    app.logger.info('cityVenues = ' + str(cityVenues))
    cityName = cityVenues[0].city
    stateName = cityVenues[0].state

    venueList = []
    for venue in cityVenues:
      venueItem = {
        "id": venue.id,
        "name": venue.name
      }
      venueList.append(venueItem)
      app.logger.info('venueList data = ' + str(venueList))

    cityItem = {
      "city": cityName,
      "state": stateName,
      "venues" :venueList
    }
    data.append(cityItem)
    app.logger.info('dataList data = ' + str(data))

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venueDat = Venue.query.get(venue_id)
  showList = Show.query.filter_by(venue_id=venue_id).limit(3).all()

  # TODO: filter condition for before and after date
  pastShows = []
  for pastShow in showList:
    artist = Artist.query.get(pastShow.artist_id)
    pastShow = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": "2019-05-21T21:30:00.000Z"
    }
    pastShows.append(pastShow)
  app.logger.info('pastShows data = ' + str(pastShows))

  upcomingShows = []
  for upcomingShow in showList:
    artist = Artist.query.get(upcomingShow.artist_id)
    upcomingShow = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": "2019-05-21T21:30:00.000Z"
    }
    upcomingShows.append(upcomingShow)
  app.logger.info('upcomingShows data = ' + str(upcomingShows))

  showGenres = []
  if venueDat.genres is not None: 
    app.logger.info('Genres = ' + str(json.dumps(venueDat.genres)))
    app.logger.info('Type =' + str(type(venueDat.genres)))
    showGenres = json.loads(json.dumps(venueDat.genres))

  data={
    "id": venueDat.id,
    "name": venueDat.name,
    "genres": showGenres,
    "address": venueDat.address,
    "city": venueDat.city,
    "state": venueDat.state,
    "phone": venueDat.phone,
    "website": venueDat.website,
    "facebook_link": venueDat.facebook_link,
    "seeking_talent": venueDat.seeking_talent,
    "seeking_description": venueDat.seeking_description,
    "image_link": venueDat.image_link,
    "past_shows":pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    app.logger.info('New Venue data acquired')
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, genres=genres)
    db.session.add(venue)
    db.session.commit()
    app.logger.info('New data for Venue commited')
    flash('Venue ' + name + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    app.logger.info('New data for Venue rolledback')
  finally:
    db.session.close()
    app.logger.info('New data for Venue session closed')
  if error:
    app.logger.info('Error orccured in new Venue')
    flash('Error occured. Venue ' + name + ' was not listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: render error page for no data or error
  allArtist = Artist.query.all()
  artistList = []
  for artist in allArtist:
    artistItem = {
      "id": artist.id,
      "name": artist.name
    }
    artistList.append(artistItem)
  app.logger.info('pastShows data = ' + str(artistList))

  return render_template('pages/artists.html', artists=artistList)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artistDat = Artist.query.get(artist_id)
  app.logger.info('artistDat = ' + str(artistDat))

  showList = Show.query.filter_by(artist_id=artist_id).limit(3).all()
  app.logger.info('showList = ' + str(showList))

  # TODO: filter with time for past and upcoing shows

  pastShows = []
  for pastShow in showList:
    artist = Artist.query.get(pastShow.artist_id)
    pastShow = {
      "venue_id": artist.id,
      "venue_name": artist.name,
      "venue_image_link": artist.image_link,
      "start_time": "2019-05-21T21:30:00.000Z"
    }
    pastShows.append(pastShow)
  app.logger.info('pastShows data = ' + str(pastShows))

  upcomingShows = []
  for upcomingShow in showList:
    artist = Artist.query.get(upcomingShow.artist_id)
    upcomingShow = {
      "venue_id": artist.id,
      "venue_name": artist.name,
      "venue_image_link": artist.image_link,
      "start_time": "2019-05-21T21:30:00.000Z"
    }
    upcomingShows.append(upcomingShow)
  app.logger.info('upcomingShows data = ' + str(upcomingShows))

  showGenres = []
  if artistDat.genres is not None: 
    app.logger.info('Genres = ' + str(json.dumps(artistDat.genres)))
    app.logger.info('Type =' + str(type(artistDat.genres)))
    showGenres = json.loads(json.dumps(artistDat.genres))

  data={
    "id": artistDat.id,
    "name": artistDat.name,
    "genres": [showGenres],
    "city": artistDat.city,
    "state": artistDat.state,
    "phone": artistDat.phone,
    "website": artistDat.website,
    "facebook_link": artistDat.facebook_link,
    "seeking_venue": artistDat.seeking_venue,
    "seeking_description": artistDat.seeking_description,
    "image_link": artistDat.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

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
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + name + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    app.logger.info('New data for Artist rolledback')
  finally:
    db.session.close()
    app.logger.info('New data for Artist session closed')
  if error:
    app.logger.info('Error orccured in new artist')
    flash('Error occured. Artist ' + name + ' was not listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.all()
  dispList = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    dispItem = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": "2019-05-21T21:30:00.000Z"
    }
    dispList.append(dispItem)

  return render_template('pages/shows.html', shows=dispList)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
