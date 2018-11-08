Benchmarks
==========

Index on badge_id
-----------------

With 500,000 rssi_readings

Postgres
  location: 0.6 seconds

Sqlite:
  location: 20 seconds, sometimes timing out


Index on badge_id and timestamp
-------------------------------
With 500,000 rssi_readings

Postgres
  location: 0.3 seconds



Index on timestamp (Winner)
---------------------------

With 500,000 rssi_readings

Postgres
  location: 0.3 seconds
