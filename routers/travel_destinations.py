from time import sleep

from fastapi import APIRouter, HTTPException, Path, Query, BackgroundTasks
from starlette import status
from fastapi.responses import StreamingResponse

from schemas.travel_destinations import TravelDestination

router = APIRouter(prefix="/travel_destinations", tags=["Travel Destinations"])

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

def run_long_running_job():
    sleep(10)
    print("Running Long Running Job")

@router.get("/", status_code= status.HTTP_200_OK)
async def get_travel_destinations():
    return destination_objects

@router.get("/{country}", status_code= status.HTTP_200_OK)
async def get_country_travel_destinations(country: str, city: str = None):
    country_destinations = []
    for destination in destination_objects:
        if destination.country == country:
            if city and destination.city == city:
                country_destinations.append(destination)
            elif city is None:
                country_destinations.append(destination)
    return country_destinations

@router.post("/create_travel_destination", status_code= status.HTTP_201_CREATED)
async def create_travel_destinations(new_destination: TravelDestination, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_long_running_job)
    new_dest =TravelDestination(**new_destination.model_dump())
    destination_objects.append(new_dest)

@router.put("/{city}", status_code= status.HTTP_200_OK)
async def update_travel_destinations(city: str = Path(description="Name of City"),
                                     new_destination: TravelDestination = Query(description="New Destination")):
    found = False
    for i in range(len(destination_objects)):
        if destination_objects[i].city == city:
            new_dest = TravelDestination(**new_destination.model_dump())
            destination_objects[i] = new_dest
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="City not found")

@router.delete("/{city}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_travel_destinations(city: str):
    found = False
    for i in range(len(destination_objects)):
        if destination_objects[i].city == city:
            destination_objects.pop(i)
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="City not found")

async def fake_video_streamer():
    for i in range(10):
        yield b"some fake video bytes"

@router.get("/streaming", status_code= status.HTTP_200_OK)
async def main():
    return StreamingResponse(fake_video_streamer())