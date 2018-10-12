var initiateBadgeLocation = function(badgeId){
    'use strict'
    var $locationDiv = document.getElementById('location-list')

    var fetchLocation = function(){
        var request = new XMLHttpRequest()
        var uri = '/badges/' + badgeId + '/location'

        request.open('GET', uri, true)

        request.onload = function() {
            var payload
            // Success!
            payload = JSON.parse(this.response)
            displayLocation(payload)
        }

        request.onerror = function() {
            var errorObject = {'error': 'Check your Internet Connetion'}
            displayLocation(errorObject)
        }

        request.send()
    }

    var displayLocation = function(payload){
        var pretty = JSON.stringify(payload, null, 2)
        $locationDiv.innerHTML = '<pre>' + pretty + '</pre>'
    }

    var fetchLocationPeriodically = function(){
        fetchLocation()
        setTimeout(fetchLocationPeriodically, 1000)
    }

    fetchLocationPeriodically()

}
