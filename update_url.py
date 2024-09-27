from pymongo import MongoClient
from datetime import datetime
from current_agent import process_agent

DATABASE_URL = "mongodb+srv://pelekadeba:JM-AMPMuk56pXqC@event-data.kg7uv.mongodb.net/EventsData"

# Connect to MongoDB
client = MongoClient(DATABASE_URL)
db = client['EventsData']
collection = db['events_main']

# Get today's date
today = datetime.today().date()
print(f"Today's date: {today}")

# Query to find events with upcoming=True and date past today
events_to_process = collection.find({
    "upcoming": True,
    "date": {"$lt": today.strftime("%Y/%m/%d")}  # Less than today's date
})

# Process the matching events
for event in events_to_process:
    title = event['title']
    date = event['date']
    theme = event['theme']
    query = f'Event Name: {title},Event Theme: {theme},Event Date: {date}'
    url = process_agent(query)
    
    if url != 'N/A':
        print(f"Processing event: {title} on {date}")
        print(f"Theme: {theme}")
        
        # Update the event in the database
        collection.update_one(
            {"_id": event["_id"]},
            {"$set": {"url": url}}  # Set upcoming to False as it's past
        )
    else:
        print(f"Skipping event: {title} (url = N/A)")

print("Processing complete.")