from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, ARRAY, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


db = SQLAlchemy()

def setup_db(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    address = Column(String(120))
    phone = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = Column(ARRAY(String(50)))
    website_link = Column(String(120))
    seeking_talent = Column(Boolean, default=False)
    seeking_description = Column(String)
    created_datetime = Column(DateTime(timezone=True), default=datetime.now(), nullable=False)
    shows = relationship("Show", backref="venue", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Venue{{ \
            id={str(self.id)}\
            , name='{self.name}'\
            , city='{self.city}'\
            , state='{self.state}'\
            , address='{self.address}'\
            , phone='{self.phone}'\
            , genres='{self.genres}'\
            , image_link='{self.image_link}'\
            , facebook_link='{self.facebook_link}'\
            , website_link='{self.website_link}'\
            , seeking_talent={self.seeking_talent}\
            , seeking_description='{self.seeking_description}'\
             }}"


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = Column(ARRAY(String(50)))
    website_link = Column(String(120))
    seeking_venue = Column(Boolean, default=False)
    seeking_description = Column(String)
    created_datetime = Column(DateTime(timezone=True), default=datetime.now(), nullable=False)
    shows = relationship("Show", backref="artist", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Venue{{ \
            id={str(self.id)}\
            , name='{self.name}'\
            , city='{self.city}'\
            , state='{self.state}'\
            , phone='{self.phone}'\
            , genres='{self.genres}'\
            , image_link='{self.image_link}'\
            , facebook_link='{self.facebook_link}'\
            , website_link='{self.website_link}'\
            , seeking_venue={self.seeking_venue}\
            , seeking_description='{self.seeking_description}'\
             }}"

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "shows"
  id = Column(Integer, primary_key=True)
  starting_time = Column(DateTime(timezone=True), default=datetime.now(), nullable=False)
  artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
  venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)

  def __repr__(self) -> str:
        return f"Venue{{ \
            id={str(self.id)}\
            , starting_time='{self.starting_time}'\
            , artist_id='{str(self.artist_id)}'\
            , venue_id='{str(self.venue_id)}'\
             }}"

