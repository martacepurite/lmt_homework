
### Dev setup 

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

fastapi dev main.py


## Run tests

pytest


### Code and info sources

https://fastapi.tiangolo.com/tutorial/sql-databases/#create-models
https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#add-the-rest-of-the-tests
https://geopy.readthedocs.io/en/latest/
https://gis.stackexchange.com/questions/425452/calculate-distance-between-two-lat-lon-alt-points-in-python
https://forest.moscowfsl.wsu.edu/fswepp/rc/kmlatcon.html
https://plotly.com/python/getting-started/
https://plotly.com/python/scatter-plots-on-maps/

https://geopy.readthedocs.io/en/latest/index.html#geopy.distance.Distance.destination
https://stackoverflow.com/questions/7477003/calculating-new-longitude-latitude-from-old-n-meters


## TODO/ideas

* Docker
* Update radar data schema
* floats with single precision
* Error handling
* More tests
* Cost calculation algorithm
* Animations?
* Prioritising algorithm to make quicker decisions if target is high danger (fast)
* Triage algorithm 
    * Speed
    * Heading direction (towards/away)
* Fetch data from database only on start



## Notes

Heading direction is the angle between the observer’s current position and the target location, measured clockwise from North. It is often expressed in:

Degrees: 0° = North, 90° = East, 180° = South, 270° = West, and values in between (e.g., 45° = Northeast).

![alt text](image.png)https://outdoorquest.blogspot.com/2015/07/compass-navigation-bearing-and-heading.html