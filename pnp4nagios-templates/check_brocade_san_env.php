<?php
#
# Copyright (c) 2010 Tomas Edwardsson, Opin Kerfi (tommi@ok.is)
# Plugin: check_brocade_env
#

# Which colors do we have to pick from ?
$colors = array("#0000FF", "#00FF00", "#FF0000", "#555555", "#00FFFF", "#FF00FF", "#6666FF");

# Initialize reference with counts and graph numbers
$type = array (
	"FAN" => array("count" => 0, "graph_num" => 1),
	"SLO" => array("count" => 0, "graph_num" => 2));


# Loop through all data sources
foreach ($DS as $i) {

	# Create some easy shorthand variables
	$shortname = substr($NAME[$i], 0, 3);
	$graph_num = $type[$shortname]["graph_num"];
	$count = $type[$shortname]["count"];


	# 2 different graph types, FAN Speed and Temperature
	## FAN
	if ($shortname == "FAN") {
		$ds_name[$graph_num] = "FAN Speed";
		if ($count == "0") {
			$opt[$graph_num] = "--vertical-label \"RPM\"  --title \"FAN Speed on $hostname\" ";
		}
	## SLO (starts with SLOT)
	} else {
		$ds_name[$graph_num] = "Temperature";
		if ($count == "0") {
			$opt[$graph_num] = "--vertical-label \"Celsius\"  --title \"Temperature for $hostname\" ";
		}
	}

	# Each graph has its own counter
	$type[$shortname]["count"]++;

	# Beautify sensor names
	$sensor_name = "";
	if ($shortname == "FAN") {
		$sensor_name = "FAN #" . substr($NAME[$i], -1, 1);
	} else {
		$sensor_name = "Temp Sensor #" . substr($NAME[$i], -1, 1);
	}

	# LINE graph
	$def[$graph_num] .=  "DEF:var$count=$rrdfile:$DS[$i]:AVERAGE " ;
	$def[$graph_num] .= "LINE2:var$count" . $colors[$count] . ":\"$sensor_name \" " ;

	$def[$graph_num] .= "GPRINT:var$count:LAST:\"% 4.0lf last \" " ;
	$def[$graph_num] .= "GPRINT:var$count:MIN:\"%4.0lf min \" " ;
	$def[$graph_num] .= "GPRINT:var$count:MAX:\"%4.0lf max \" " ;
	$def[$graph_num] .= "GPRINT:var$count:AVERAGE:\"%6.2lf avg \\n\" " ;
}

?>
