#!/bin/bash
sudo systemctl start zookeeper.service
sudo systemctl start kafka.service
start-all.sh
$SPARK_HOME/sbin/start-all.sh

