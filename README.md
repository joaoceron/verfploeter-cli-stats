# verfploeter-cli-stats
Script used to extract and summarize info from our anycast measurement tool (verfploeter).
``
usage: vp-cli.py [options]

optional arguments:
  -h, --help            show this help message and exit
  --version             print version and exit
  -v, --verbose         print info msg
  -d, --debug           print debug info
  -q, --quiet           ignore animation
  -f [FILE], --file [FILE]
                        Verfploeter measurement output file
  -n, --normalize       remove inconsistency from the measurement dataset
  -g GEO [GEO ...], --geo GEO [GEO ...]
                        geo-location database - IP2Location (BIN)
  --hitlist HITLIST [HITLIST ...]
                        IPv4 hitlist - used to find unknown stats
  -s [SOURCE], --source [SOURCE]
                        Verfploeter source pinger node
  -b [BGP], --bgp [BGP]
                        BGP status
  --stats {load,block,country}
                        show stats from the vp measurement. Potential options:
                        load (default) block country
