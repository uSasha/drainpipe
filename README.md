#### Drainpipe is a tool to persist messages from multiple Redis Streams to single CSV file on disk. 

### Usage: 
`docker run -v <LOCAL_DIR>:/app/data --network host usasha/drainpipe <PATTER_TO_MATCH_STREAMS> <CSV_FILE_NAME>`

e.g. `docker run -v /data:/app/data --network host usasha/drainpipe mystream_\* mystream.csv`
(don't forget to escape * in pattern)

Drainpipe will constantly searching for new streams matching pattern and save all *new* messages to CSV. 
Old messages will not be stored. 
First message in new stream will only initialize stream and also will not be dumped.

If you need more flexibility use ENV variables:
- redis_host
- redis_port
- idle_seconds: seconds to sleep between checks for new messages
- header: specify keys you want to store (e.g. 'user_id,item_id,stars'), 
drainpipe will add stream and timestamp fields
- consumer_group: useful when you want to use more than ane drainpipe on stream 
to store updates to more than one file (e.g. streams 1, 2, 3 -> small.csv; 2, 4, 6 -> even.csv)
- consumer_name: to be able to run multiple replicas of same drainpipes for scaling


## usage patterns:
Drainpipes could be scaled and work in groups for better performance.

Single stream to CSV file (single grainpipe/goup) st_1 -> st1.csv:

`drainpipe st_1 st1.csv`

Multiple streams to CSV file (single grainpipe/goup) st_1, st_2, st_3 -> st1-3.csv:

`drainpipe st_\* st1.csv`

Multiple streams to multiple CSV files (two grainpipes/goups) st_21, st_31, st_51 -> ones.csv; st_21, st_22, st_23 -> twos.csv:

`drainpipe st_\*1 st1.csv`

`drainpipe st_2\* st1.csv`
