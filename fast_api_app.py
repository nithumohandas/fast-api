from fastapi import FastAPI

from models.travel_destinations import TravelDestination, TravelDestinationRequest

app = FastAPI()

destinations = [
    {'city': 'Bali', 'country': 'Vietnam', 'feature': 'Tropical beaches and vibrant culture'},
    {'city': 'Kerala', 'country': 'India', 'feature': 'Backwaters and Ayurvedic retreats'},
    {'city': 'Lucerne', 'country': 'Switzerland', 'feature': 'Lake views and medieval architecture'},
    {'city': 'Zurich', 'country': 'Switzerland', 'feature': 'Financial hub with scenic old town'},
    {'city': 'Kashmir', 'country': 'India', 'feature': 'Snowy mountains and houseboats'},
    {'city': 'Tokyo', 'country': 'Japan', 'feature': 'Modern cityscape and traditional temples'}
]

destination_objects = [
    TravelDestination(id=i, **dest)
    for i, dest in enumerate(destinations, start=1)
]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/travel_destinations")
async def get_travel_destinations():
    return destination_objects

@app.get("/travel_destinations/{country}")
async def get_country_travel_destinations(country: str, city: str = None):
    country_destinations = []
    for destination in destination_objects:
        if destination.country == country:
            if city and destination.city == city:
                country_destinations.append(destination)
            elif city is None:
                country_destinations.append(destination)
    return country_destinations

@app.post("/travel_destinations/create_travel_destination")
async def create_travel_destinations(new_destination: TravelDestinationRequest):
    new_dest =TravelDestination(**new_destination.model_dump())
    destination_objects.append(new_dest)

@app.put("/travel_destinations/{city}")
async def update_travel_destinations(city: str, new_destination: TravelDestinationRequest):
    for i in range(len(destination_objects)):
        if destination_objects[i].city == city:
            new_dest = TravelDestination(**new_destination.model_dump())
            destination_objects[i] = new_dest

@app.delete("/travel_destinations/{city}")
async def delete_travel_destinations(city: str):
    for i in range(len(destination_objects)):
        if destination_objects[i].city == city:
            destination_objects.pop(i)
            break