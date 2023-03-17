#!/bin/bash
sudo systemctl stop zookeeper.service
sudo systemctl stop kafka.service
stop-all.sh
$SPARK_HOME/sbin/stop-all.sh
