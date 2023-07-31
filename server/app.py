#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''


@app.route('/scientists', methods=['GET', 'POST'])
def scientists():
    if request.method == 'GET':
        scientist_list = [scientist.to_dict(rules=('-missions',)) for scientist in Scientist.query.all()]

        return make_response(scientist_list, 200)
    
    if request.method == 'POST':
        data = request.json
        try:
            scientist = Scientist(name = data['name'], field_of_study = data['field_of_study'])
            db.session.add(scientist)
            db.session.commit()

            return make_response(scientist.to_dict(rules=('-missions',)), 201)
        
        except:
            return make_response({"errors": ["validation errors"]}, 400)



@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientist_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()

    if request.method == 'GET':
        if scientist == None:
            return make_response({'error': 'Scientist not found'}, 404)
        
        return make_response(scientist.to_dict(), 200)
    

    if request.method == 'PATCH':
        if scientist == None:
            return make_response({'error': 'Scientist not found'}, 404)
        
        data = request.json
        try:
            for attr in data:
                setattr(scientist, attr, data[attr])
            db.session.commit()

            return make_response(scientist.to_dict(rules=('-missions',)), 202)
        
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        

    if request.method == 'DELETE':
        if scientist == None:
            return make_response({'error': 'Scientist not found'}, 404)
        
        Mission.query.filter(Mission.scientist_id == scientist.id).delete()
        db.session.delete(scientist)
        db.session.commit()
        return make_response('', 204)
        


@app.route('/planets', methods=['GET'])
def planets():
    if request.method == "GET":
        planet_list = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]

        return make_response(planet_list, 200)


@app.route('/missions', methods=['GET', 'POST'])
def missions():
    if request.method == "GET":
        mission_list = [mission.to_dict() for mission in Mission.query.all()]

        return make_response(mission_list, 200)
    
    if request.method == 'POST':
        data = request.json
        try:
            mission = Mission(name = data['name'], scientist_id = data['scientist_id'], planet_id = data['planet_id'])
            db.session.add(mission)
            db.session.commit()

            return make_response(mission.to_dict(), 201)
        
        except:
            return make_response({"errors": ["validation errors"]}, 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
