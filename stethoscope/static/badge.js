/* http://youmightnotneedjquery.com/
 *
 */



/* globals TimeSeries */
/* globals SmoothieChart */



var initiateBadgeSmoothie = function(id, serverTime, initialMaxId){
    'use strict'
    var smoothie = new SmoothieChart(

        {millisPerPixel:24,
         //interpolation:'step', // step|bezier|linear
         scrollBackwards:true,
         grid:{strokeStyle:'#e93a3a'},
         tooltip:true,
         //responsive: true,
         labels: {fontSize: 20, // large labels
                  precision: 0}, // 0 for no values after decimal
         timestampFormatter: function(t){return ''},
         horizontalLines:[{color:'#ffffff',lineWidth:1,value:0},
                          {color:'#880000',lineWidth:2,value:3333},
                          {color:'#880000',lineWidth:2,value:-3333}]
        }
        //{ grid: { strokeStyle: '#baa' }}
        // {grid: { strokeStyle:'rgb(125, 0, 0)', fillStyle:'rgb(60, 0, 0)',
        //  lineWidth: 1, millisPerLine: 250, verticalSections: 6, },
        //  labels: { fillStyle:'rgb(60, 0, 0)' }}

    )
    var serverTimeInteger = new Date(serverTime).getTime()
    var jsTime = new Date().getTime()
    var timeDelta = serverTimeInteger - jsTime

    var lines = {}
    //var line1 = new TimeSeries()
    //var line2 = new TimeSeries()
    var delay = 7000

    var maxId = initialMaxId

    var colorGenerator = function(){
        var index = 0,
            colors = ['#fffac8',
                      '#0082c8',
                      '#aa6e28',
                      '#46f0f0',
                      '#3cb44b',
                      '#808080',
                      '#e6beff',
                      '#f032e6',
                      '#800000',
                      '#aaffc3',
                      '#000080',
                      '#808000',
                      '#f58231',
                      '#fabebe',
                      '#911eb4',
                      '#e6194b',
                     ],
            length = colors.length,
            assignedColors = {}

        var newColor = function(beaconId){
            var indexToUse,
                assignedColor = assignedColors[beaconId]

            if (assignedColor === undefined){
                indexToUse = index % length
                assignedColor = colors[indexToUse]
                assignedColors[beaconId] = assignedColor
                index += 1
            }

            return assignedColor
        }

        return { newColor: newColor }
    }()

    var keysFromObject = function(obj){
        var output = []
        for (var key in obj){
            if (obj.hasOwnProperty(key)){
                output.push(key)
            }
        }
        return output
    }

    var loadPacket = function(packet){
        var timestamp = new Date(packet.timestamp).getTime()
        var timestampToUse = timestamp - timeDelta
        var fakeTimestamp = new Date().getTime()
        var beaconIds = keysFromObject(packet.beacons)

        // Set maxId
        maxId = Math.max(maxId, packet.id)
        beaconIds.forEach(function(beaconId){
            var line = lines[beaconId],
                add = false,
                lastTimestamp,
                allowableGapInMilliseconds = 6500,
                newColor

            if (line === undefined){
                add = true
            }else{
                // TODO Remove Nested If Statement
                lastTimestamp = line.data.slice(-1)[0][0]
                if (Math.abs(lastTimestamp - timestampToUse) > allowableGapInMilliseconds){
                    add = true
                }
            }

            if (add){
                lines[beaconId] = new TimeSeries()
            }

            line = lines[beaconId]

            if(add){
                newColor = colorGenerator.newColor(beaconId)
                //console.log(newColor)
                smoothie.addTimeSeries(line, {
                                              strokeStyle: newColor,
                                              lineWidth: 3,
                                              tooltipLabel: beaconId
                                             })
            }

            line.append(timestampToUse, packet.beacons[beaconId])


        })


    }
    var appendData = function(){
        var request = new XMLHttpRequest()
        var uri = '/badges/' + id + '/fetch?after=' + maxId

        request.open('GET', uri, true)

        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                // Success!
                var data = JSON.parse(this.response)
                data.forEach(function(packet){
                    loadPacket(packet)
                    //console.log(packet)
                })

            } else {
                // We reached our target server, but it returned an error

            }
        }

        request.onerror = function() {
          // There was a connection error of some sort
        }

        request.send()
    }

    smoothie.streamTo(document.getElementById("mycanvas"), delay)

    // Data

    // Add a random value to each line every second
    setInterval(function() {
        appendData()
        //line1.append(new Date().getTime(), Math.random())
        //line2.append(new Date().getTime(), Math.random())
    }, 1000)

    // Add to SmoothieChart
    //smoothie.addTimeSeries(line1)
    //smoothie.addTimeSeries(line2)


}
