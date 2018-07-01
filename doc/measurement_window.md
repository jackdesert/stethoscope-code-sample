Measurement Window
==================

from Mark:
  We can't be sure the Badge will pick up signals from all nearby beacons
  in every 1-second period, so we need a longer interval.  Let's assume
  the badge listens over 5 seconds and remembers the 3 strongest signal
  RSSIs along with their IDs.  This dataset is "held" and repeatedly
  transmitted by the badge every 1 second, until the next update is ready
  5 seconds later.)


Update Window
-------------

From the above, the update window is taken to be 5 seconds.
This means that every 5 seconds the data being advertised has the
opportunity to change.


Advertisement Interval
----------------------

The advertisement interval is assumed to be approximately 1 second


Random Delay
------------

According to http://www.argenox.com/a-ble-advertising-primer/

"The random delay is a pseudo-random value from 0ms to 10ms that is automatically added"


Network Latency
---------------

The time it takes to get from the badge, through the pi, all the way
to the stethoscope. This will fluctuate with time.


Total Delay/Latency
-------------------


= Network Latency + Random Delay

