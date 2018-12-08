#! /bin/bash

for i in {1..10000}; do

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"ip_address":"1.1.1.1", "badge_id":"2", "badge_strength":-71, "pi_id":"2", "position": 2, "motion": 2, "beacons":{"BIP001":-50}}'
    sleep 6

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"ip_address":"1.1.1.1", "badge_id":"2", "badge_strength":-71, "pi_id":"2", "position": 2, "motion": 2, "beacons":{"unknown-1":-50}}'
    sleep 6

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"ip_address":"1.1.1.1", "badge_id":"2", "badge_strength":-70, "pi_id":"1", "position": 1, "motion": 2}'
    sleep 6
done


