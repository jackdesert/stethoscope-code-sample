API: Location History
=====================

This endpoint works either via POST (allows you to send in priors)
or GET (simple to use from a web page)

POST /badges/:badge_id/location
GET  /badges/:badge_id/location


Payload (POST only)
-------------------

    {
      'grain' : <integer>,
      'date'  : <string>,
      'algorithm' : <string>,
      'return_value' : <string>,
      'offset': <integer>,
      'priors': [
                  [<room_id>, <weight>],
                  [<room_id>, <weight>],
                  [<room_id>, <weight>]]
    }

* `grain` is the number of seconds that are grouped together.
* `grain` must be one of: 60, 600, 3600
  If no grain is specified, all rssi readings for the day will be returned
* `date` is in the format 2018-12-29. If date is not specified, default is today's date.
* `return_value` may be either "room_id" or "room_name"
* `algorithm` may be either "raw" or "bayes"
* If both `grain` and `offset` are present, and you are fetching data for the current day, it will start with the period you specify with "offset", and end with the last completed period. For example, if grain is 3600 and offset is 5 and date is NULL (default to current day) and the time is currently 07:30, the periods returned will be
    [{start: 05:00, end: 06:00},
     {start: 06:00, end: 07:00}]
* `priors` means how many times more likely than the default value are they to be in that room.
* `priors` is optional. That is, this endpoint may be called with no payload at all.
* If `priors` are included, the default prior is 1.0. That means any trained rooms that are not explicitly listed in your priors will receive a value of 1.
* Ordering of the rooms does not matter.
* Parameters not listed in the payload above will be ignored.
* Weights need not add up to 1.0.


Request Data Types
------------------

  * room_id:   uuid. Any uuids that are not listed by [this elitecarerails endpoint](https://bip.elitecare.com/api/stethoscope/rooms_insecure) will be ignored
  * weight:    number (Weights need not add to 100%)


Authentication
--------------

Authentication by IP address whitelisting.


Status Codes
------------

    * 200: Success
    * 400: Invalid Payload
    * 404: ----- TODO---- do we need a 404 for anything?Badge not active in last 60 seconds
    * 500: Server error


Response
--------

    [ [ <timestamp_or_period>, <value> ],
      [ <timestamp_or_period>, <value> ],
      ...
    ]



### Timestamp or Period

If `grain` is not specified, `timestamp_or_period` represents the timestamp of the rssi reading.
If `grain` is specified, `timestamp_or_period` represents the beginning of the period


### Value

`value` is determined by the input parameter `return_value`



Response Data Types
-------------------

* timestamp_or_period: string
* value: string. Sometimes a uuid, sometimes a room name such as "Tabor 3B"




Curl Example
------------

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/badges/BIP1005/location_history   -d '{"priors": [["d168fd6b-6c24-4098-b90d-c9737a22cb03", 10], ["5359f090-2165-49a2-967b-22cbe59eef23", 30]], "algorithm": "bayes", "return_value": "room_name" }'


Curl Example (Localhost)
------------------------

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/badges/BIP1005/location_history   -d '{"priors": [["d168fd6b-6c24-4098-b90d-c9737a22cb03", 10], ["5359f090-2165-49a2-967b-22cbe59eef23", 30]], "algorithm": "bayes", "return_value": "room_name" }'


