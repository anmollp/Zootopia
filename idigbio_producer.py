import argparse
from kafka import KafkaProducer
import json
import subprocess
import shlex

parser = argparse.ArgumentParser(description='Start a kafka producer')
parser.add_argument("--bootstrap-servers", nargs='+', metavar='0.0.0.0', type=str,
                    help="Space separated broker ip addresses")
args = parser.parse_args()
args_dict = vars(args)
brokers = list(map(lambda x: x + ":9092", args_dict.get('bootstrap_servers', 'localhost')))

producer = KafkaProducer(key_serializer=str.encode,
                         bootstrap_servers=",".join(brokers))

command1 = "preston track --seed https://idigbio.org"
command2 = "./clean-cache"
command3 = "preston json-stream"

# invoke process
process1 = subprocess.Popen(shlex.split(command1), shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
process2 = subprocess.Popen(shlex.split(command2), shell=False, stdin=process1.stdout, stdout=subprocess.PIPE)
process3 = subprocess.Popen(shlex.split(command3), shell=False, stdin=process2.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

#process1.stdout.close()
#process2.stdout.close()

while True:
    output = process3.stdout.readline()

    if process3.poll() is not None:
        break
    if output:
        producer.send('idigbio', key='https://idigbio.org', value=output.strip())
rc = process3.poll()
print(rc)
