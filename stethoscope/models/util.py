import requests
import pdb

def bip_rooms():
    uri = 'https://bip.elitecare.com/api/stethoscope/rooms_insecure'
    data = requests.get(uri, timeout=10)
    return data.json()


if __name__ == '__main__':
    bip_rooms()


