Load Testing
============

Results First
-------------

In short, on an EC2 nano box running waitress via systemd,
this app stands up to 400 total requests/second, of which 20/second
write to the database. (5% unique)

This is enough to collect data in 5 houses simultaneously. 



Generate Vegeta Targets
-----------------------


Call `python3 generate_load_test.py` with the appropriate values for NUM_BADGES.
That will generate a file named targets.txt, and for each dinstinctive payload
reference will add a corresponding file in vegeta_data.

The python module will also tell you what type of run you have prepared:

    $ python3 generate_load_test.py 
    
    24000 emissions generated in targets.txt
      100 badges
      4 pis
      60 seconds
    
      1 out of 20 is unique
    
      400 API hits per second
      20 database writes per second
    Invoke like this:
    vegeta attack -targets=targets.txt -rate=400 -duration=60s | vegeta report


The above test case (a fair test of running 4 pis per house, 20 badges per houes, 
5 total houses) means the API will be hit 400 times per second, but only 20/second
will be database writes. Note it says "1 out of 20 is unique". 


Run Vegeta Against Targets
--------------------------


Running this gives these results:

    $ vegeta attack -targets=targets.txt -rate=400 -duration=60s | vegeta report
    Requests      [total, rate]            24000, 400.01
    Duration      [total, attack, wait]    1m0.003154171s, 59.998717406s, 4.436765ms
    Latencies     [mean, 50, 95, 99, max]  3.843311ms, 1.702055ms, 10.179838ms, 36.348653ms, 275.300737ms
    Bytes In      [total, mean]            806274, 33.59
    Bytes Out     [total, mean]            2448920, 102.04
    Success       [ratio]                  5.00%
    Status Codes  [code:count]             201:1199  409:22801  
    Error Set:
    409 Conflict
    

Note the following:

* We get the success ratio we expect (5% == 1/20). 
* We get lots of 201 response and the rest 409, which means "duplicate".



What if we double that?
-----------------------


If we increase NUM_BADGES from 100 to 200 (simulating 10 houses, each with four PIs),
there will be many errors in /var/log/nginx/error.log that look like this:

    2018/07/12 08:50:49 [alert] 9667#9667: 768 worker_connections are not enough

The next step if increased performance were required would be to expermiment with 
setting ulimit to higher than the default value of 1024. 

