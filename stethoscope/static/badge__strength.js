var initiateBadgeStrength = function(badgeId){
    'use strict'
    var $locationDiv = document.getElementById('strength-list')

    var fetchBadgeStrength = function(){
        var request = new XMLHttpRequest()
        var uri = '/badges/' + badgeId + '/strength_history'

        request.open('GET', uri, true)

        request.onload = function() {
            var payload
            // Success!
            payload = JSON.parse(this.response)
            displayBadgeStrength(payload)
        }

        request.onerror = function() {
            var errorObject = {'error': 'Check your Internet Connetion'}
            displayBadgeStrength(errorObject)
        }

        request.send()
    }

    var displayBadgeStrength = function(payload){
        var pretty = JSON.stringify(payload, null, 2)
        $locationDiv.innerHTML = '<pre>' + pretty + '</pre>'
    }

    var fetchBadgeStrengthPeriodically = function(){
        fetchBadgeStrength()
        setTimeout(fetchBadgeStrengthPeriodically, 1000)
    }

    fetchBadgeStrengthPeriodically()

}
