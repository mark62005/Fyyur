#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from sqlalchemy.sql.elements import or_
from forms import *
import traceback
from datetime import datetime, timedelta
from models import Show, Artist, Venue, db, setup_db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# # app.config.from_object('config')
# db = SQLAlchemy(app)
setup_db(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

def getDestinctCitiesAndStates() -> list:
  return db.session.query(Venue.city, Venue.state)\
    .distinct(Venue.city, Venue.state).order_by(Venue.state).all()

@app.route('/venues')
def get_venues() -> str:
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  try:
    data = []
    areas = getDestinctCitiesAndStates()
    venues = Venue.query.all()

    for area in areas:
      new_area = {
        "city": area["city"],
        "state": area["state"],
        "venues": []
      }
      for venue in venues:
        if (area["city"] == venue.city and area["state"] == venue.state):
          new_area["venues"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0
          })
      data.append(new_area)

    return render_template('pages/venues.html', areas=data)
  except:
    traceback.print_stack()
    abort(404)


def count_num_upcoming_shows(venue: Venue) -> int:
    count = 0
    now = datetime.timestamp(datetime.now())
    for show in venue.shows:
      if (datetime.timestamp(show.starting_time) > now):
        count += 1

    return count


def search_venues_by_name(search_term: str) -> object:
    venues_by_name = Venue.query.filter(
        Venue.name.ilike(f"%{search_term}%")).all()
    searched_by_name = {
        "count": len(venues_by_name),
        "data": []
    }
    for venue in venues_by_name:
        searched_by_name["data"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": count_num_upcoming_shows(venue)
        })
    return searched_by_name


def search_venues_by_city_and_state(search_term: str):
    areas = db.session.query(Venue.city, Venue.state)\
        .distinct("city", "state")\
        .filter(or_(
                Venue.city.ilike(f"%{search_term}%"),
                Venue.state.ilike(f"%{search_term}%"))).all()
    venues_by_city_state = Venue.query.filter(or_(
        Venue.city.ilike(f"%{search_term}%"),
        Venue.state.ilike(f"%{search_term}%"))).all()
    searched_by_city_state = {
        "count": len(venues_by_city_state),
        "data": []
    }

    for area in areas:
        new_area = {
            "city": area.city,
            "state": area.state,
            "venues": []
        }
        for venue_by_city_state in venues_by_city_state:
            if (area.city == venue_by_city_state.city and area.state == venue_by_city_state.state):
                new_area["venues"].append({
                    "id": venue_by_city_state.id,
                    "name": venue_by_city_state.name,
                    "num_upcoming_shows": count_num_upcoming_shows(venue_by_city_state)
                })
        searched_by_city_state["data"].append(new_area)
    return searched_by_city_state

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # try:
  search_term = request.form.get('search_term', '')

  searched_by_name = search_venues_by_name(search_term)
  searched_by_city_state = search_venues_by_city_and_state(search_term)

  return render_template('pages/search_venues.html',
                          searched_by_name=searched_by_name,
                          searched_by_city_state=searched_by_city_state,
                          search_term=search_term)
  # except:
  #   abort(404)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  data = {}
  venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

  if venue is None:
    abort(404)

  data = {
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "genres": venue.genres,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [{
      # "artist_id": 0,
      # "artist_name": "",
      # "artist_image_link": "",
      # "start_time": ""
    }],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = VenueForm(request.form)

  try:
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data,
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    error = True
    db.session.rollback()
    traceback.print_stack()
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()

  if error:
    abort(422)
  else:
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

  if venue is None:
    abort(404)

  try:
    db.session.delete(venue)
    db.session.commit()
    flash(f"{venue.name} has been deleted successfully.")
  except:
    error = True
    db.session.rollback()
    traceback.print_stack()
    flash("Something went wrong!")
  finally:
    db.session.close()
  
  if error:
    return redirect(url_for("show_venue", venue_id = venue_id))
  else:
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  try:
    search_term = request.form.get('search_term', '').strip()
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).order_by(Artist.name).all()

    response = {
      "count": len(artists),
      "data": []
    }

    for artist in artists:
      response["data"].append({
        "id": artist.id,
        "name": artist.name
      })

    return render_template('pages/search_artists.html', results=response, search_term=search_term)
  except:
    abort(404)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

  if artist is None:
    abort(404)

  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "genres": artist.genres,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [
      # {
      # "venue_id": 1,
      # "venue_name": "The Musical Hop",
      # "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      # "start_time": "2019-05-21T21:30:00.000Z"
      # }
    ],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }

  return render_template('pages/show_artist.html', artist=data)


#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  error = False
  artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

  if artist is None:
    abort(404)

  try:
    db.session.delete(artist)
    db.session.commit()
    flash(f"{artist.name} has been deleted successfully.")
  except:
    error = True
    db.session.rollback()
    traceback.print_stack()
    flash("Something went wrong!")
  finally:
    db.session.close()
  
  if error:
    return redirect(url_for("show_artist", artist_id = artist_id))
  else:
    return redirect(url_for("index"))


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm(request.form)
  artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

  if artist is None:
    abort(404)

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)

  try:
    if (form.name.data):
      artist.name = form.name.data
    if (form.city.data):
      artist.city = form.city.data
    if (form.state.data):
      artist.state = form.state.data
    if (form.phone.data):
      artist.phone = form.phone.data
    if (form.genres.data):
      artist.genres = form.genres.data
    if (form.facebook_link.data):
      artist.facebook_link = form.facebook_link.data
    if (form.image_link.data):
      artist.image_link = form.image_link.data
    if (form.website_link.data):
      artist.website_link = form.website_link.data
    if (form.seeking_venue.data):
      artist.seeking_venue = form.seeking_venue.data
    if (form.seeking_description.data):
      artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash(f"Aritst {form.name.data} has been edited successfully.")
  except:
    error = True
    db.session.rollback()
    traceback.print_stack()
    flash("Something went wrong!")
  finally:
    db.session.close()

  if error:
    abort(422)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()  
  venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

  if venue is None:
    abort(404)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)

  try:
    if (form.name.data):
      venue.name = form.name.data
    if (form.city.data):
      venue.city = form.city.data
    if (form.state.data):
      venue.state = form.state.data
    if (form.address.data):
      venue.address = form.address.data
    if (form.phone.data):
      venue.phone = form.phone.data
    if (form.genres.data):
      venue.genres = form.genres.data
    if (form.facebook_link.data):
      venue.facebook_link = form.facebook_link.data
    if (form.image_link.data):
      venue.image_link = form.image_link.data
    if (form.website_link.data):
      venue.website_link = form.website_link.data
    if (form.seeking_talent.data):
      venue.seeking_talent = form.seeking_talent.data
    if (form.seeking_description.data):
      venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash(f"{form.name.data} has been edited successfully.")
  except:
    error = True
    db.session.rollback()
    flash("Something went wrong!")
    traceback.print_stack()
  finally:
    db.session.close()
  
  if error:
    abort(422)
  else:
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
  form = ArtistForm(request.form)
  try:
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data,
    )

    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    error = True
    db.session.rollback()
    traceback.print_stack()
    flash('An error occurred. Artist ' + form.data.name + ' could not be listed.')
  finally:
    db.session.close()

  if error:
    abort(422)
  else:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  try:
    data = []
    joined_shows = db.session.query(
      Show.venue_id, 
      Venue.name, 
      Show.artist_id, 
      Artist.name, 
      Artist.image_link, 
      Show.starting_time
    )\
    .join(Venue)\
    .join(Artist)\
    .order_by(Show.starting_time)\
    .all()

    for show in joined_shows:
      data.append({
        "venue_id": show[0],
        "venue_name": show[1],
        "artist_id": show[2],
        "artist_name": show[3],
        "artist_image_link": show[4],
        "starting_time": show[5]
      })
    return render_template('pages/shows.html', shows=data)
  except:
    flash("Something went wrong!")
    abort(404)


def isArtistAvailable(artist: Artist, new_start_time: datetime):
    """
    Check if an artist is avaible at the start time which user is tyring to book, return True if the artist is available, else False
    :param artist: the artist that we're checking
    :param new_start_time: the start time that user trying to book
    :return: True if the artist is available, else False
    """
    for show in artist.shows:
        booked_start_time = (show.starting_time)
        booked_end_time = show.starting_time + timedelta(hours=5)
        if datetime.timestamp(booked_start_time) <= datetime.timestamp(new_start_time) <= datetime.timestamp(booked_end_time):
            formatted_booked_start_time = booked_start_time.strftime(
                "%m/%d/%Y at %H:%M:%S")
            formatted_booked_end_time = booked_end_time.strftime("%H:%M:%S")
            flash(
                f"Sorry, {artist.name} will not be available from {formatted_booked_start_time} to {formatted_booked_end_time} , please try another time.")
            db.session.rollback()
            db.session.close()
            return False
    return True


def isVenueAvailable(venue: Venue, new_start_time: datetime):
    """
    Check if an venue is avaible at the start time which user is tyring to book, return True if the venue is available, else False
    :param venue: the venue that we're checking
    :param new_start_time: the start time that user trying to book
    :return: True if the venue is available, else False
    """
    for show in venue.shows:
        booked_start_time = show.starting_time
        booked_end_time = show.starting_time + timedelta(hours=5)
        if datetime.timestamp(booked_start_time) <= datetime.timestamp(new_start_time) <= datetime.timestamp(booked_end_time):
            formatted_booked_start_time = booked_start_time.strftime(
                "%m/%d/%Y at %H:%M:%S")
            formatted_booked_end_time = booked_end_time.strftime("%H:%M:%S")
            flash(
                f"Sorry, {venue.name} is already booked from {formatted_booked_start_time} to {formatted_booked_end_time} , please try another time.")
            db.session.rollback()
            db.session.close()
            return False
    return True

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm(request.form)

  new_start_time = form.start_time.data
  artist = Artist.query.filter(Artist.id == form.artist_id.data).one_or_none()
  venue = Venue.query.filter(Venue.id == form.venue_id.data).one_or_none()

  if artist is None or venue is None:
    abort(404)

  # try:
  if isArtistAvailable(artist, new_start_time) and isVenueAvailable(venue, new_start_time):
      show = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        starting_time = form.start_time.data,
      )
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  else:
      return redirect(url_for("create_shows"))
  # except:
  #   # TODO: on unsuccessful db insert, flash an error instead.
  #   # e.g., flash('An error occurred. Show could not be listed.')
  #   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #   error = True
  #   db.session.rollback()
  #   traceback.print_stack()
  #   flash('An error occurred. Show could not be listed.')
  # finally:
  #   db.session.close()

  # if error:
  #   abort(422)
  # else:
  #   return render_template('pages/home.html')


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
