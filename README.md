# drainpipe
Persist Redis streams to CSV

## start consumer:
`docker run -it -v <LOG DIR>:/app/data --network host drainpipe <STREAM NAME PATTERN> <CSV FILE NAME>`

don't forget to escape * in pattern
