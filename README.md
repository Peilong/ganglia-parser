ganglia-parser
==============

Parser to retrieve and plot Ganglia metrics from an EC2 cluster

--------------
How to use:

1. Configure the "target.conf" file with the parameters required 
in each section. Here is a simple example:
	[target]
	dns=ec2-54-221-160-93.compute-1.amazonaws.com

	[option]
	metrics=cpu_system,dfs.FSNamesystem.PendingDeletionBlocks,dfs.datanode.blocks_verified

This file contains the DNS server where Ganglia gmetad process
is running and the metrics option. By default, the metrics contains
all Ganglia metrics, which might not be necessary in some cases.
The internal IPs of the cluster nodes will be determined by parsing
the Ganglia web page.

2. Run script: ./gangliaParser.py target.conf
or python gangliaParser.py target.conf

3. Two kinds of files will be automatically saved to a timestamped
directory. One is JSON files that contains the wanted metric data,
the other is png figures that visualized the JSON data.

4. Limitation:
The parser can only parse the latest one-hour metrics. So it must be
executed right after the workload under study completes.

