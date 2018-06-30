import googlemaps

class Trip():
    def __init__(self,origin,destination,distance,duration):
        self.origin = origin
        self.destination = destination
        self.distance = distance
        self.duration = duration

key = "AIzaSyDpQIj9Cd67_JYAcDkg2Cy61C3xZBYSLC8"

def get_trips(origin, listings):
    gmaps = googlemaps.Client(key = key)


    dests = []
    for listing in listings:
        dests.append(listing.address)

    matrix = gmaps.distance_matrix([origin], dests)

    trips = {}

    i = 0

    while(i<len(matrix["destination_addresses"])):

        listing = listings[i]
        elements = matrix["rows"][0]["elements"][i]

        if("OK" not in elements["status"]):
            i+=1
            continue

        origin = matrix["origin_addresses"][0]
        destination = matrix["destination_addresses"][i]

        distance = int(elements["distance"]["value"])
        duration = int(elements["duration"]["value"])

        trip = Trip(
            origin,
            destination,
            distance,
            duration,
        )

        trips[listing] = trip
        i+=1

    return trips

def test_address(address):
    gmaps = googlemaps.Client(key = key)
    matrix = gmaps.distance_matrix(["New York"], [address])
    elements = matrix["rows"][0]["elements"][0]
    return "OK" in elements["status"]



