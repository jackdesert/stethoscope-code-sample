API: RSSI Readings
==================

POST /rssi_readings


Payload
-------

    {
     'badge_id': <badge_id>,
     'pi_id':    <pi_id>,
     'beacons': { <beacon_id>: <rssi>,
                  <beacon_id>: <rssi>,
                  <beacon_id>: <rssi> }
    }

Badge ID and PI ID are required keys.

The ordering of the beacons does not matter.

Parameters not listed in the payload above will be ignored.


Data Types
----------

  * badge_id:  string
  * pi_id:     string
  * beacon_id: string
  * rssi:      integer


Authentication
--------------

No authentication is required. This may change in the future.


Status Codes
------------

    * 201: Created
    * 400: Invalid Payload
    * 404: Not Found (Check URL)
    * 409: Conflict (Duplicate)
    * 500: Server error


Duplicates are Expected
-----------------------

When N PIs hear a particular badge, all N of those PIs will POST
the same data to this endpoint.

Furthermore, the sampling window is 5 seconds, meaning values
advertised from a particular badge only change every 5 seconds.
(Even though the badge advertises every second.)

A _Duplicate_ is defined as one where _badge-id_ and _beacons_
are the same as another POST that arrived within the last 4.5 seconds.
(pi_id is not considered when determining duplicates.)

Duplicates will return status code 409. This is normal and expected behavior.
The more PIs there are within listening range of a given badge, the greater the
likelihood that any given POST will return a 409. For example, if there is only
one PI, you can expect 1/5 of its POSTs to return 201 and the rest to return
409. Similarly, if there are three PIs, you can expect 1/15 of the POSTs to
return 201 and the rest to return 409.


Curl Example
------------

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -30, "b": -35, "c": -40} }'



