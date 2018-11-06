#! /bin/bash

for i in {1..10000}; do
    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"ip_address": "localhost", "badge_id":"2", "pi_id":"1", "position": 1, "motion": 2, "beacons":{"BIP003": -31, "BIP010": -36, "BIP020": -42, "BIP022": -57, "BIP036": -58} } '
    sleep 1


    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"ip_address": "localhost", "badge_id":"2", "pi_id":"1", "position": 1, "motion": 2, "beacons":{"BIP003": -52, "BIP010": -16, "BIP020": -17, "BIP022": -27, "BIP036": -42} }'
    sleep 1

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"ip_address": "localhost", "badge_id":"2", "pi_id":"1", "position": 1, "motion": 2, "beacons":{"BIP003": -18, "BIP010": -31, "BIP020": -49, "BIP022": -47, "BIP036": -40} }'
    sleep 1

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"ip_address": "localhost", "badge_id":"2", "pi_id":"1", "position": 1, "motion": 2, "beacons":{"BIP003": -40, "BIP010": -45, "BIP020": -30, "BIP022": -22, "BIP036": -35} }'
    sleep 1

    curl -k -X POST -H "Content-Type:application/json"  -i https://bip-stethoscope.elitecare.com/rssi_readings   -d '{"ip_address": "localhost", "badge_id":"2", "pi_id":"1", "position": 1, "motion": 2, "beacons":{"BIP003": -32, "BIP010": -45, "BIP020": -50, "BIP022": -82, "BIP036": -42} }'
    sleep 1
done


