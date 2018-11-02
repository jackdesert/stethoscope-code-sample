#! /bin/bash

for i in {1..10000}; do
    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"ip_address":"1.1.1.1", "badge_id":"2", "pi_id":"1", "beacons":{"BIP003": -30, "BIP010": -35, "BIP020": -40, "BIP022": -42, "BIP036": -50} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"ip_address":"1.1.1.1", "badge_id":"2", "pi_id":"2", "beacons":{"BIP003": -34, "BIP010": -38, "BIP020": -52, "BIP022": -53, "BIP036": -54} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"ip_address":"1.1.1.1", "badge_id":"2", "pi_id":"2", "beacons":{"BIP003": -34, "BIP010": -37, "BIP020": -45, "BIP022": -60, "BIP036": -63} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"ip_address":"1.1.1.1", "badge_id":"2", "pi_id":"2", "beacons":{"BIP003": -41, "BIP010": -42, "BIP020": -52, "BIP022": -60, "BIP036": -63} }'
    sleep 1

    curl -X POST -H "Content-Type:application/json"  -i http://localhost:6540/rssi_readings   -d '{"badge_id":"2", "pi_id":"2", "beacons":{"BIP003": -39, "BIP010": -42, "BIP020": -62, "BIP022": -70, "BIP036": -63} }'
    sleep 1
done


