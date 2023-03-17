ps -ef | grep 'preston' | grep -v grep | awk '{print $2}' | xargs -r kill -9

