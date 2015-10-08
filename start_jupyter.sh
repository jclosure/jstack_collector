
#ipython notebook --ip `/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`
ipython notebook --ip '*'
