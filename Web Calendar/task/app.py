from flask import Flask
from flask_restful import Api, Resource, reqparse, inputs, marshal_with, fields, abort
from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import *

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

class Event(db.Model):
    __tablename__ = "data_table"
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(40), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return '<Event %r>' % self.event

    def serialize(self):
        print('didnt serialize right')
        return {
            'id': self.id,
            'event': self.event,
            'date': self.date
        }

db.create_all()


# write your code here

class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d')

resource_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': MyDateFormat
}
reaponse_message_fileds = {
    'message': fields.String
}

class EventDao(object):
    def __init__(self, event, date):
        self.event = event
        self.date = date

parser = reqparse.RequestParser()
parser2 = reqparse.RequestParser()

parser.add_argument(
    'event',
    type=str,
    help='The event name is required!',
    required=True
)
parser.add_argument(
    'date',
    type=inputs.date,
    help='The event date with the correct format is required! The correct format is YYYY-MM-DD!',
    required=True
)

parser2.add_argument(
    'start_time',
    type=inputs.date,
    help='Enter start date',
    required=False
)

parser2.add_argument(
    'end_time',
    type=inputs.date,
    help='Enter end date',
    required=False
)


class EventResource(Resource):

    @marshal_with(resource_fields)
    def get(self):
        return Event.query.filter(Event.date == date.today()).all()


class EventHandler(Resource):
    def post(self):
        pass

    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(http_status_code=404, message="The event doesn't exist!")
        return event

    @marshal_with(reaponse_message_fileds)
    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(http_status_code=404, message="The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        return {'message': 'The event has been deleted!'}


class EventParser(Resource):
    # @marshal_with(resource_fields)
    def post(self):
        args_for_input = parser.parse_args()
        print(args_for_input)
        if args_for_input['event'] != None and args_for_input['date'] != None:
            event = Event(event=args_for_input['event'], date=args_for_input['date'].date())
            db.session.add(event)
            db.session.commit()
        if args_for_input['event'] == '':
            args_for_input['event'] = None
        response = {
            "message": "The event has been added!",
            "event": args_for_input['event'],
            "date": str(args_for_input['date'].date())
        }
        return response


    @marshal_with(resource_fields)
    def get(self):
        args_for_output = parser2.parse_args()
        if not args_for_output['start_time'] and not args_for_output['end_time']:
            return Event.query.all()
        events = Event.query.filter(Event.date >= args_for_output['start_time'].date()).\
            filter(Event.date<=args_for_output['end_time'].date()).all()
        json_events = []
        for event in events:
            response = event.serialize()
            json_events.append(response)

        return json_events

class EventAll(Resource):

    @marshal_with(resource_fields)
    def get(self):
        return Event.query.all()



api.add_resource(EventResource, '/event/today')
api.add_resource(EventParser, '/event/', methods=['POST', "GET"])
api.add_resource(EventHandler, '/event/<int:event_id>')


# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
