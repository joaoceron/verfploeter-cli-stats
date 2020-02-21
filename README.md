# verfploeter-cli-stats
Script used to extract and summarize info from our anycast measurement tool (verfploeter).
<pre>

optional arguments:
  -h, --help            show this help message and exit
  --version             print version and exit
  -v, --verbose         print info msg
  -d, --debug           print debug info
  -q, --quiet           ignore animation
  -f [FILE], --file [FILE]
                        Verfploeter measurement output file
  -n, --normalize       remove inconsistency from the measurement dataset and
                        rebuild geolocation
  -g GEO [GEO ...], --geo GEO [GEO ...]
                        geo-location database - IP2Location (BIN)
  --hitlist HITLIST [HITLIST ...]
                        IPv4 hitlist - used to find unknown stats
  -s [SOURCE], --source [SOURCE]
                        Verfploeter source pinger node to be inserted as
                        metadata
  -b [BGP], --bgp [BGP]
                        BGP policy to be inserted as metadata
  -w WEIGHT [WEIGHT ...], --weight WEIGHT [WEIGHT ...]
                        File used to weight the /24. Use the SIDN load file.
  --csv                 print server load distribution using csv
  
                        </pre>
