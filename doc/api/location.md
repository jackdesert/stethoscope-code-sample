API: Location
=============

This endpoint works either via POST (allows you to send in priors)
or GET (simple to use from a web page)

POST /badges/:badge_id/location
GET  /badges/:badge_id/location


Payload (POST only)
-------------------

    {
      'priors': [
                  [<room_id>, <weight>],
                  [<room_id>, <weight>],
                  [<room_id>, <weight>]]
    }

* `priors` is optional. That is, this endpoint may be called with no payload at all.
* If `priors` are included, you must provide a weight for each room which had training runs when the keras model was trained.
* Ordering of the rooms does not matter.
* Parameters not listed in the payload above will be ignored.
* Weights need not add up to 1.0.


Request Data Types
------------------

  * room_id:   uuid. Must be one of the uuids given by [this elitecarerails endpoint](https://bip.elitecare.com/api/stethoscope/rooms_insecure)
  * weight:    number (Weights need not add to 100%)


Authentication
--------------

No authentication is required. This may change in the future.


Status Codes
------------

    * 200: Success
    * 400: Invalid Payload
    * 404: Badge not active in last 60 seconds
    * 409: One or more supplied prior room ids not found in bip_rooms
    * 500: Server error


Response
--------

    { 'raw':   [
                 // Highest Raw Probability First
                 // Raw Probabilities sum to 1.0
                 [<room_id>, <raw_probability>, <room_name>],
                 [<room_id>, <raw_probability>, <room_name>],
                 [<room_id>, <raw_probability>, <room_name>],
               ],
      'bayes': [ // Bayes result is only present if "priors" is included in the request
                 // Highest Bayes Probability First
                 // Bayes Probabilities sum to 1.0
                 // Bayes weights sum to 1.0
                 [<room_id>, <bayes_probability>, <room_name>, <bayes_weight>],
                 [<room_id>, <bayes_probability>, <room_name>, <bayes_weight>],
                 [<room_id>, <bayes_probability>, <room_name>, <bayes_weight>],
               ],
      'reading': {'id': <integer>,
                  'beacons': <array>,
                  'timetamp': <string>,
                  'pi_id': <string>,
                  'badge_id': <string>,
                  'imposter_beacons': <array>
    }



### Raw

The `raw` version is the straight probabilites from our keras deep learning model,
sorted by probability.


### Bayes

The `bayes` version takes into account the priors that were passed in.
These priors are intended to represent how often a person is actually in a given room.
It starts with the `raw` data, then applies Bayes` Theorem.

### Reading

`imposter_beacons` should be empty. If not, it means there is an active beacon that
was not active during the keras model training. As such, this imposter beacon
will displace actual readings and will worsen location accuracy.



Response Data Types
-------------------

* room_id: uuid (Only rooms present in TrainingRuns will be shown)
* raw_probability: number between 0.0 and 1.0.
* bayes_probability: number between 0.0 and 1.0.
* room_name: string


Algorithm
---------

Currently this endpoint uses the most recent RssiReading from that badge.



### Future Algorithms

The response above shows the results of two distinct algorithms: `raw` and `bayes`.
In the future, the payload may include more than just these two. Additional
algorithms will follow the same pattern of [<room_id>, <probability>,
<room_name>, ...]



Curl Example
------------

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/badges/abcd/location   -d '{"priors": [["abc", 50], ["def", 30]] }'


Curl Example (Localhost)
------------------------

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/badges/1/location   -d '{"priors": [["9cc6a280-8b7b-4ece-a986-fcb566511696", 50], ["da651323-17f0-4dbe-ba09-81b18ec25744", 30]] }'


