API: Location
=============

POST /badges/:badge_id/location


Payload
-------

    {
      'priors': [
                  [<room_id>, <weight>],
                  [<room_id>, <weight>],
                  [<room_id>, <weight>]]
    }

* `priors` is optional. That is, this endpoint may be called with no payload at all.
* Ordering of the rooms does not matter.
* Parameters not listed in the payload above will be ignored.


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
                 // Highest Probability First
                 [<room_id>, <probability>, <room_name>],
                 [<room_id>, <probability>, <room_name>],
                 [<room_id>, <probability>, <room_name>],
               ],
      'bayes': [ // Bayes result is only present if "priors" is included in the request
                 // Highest Probability First
                 [<room_id>, <probability>, <room_name>, <prior_probability>],
                 [<room_id>, <probability>, <room_name>, <prior_probability>],
                 [<room_id>, <probability>, <room_name>, <prior_probability>],
               ]
    }



### Raw

The `raw` version is the straight probabilites from our keras deep learning model,
sorted by probability.


### Bayes

The `bayes` version takes into account the priors that were passed in.
These priors are intended to represent how often a person is actually in a given room.
It starts with the `raw` data, then applies Bayes` Theorem.


### Future Algorithms

The response above shows the results of two distinct algorithms: `raw` and `bayes`.
In the future, the payload may include more than just these two. Additional
algorithms will follow the same pattern of [<room_id>, <probability>,
<room_name>, ...]


Response Data Types
-------------------

* room_id: uuid
* probability: number between 0.0 and 1.0. The room with the highest probability is shown first. Probabilities for each algorithm sum to 1.0.
* room_name: string
* prior_probability: number between 0.0 and 1.0. It's the same as the passed in `weight` for that room, but shown as a percentage of the total weights.






Curl Example
------------

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/badges/abcd/location   -d '{"priors": [["abc", 50], ["def", 30]] }'


Curl Example (Localhost)
------------------------

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/badges/1/location   -d '{"priors": [["9cc6a280-8b7b-4ece-a986-fcb566511696", 50], ["da651323-17f0-4dbe-ba09-81b18ec25744", 30]] }'


