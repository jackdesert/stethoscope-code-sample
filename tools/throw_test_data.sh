#! /bin/bash

for i in {1..10000}; do
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"2", "pi_id":"1", "beacons":{"a": -30, "b": -35, "c": -40, "d": -42, "e": -50} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"2", "pi_id":"2", "beacons":{"a": -34, "b": -38, "c": -52, "d": -53, "e": -54} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"2", "pi_id":"2", "beacons":{"a": -34, "b": -37, "c": -45, "d": -60, "e": -63} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"2", "pi_id":"2", "beacons":{"a": -41, "b": -42, "c": -52, "d": -60, "e": -63} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"2", "pi_id":"2", "beacons":{"a": -39, "b": -42, "c": -62, "d": -70, "e": -63} }'
    sleep 1
done


