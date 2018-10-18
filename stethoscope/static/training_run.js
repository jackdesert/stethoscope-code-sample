var bindNewTrainingRun = function(){
    'use strict'
    var running = false,
        inProgressTrainingRunIds = [],
        inProgressBadgeIds = [],
        inProgressRoomId = null,
        startButton = document.getElementById('training-run-start-button'),
        startRuns = function(){
            var request = new XMLHttpRequest(),
                path = '/training_runs/bulk_start',
                payload

            // Set top-level-variables
            inProgressRoomId   = selectedRoomId()
            inProgressBadgeIds = selectedBadgeIds()

            payload = { badge_ids: inProgressBadgeIds,
                        room_id: inProgressRoomId }

            console.log('started')
            console.log('badgeIds', inProgressBadgeIds)
            console.log('roomId', inProgressRoomId)


            request.open('POST', path, true)

            request.onload = function() {
                var response,
                    responseHash
                if (this.status >= 200 && this.status < 400) {
                    // Success!
                    response = this.response
                    responseHash = JSON.parse(response)
                    running = true
                    inProgressTrainingRunIds = responseHash.training_run_ids
                    setButtonText()
                    // Fetch stats manually so user can see them immediately
                    fetchStats()
                } else {
                    displayErrorJson(this.response)
                }
            }

            request.onerror = function() {
                alert('Error starting training runs. Please check your network connection and click "Start" again.')
              // There was a connection error of some sort
            }

            request.setRequestHeader('Content-Type', 'application/json')
            request.send(JSON.stringify(payload))

        },

        endRuns = function(){
            var request = new XMLHttpRequest(),
                path = '/training_runs/bulk_end',
                payload = { training_run_ids: inProgressTrainingRunIds }

            request.open('POST', path, true)

            request.onload = function() {
                var response,
                    responseHash
                if (this.status >= 200 && this.status < 400) {
                    // Success!
                    response = this.response
                    displaySuccessString('You Rock')


                    console.log('stopped')
                    running = false
                    inProgressTrainingRunIds = []
                    inProgressBadgeIds = []
                    inProgressRoomId = null
                    setButtonText()

                } else {
                    displayErrorJson(this.response)
                }
            }

            request.onerror = function() {
                alert('Error saving training runs. Please check your network connection and click "End" again.')
              // There was a connection error of some sort
            }

            request.setRequestHeader('Content-Type', 'application/json')
            request.send(JSON.stringify(payload))

        },

        fetchStats = function(){
            var payload = { training_run_ids: inProgressTrainingRunIds,
                            room_id: inProgressRoomId },
                request = new XMLHttpRequest(),
                path = '/training_runs/bulk_stats'

            console.log('fetching stats')



            // Using POST so we can send a body
            request.open('POST', path, true)

            request.onload = function() {
                var response,
                    responseHash

                if (this.status >= 200 && this.status < 400) {
                    // Success!
                    response = this.response
                    responseHash = JSON.parse(response)
                    displayResultsTable()
                    setInProgressReadings(responseHash.in_progress)
                    setInProgressTotal(responseHash.in_progress_total)
                    setCompletedReadings(responseHash.completed)
                    setTotalReadings(responseHash.total)
                } else {
                    displayErrorJson(this.response)
                }
            }

            request.onerror = function() {
                console.log('Error fetching stats. Please check your network connection')
              // There was a connection error of some sort
            }


            request.setRequestHeader('Content-Type', 'application/json')
            request.send(JSON.stringify(payload))

        },

        doSomething = function(){
            clearDisplayedMessages()
            if (running){
                endRuns()
            }else{
                startRuns()
            }
        },

        selectedRoomId = function(){
            var selector = document.getElementById('room-id'),
                id = selector.value

            return id
        },

        selectedBadgeIds = function(){
            var elements = document.querySelectorAll('input[type="checkbox"]'),
                badgeIds = []

            elements.forEach(function(e){
                if (e.checked === true){
                    badgeIds.push(e.id)
                }
            })

            return badgeIds
        },

        displaySuccessString = function(msg){
            var div = document.getElementById('success-message')

            div.innerHTML = msg
        },


        displayErrorJson = function(msg){
            var div = document.getElementById('error-message'),
                innerMsg,
                messageToDisplay,
                msgMap = { 'Please supply badge_ids': 'Please select one or more badges',
                        'Please supply room_id':   'Please select a room' }

            if (msg === ''){
                div.innerHTML = ''
            }else{
                innerMsg = JSON.parse(msg).error
                messageToDisplay = msgMap[innerMsg] || innerMsg

                div.innerHTML = 'ERROR: ' + messageToDisplay
            }
        },

        clearDisplayedMessages = function(){
            displayErrorJson('')
            displaySuccessString('')
        },

        setButtonText = function(){
            var runningClass = 'start-button_running'

            if (running){
                startButton.value = 'End'
                startButton.classList.add(runningClass)
            }else{
                startButton.value = 'Start'
                startButton.classList.remove(runningClass)
            }

        },

        setTotalReadings = function(value){
            var div = document.getElementById('total-readings')
            div.innerHTML = value
        },

        setInProgressReadings = function(hash){
            // Expects `hash` in the format:
            // { <badgeId> : <integer>, ... }

            var div,
                badgeId
            for (badgeId in hash){
                if (hash.hasOwnProperty(badgeId)){
                    div = document.getElementById('num-readings-for-badge-' + badgeId)
                    div.innerHTML = hash[badgeId]
                }
            }
        },

        setInProgressTotal = function(total){
            var div = document.getElementById('in-progress-total')
            div.innerHTML = total
        },

        setCompletedReadings = function(value){
            var div = document.getElementById('completed-run-readings')
            div.innerHTML = value
        },

        displayResultsTable = function(){
            var table = document.getElementById('training-run-report-table')
            // class starts out as 'table hidden'.
            table.className = 'table'
        },

        removeStartButtonFocus = function(){


            // For a full list of event types: https://developer.mozilla.org/en-US/docs/Web/API/document.createEvent
            var event = document.createEvent('HTMLEvents'),
                footer = document.getElementById('footer')
            event.initEvent('blur', true, false)
            startButton.dispatchEvent(event)


        }



    startButton.addEventListener('click', doSomething)
    startButton.addEventListener('mouseout', removeStartButtonFocus)

    setInterval(function() {
        if (inProgressTrainingRunIds.length !== 0 ){
            fetchStats()
        }
    }, 5000)


}
