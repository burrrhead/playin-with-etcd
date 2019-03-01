# playin-with-etcd

This is a very simple set of files for playing with etcd

My environment is a windows 10 box.  You will need the following installed on your windows box.

Vagrant - http://www.vagrantup.com
Virtual Box - http://www.virutalbox.org
Python3 - https://www.python.org

I also use x410 which is a windows 10 x server which can be purchased from the Mircrosoft store.  This isn't necessary, but kind of fun.

clone this report into a directory on your windows box and cd to that directory

on you laptop or desktop, use git to clone this repository and cd to the directory

To build the vagrant file, other useful scripts and start the whole thing up execute the following

>python doit.py

if all works, a vagrantfile will be created, the python script will startup vagrant, download a virtual machine which I have configured from vagrantup.com, startup the vm, modify the /etc/hosts file, create ssh keys, clone and build etcd.

At the end you should have three machines running named box1, box2 and box3, each with etcd built but not running.

open three command boxes so that you can connect to each of the machines.  To ssh into box1, choose a command window, 
cd to the directory with the vagrantfile and type:

>vagrant ssh box1

that should ssh you into the vagrant machine box1.  etcd is in the subdirectory etcd.  

The doit.py script created a shell script which will startup etcd in a clustered mode. It expects etcd to be run on all the boxes.   To startup etcd on box1 enter this command in the window connected to box1

>/vagrant/etcd-box1.sh

you should see lots of log messages, many telling you that it cannot connect to other hosts.  In the other command windows, ssh to the other boxes and execute the box specific etcd startup script.

As you start etcd on the other boxes, you should see the log files show that the etcd are finding each other and forming a cluster.  

When you are finished virtual box environment, just open a command window, go to the directory with the vagrantfile and enter the command

>vagrant halt

This will kill all the virtual machines. 

You do not need to run doit.py again if you do not wish to.  To restart the virtual boxes, open a command window and go to the directory with the vagrant file and enter the command

> vagrant up

That will start all the virtual machines. You need to ssh in and start etcd 

The etcd config starts has the daemon listen for clients on both localhost and the hosts IP address.  Say you are box1 the command

> etcd/bin/etcdctl member status

will resolve to localhost.  This makes it easy to play but you should really use the --endpoints command line argumet to connect to the network port

> etcd/bin/etcdctl --endpoints 192.168.50.2:2379,129.168.50.3:2379 member status

will use the network port.  If the etcd cluster is up, and you say, kill the etcd on box1 (192.168.50.2), the second command will correctly try to connect to the second host. 

The cluster works just fine running on two of the three nodes, so you can leave it down on one of the boxes and use the other to play with the cluster. Or modify the doit.py and create boxes which aren't in the cluster.  

etcdctl is a utilty control program which exercises the cluster.  Read the doc, but very easy to show a distributed lock working with a command like

> etcdctl lock stan

Open a couple of cmd windows and ssh to two of the nodes and try it.  The first will acquire the lock, the second will block.  When you kill the first, the second will acquire the lock.  Just read the docs to see what you can do. 