<?php
#
# Copyright (c) 2006-2008 Joerg Linge (http://www.pnp4nagios.org)
# Plugin: check_icmp [Multigraph]
# $Id: check_ping.php 553 2008-11-07 21:33:50Z Le_Loup $
#
foreach ($DS as $i) {
	if ($NAME[$i] == "rta") {
	# RTA
	#
		$ds_name[$i] = "Round Trip Times";
		$opt[$i] = "--vertical-label \"RTA\"  --title \"Ping times for $hostname / $servicedesc\" ";
		$def[$i] =  "DEF:var1=$rrdfile:$DS[$i]:AVERAGE " ;
		$def[$i] .=  "CDEF:sp1=var1,100,/,12,* " ;
		$def[$i] .=  "CDEF:sp2=var1,100,/,30,* " ;
		$def[$i] .=  "CDEF:sp3=var1,100,/,50,* " ;
		$def[$i] .=  "CDEF:sp4=var1,100,/,70,* " ;



		$def[$i] .= "AREA:var1#FF5C00:\"Round Trip Times \" " ;
		$def[$i] .= "AREA:sp4#FF7C00: " ;
		$def[$i] .= "AREA:sp3#FF9C00: " ;
		$def[$i] .= "AREA:sp2#FFBC00: " ;
		$def[$i] .= "AREA:sp1#FFDC00: " ;


		$def[$i] .= "GPRINT:var1:LAST:\"%6.2lf $UNIT[$i] last \" " ;
		$def[$i] .= "GPRINT:var1:MAX:\"%6.2lf $UNIT[$i] max \" " ;
		$def[$i] .= "GPRINT:var1:AVERAGE:\"%6.2lf $UNIT[$i] avg \\n\" " ;
		$def[$i] .= "LINE1:var1#000000:\"\" " ;


		if($WARN[$i] != ""){
  			$def[$i] .= "HRULE:".$WARN[$i]."#000000:\"Warning ".$WARN[$i]."%% \" " ;
		}
		if($CRIT[$i] != ""){
  			$def[$i] .= "HRULE:".$CRIT[$i]."#FF0000:\"Critical ".$CRIT[$i]."%% \" " ;
		}

	} else {
	#
	# Packets Lost
		$ds_name[$i] = "Packets Lost";
		$opt[$i] = "--vertical-label \"Packets lost\" -l0 -u105 --title \"Packets lost for $hostname / $servicedesc\" ";

		$def[$i] = "DEF:var1=$rrdfile:$DS[$i]:AVERAGE " ;
		$def[$i] .=  "CDEF:sp1=var1,100,/,12,* " ;
		$def[$i] .=  "CDEF:sp2=var1,100,/,30,* " ;
		$def[$i] .=  "CDEF:sp3=var1,100,/,50,* " ;
		$def[$i] .=  "CDEF:sp4=var1,100,/,70,* " ;


		$def[$i] .= "AREA:var1#FF5C00:\"Packets lost \" " ;
		$def[$i] .= "AREA:sp4#FF7C00: " ;
		$def[$i] .= "AREA:sp3#FF9C00: " ;
		$def[$i] .= "AREA:sp2#FFBC00: " ;
		$def[$i] .= "AREA:sp1#FFDC00: " ;


		$def[$i] .= "GPRINT:var1:LAST:\"%6.2lg $UNIT[$i] last \" " ;
		$def[$i] .= "GPRINT:var1:MAX:\"%6.2lg $UNIT[$i] max \" " ;
		$def[$i] .= "GPRINT:var1:AVERAGE:\"%6.2lg $UNIT[$i] avg \\n\" " ;
		$def[$i] .= "LINE1:var1#000000: " ;
		$def[$i] .= "HRULE:100#000000:\"\" " ;
		if($WARN[$i] != ""){
  			$def[$i] .= "HRULE:".$WARN[$i]."#FFFF00:\"Warning ".$WARN[$i]."%% \" " ;
		}
		if($CRIT[$i] != ""){
  			$def[$i] .= "HRULE:".$CRIT[$i]."#FF0000:\"Critical ".$CRIT[$i]."%% \" " ;
		}
	}
}

?>
