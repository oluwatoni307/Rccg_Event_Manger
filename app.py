from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = os.getenv("DATABASE_URL")
mongo = PyMongo(app)

# test connection, for debugging
@app.route("/test-connection", methods=["GET"])
def test_mongo_connection():
    try:
        mongo.db.command("ping")
        return jsonify({"message": "MongoDB connection successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# converts the events id to a readable string
def objectid_to_str(obj):
    return str(obj)

# Create event function
def get_year_from_date(date):
    try:
        return int(date.split('/')[0])
    except Exception:
        return None

@app.route("/events", methods=["POST"])
def create_event():
    data = request.json
    date = data.get("date")
    year = get_year_from_date(date)
    
    event = {
        "title": data.get("title"),
        "venue": data.get("venue"),
        "date": data.get("date"),
        "time": data.get("time"),
        "month": data.get("month"),
        "theme": data.get("theme"),
        "year": year
    }
    try:
        result = mongo.db.events_main.insert_one(event)
        return jsonify({"message": "Event created", "id": objectid_to_str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Retrieve all events based off upcoming: false
@app.route("/events/all", methods=["GET"])
def get_all_events():
    events = mongo.db.events_main.find({"upcoming": False}).sort("date", 1) 
    return jsonify([{
        "id": objectid_to_str(event["_id"]),
        "title": event["title"],
        "venue": event["venue"],
        "time": event["time"],
        "date": event["date"],
        "month": event["month"],
        "theme": event["theme"],
        "upcoming":event["upcoming"]
    } for event in events]), 200

# Retrieve events by current month
@app.route("/events/current_month", methods=["GET"])
def get_current_month_events():
    current_month = datetime.now().strftime("%B")
    events = mongo.db.events_main.find({"month": current_month}).sort("date", 1)
    return jsonify([{
        "id": objectid_to_str(event["_id"]),
        "title": event["title"],
        "venue": event["venue"],
        "time": event["time"],
        "date": event["date"],
        "month": event["month"],
        "theme": event["theme"],
    } for event in events]), 200


# Retrieve an event by id function
@app.route("/events/<event_id>", methods=["GET"])
def get_event(event_id):
    event = mongo.db.events_main.find_one_or_404({"_id": ObjectId(event_id)})
    return jsonify({
        "id": objectid_to_str(event["_id"]),
        "title": event["title"],
        "venue": event["venue"],
        "time": event["time"],
        "date": event["date"],
        "month": event["month"],
        "theme": event["theme"]
    }), 200

# Update event details
@app.route("/events/<event_id>", methods=["PUT"])
def update_event(event_id):
    data = request.json
    update_fields = {
        "title": data.get("title"),
        "venue": data.get("venue"),
        "time": data.get("time"),
        "date": data.get("date"),
        "month": data.get("month"),
        "theme": data.get("theme")
    }
    # Filter out None values (e.g., if a field is missing in the request)
    update_fields = {k: v for k, v in update_fields.items() if v is not None}
    
    result = mongo.db.events_main.update_one({"_id": ObjectId(event_id)}, {"$set": update_fields})
    if result.matched_count > 0:
        return jsonify({"message": "Event updated"}), 200
    else:
        return jsonify({"error": "Event not found"}), 404

# Delete event
@app.route("/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    result = mongo.db.events_main.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count > 0:
        return jsonify({"message": "Event deleted"}), 200
    else:
        return jsonify({"error": "Event not found"}), 404


@app.route("/events/upcoming", methods=["GET"])
def get_upcoming_events():
    present = datetime.now().date()
    present_formatted_date = present.strftime("%Y/%m/%d")
    end_date = present + timedelta(days=10)
    end_formatted_date = end_date.strftime("%Y/%m/%d")
    events = mongo.db.events_main.find({"date": {"$gte": present_formatted_date, "$lt": end_formatted_date}})
    
    return jsonify([{
        "id": objectid_to_str(event["_id"]),
        "title": event["title"],
        "venue": event["venue"],
        "time": event["time"],
        "date": event["date"],
        "month": event["month"],
        "theme": event["theme"],
    } for event in events]), 200

if __name__ == "__main__":
    app.run(debug=True)
