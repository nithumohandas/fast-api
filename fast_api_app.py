from fastapi import Body, FastAPI

app = FastAPI()

destinations = [
    {'city': 'Bali', 'country': 'Vietnam', 'feature': 'Tropical beaches and vibrant culture'},
    {'city': 'Kerala', 'country': 'India', 'feature': 'Backwaters and Ayurvedic retreats'},
    {'city': 'Lucerne', 'country': 'Switzerland', 'feature': 'Lake views and medieval architecture'},
    {'city': 'Zurich', 'country': 'Switzerland', 'feature': 'Financial hub with scenic old town'},
    {'city': 'Kashmir', 'country': 'India', 'feature': 'Snowy mountains and houseboats'},
    {'city': 'Tokyo', 'country': 'Japan', 'feature': 'Modern cityscape and traditional temples'}
]
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/travel_destinations")
async def get_travel_destinations():
    return destinations

@app.get("/travel_destinations/{country}")
async def get_country_travel_destinations(country: str, city: str = None):
    country_destinations = []
    for destination in destinations:
        if destination["country"] == country:
            if city and destination["city"] == city:
                country_destinations.append(destination)
            elif city is None:
                country_destinations.append(destination)
    return country_destinations

@app.post("/travel_destinations/create_travel_destination")
async def create_travel_destinations(new_destination=Body()):
   destinations.append(new_destination)

