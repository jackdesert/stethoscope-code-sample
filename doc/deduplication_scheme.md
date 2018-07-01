Deduplication Scheme
====================

We expect to receive duplicate payloads in subsequent advertisements
because the badge transmits the same payload five times.

Goal: Only save the advertisement once.

Method: Only save record if no record with the same payload has been saved in the last dedup_period.

Background
----------

Advertisements are coming in at approximately 1-second interval
(See doc/measurement_window.md)
and the update window is 5 seconds, we want a deduplication scheme
that gives us good odds of eliminating duplicates.


Dedup Period
------------

A time of 4.5 seconds is chosen as the optimal dedup_period.

Let P_d be the dedup period
Let P_u be the update period
Let P_a be the advertisement interval
Let D_i be the delay of the initial advertisement in an update period.
Let D_f be the delay of the final   advertisement in an update period.


We choose P_d = P_u - 0.5 P_a
so that if abs(D_i - D_f) < 0.5
then duplicates will be properly identified by this scheme.


Dedup Key
---------

The dedup key is formed from the payload. If the payload is different,
the dedup key will be different.

Redis
-----

The plan is to shove a dedup key into redis with an expiration.
Then just check if the same dedup key exists in redis before saving new records.
