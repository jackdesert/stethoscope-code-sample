#! /bin/bash

for i in {1..10000}; do
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"1", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"3", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"4", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"5", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"6", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"7", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"8", "beacons":{"a": -30, "b": -35, "c": -40} }'
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"9", "beacons":{"a": -30, "b": -35, "c": -40} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -34, "b": -38, "c": -52} }'
    sleep 2

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -34, "b": -38, "d": -45} }'
    sleep 4
done


