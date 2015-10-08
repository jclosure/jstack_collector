

# get fuse pid
ps -ef | grep java

# run jstack against pid
jstack 10641

# get new entries in wrapper.log

# format as data

# send data

cat data/log/wrapper.log | grep "2015/09/28" | grep "Camel (mft-redesign)" > jstack_capture.lo

cat jstack_capture.log | mail -s stuff joel.holder@amd.com



# cat data/log/wrapper.log | grep "2015/09/28 18:47" |  grep "Camel (mft-redesign)"  | wc -l
# cat data/log/wrapper.log | grep "2015/09/28 18:47" | wc -l

# cat data/log/wrapper.log | grep "2015/09/28 18:47"
