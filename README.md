# Zootopia
A distributed streaming data processing pipeline.

## Description:
Open source technologies used and their versions:
| Technology | Version |
|------------|---------|
| Java       | 11      |
| Kafka      | 3.1.0   |
| Spark      | 3.2.1   |
| Hadoop     | 3.2.3   |    
| Preston    | 0.3.5   |
| Python     | 3.9.0   |

## High Level System Design
![image](https://user-images.githubusercontent.com/19925448/225933206-5e5c0b64-a4f0-4640-be3d-b1f870296689.png)



1. Firstly a cluster of 3 nodes has to be set up with an Ubuntu operating system on cloud lab.
2. Since the project is JVM heavy, Java 11 needs to be installed.
3. To exploit parallel processing we need to install Kafka and Spark appropriate versions.
4. For the persistence layer we will be using HDFS and it would require us using hadoop.
5. Python is the primary language used to develop the spark code.
6. Libraries like kafka-python, web.py need to be installed.
7. When configuring kafka, make sure the broker id is different for different nodes.
8. Set max.retention.minutes = 2 and set the zookeeper address correctly in server.properties file for kafka. Also need to carefully set the replication factor, number of partitions and number of in sync replicas for topics.
9. Setup systemd services for zookeeper and kafka brokers to startup automatically on
system boot.
10. For spark, we need to create our own spark-env.sh file that includes spark master
details and details for pyspark.
11. Also spark needs to know the master and slave ip addresses inorder to run
distributedly.
12. Our spark cluster runs as a standalone server.
13. Spark submit is used to start the spark processing of streaming records from kafka in
client mode with spark structured streaming jars passed as arguments.
14. While configuring hdfs, we need to configure the following files correctly namely
core-site.xml, hdfs-site.xml, yarn-site.xml, hadoop-env.sh, masters and slaves.
15. For all of the distributed processes to run properly a passwordless ssh has to be set up
amongst these nodes.
16. Therefore the master node’s public key has to be present in all the slave server node’s
authorised_keys file under the .ssh/ folder.
17. Finally when all these steps are taken care of we can spark submit our consumer job
and subsequently we can start the producer processes that also takes care of starting
preston streamer.
18. As I am using a trigger process interval of 2 minutes , windows of data pertaining to
kingdom, species and source related records are processed by spark and stored on hdfs
in a distributed fashion.
19. To control the pipeline and to visualize the data processed I use a web server
developed in web.py that exposes APIs to achieve the same.
High Level System design:
List of scripts and their description:
20. consumer.py: contains spark code that consumes data from all three topics using spark
structured streaming creating windows of required data every 2 minutes.
21. gbif_producer.py: python code that starts gbif stream and streams it to a producer that
pushes data to the kafka broker assigned to it to a topic called gbif, takes broker ip as
input.
22. obis_producer.py: python code that starts an obis stream and streams it to a producer
that pushes data to the kafka broker assigned to it to a topic called gbif, takes broker ip
as input.
23. idigbio_producer.py: python code that starts an idigbio stream and streams it to a
producer that pushes data to the kafka broker assigned to it to a topic called idigbio,
takes broker ip as input.
24. webserver.py: this code deploys a web server that exposes APIs to read processed
data residing on HDFS.
25. start-script.sh: a shell script thats starts zookeeper, kafka, hdfs and spark master and
slaves.
26. stop-script.sh: shell script that stops zookeeper, kafka, hdfs and spark.
27. start-slave-script.sh: shell script that starts kafka broker on a slave.
28. stop-slave-script.sh: shell script that stops kafka broker running on a slave.
29. stop-stream.sh: stops preston streams streaming data to kafka.
30. zookeeper.service: as soon as the master node is powered and network is available,
start the zookeeper using this systemd service profile.
31. kafka.service: as soon as a node is powered and network is available, start the kafka
broker using this systemd service profile.

# Supported APIs:
● curl -X GET http://128.105.144.46:10001/addSource?url=(url)
  
● curl -X GET http://128.105.144.46:10001/addSource?url=(url)
  
● curl -X GET http://128.105.144.46:10001/addSource?url=(url)
  
● curl -X GET http://128.105.144.46:10001/listSources
  
● curl -X GET http://128.105.144.46:10001/count?by=totalSpecies
  
● curl -X GET http://128.105.144.46:10001/count?by=kingdom
  
● curl -X GET http://128.105.144.46:10001/count?by=source
  
● curl -X GET http://128.105.144.46:10001/window?id=(int)
