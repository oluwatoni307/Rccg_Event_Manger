from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId

from datetime import datetime, timedelta
from current_agent import process_agent



DATABASE_URL = "mongodb+srv://pelekadeba:JM-AMPMuk56pXqC@event-data.kg7uv.mongodb.net/EventsData"

# Connect to MongoDB using your DATABASE_URL
client = MongoClient(DATABASE_URL)

# Select the correct database and collection
db = client['EventsData']  # Your database name
collection = db['events_main']  # Replace with your collection name

# Get today's date
today = datetime.today().date()
print(today)

# Calculate the date 5 days from now
five_days_from_now = today + timedelta(days=7)

# Query to find events happening within the next 5 days
events_in_5_days = collection.find({
    "date": {
        "$gte": today.strftime("%Y/%m/%d"),  # Greater than or equal to today
        "$lte": five_days_from_now.strftime("%Y/%m/%d")  # Less than or equal to 5 days from now
    }
})

# Print the matching events
for event in events_in_5_days:
    # print(event)
    title = event['title']
    month = event['month']
    year = event['year']
    date = event['date']
    query = 'theme of '+title + ' '+ date
    theme = process_agent(query)
    print(theme)
    if theme == 'N/A':
        continue
    event['theme'] = theme
    event['upcoming'] = True
    collection.update_one(
        {"_id": event["_id"]},  # Use the _id from the event directly, it's already an ObjectId
        {"$set": {"theme": theme, "upcoming": True}}
    )
    


 
# title = 'Youth Convention'
# month = 'October'
# year = '2024'
# day = '2nd'



# answer = process_agent(query)
# print(answer)