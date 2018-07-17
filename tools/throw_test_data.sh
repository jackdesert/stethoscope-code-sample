#! /bin/bash

for i in {1..10000}; do
    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -30, "b": -35, "c": -40} }'
    sleep 1

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -34, "b": -38, "c": -52} }'
    sleep 2

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"badge_id":"1", "pi_id":"2", "beacons":{"a": -34, "b": -38, "d": -45} }'
    sleep 4
done


