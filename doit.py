import subprocess
boxes = (( "client","192.168.50.2", "box1"),
         ( "client","192.168.50.3", "box2" ),
         ( "client","192.168.50.4", "box3"))




def makeEtcHosts( boxes ):

    res = "  config.vm.provision \"shell\", inline: <<-SHELL \n"
    for box in boxes:
        res += "    echo \"{0}    {1}  {1} \" >> /etc/hosts \n".format( box[1], box[2])
    res += "  SHELL\n"
    return res

# a text string to hold the common vagrant configuration stuff. If I knew Ruby I'd probably just do this in Ruby
# and not have to worry about python. One day

commonBoxFileContents = """
# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

#  config.vm.box = "ubuntu/bionic64"
  config.vm.box = "compstan/bionicPythonGo"
  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  #config.vm.synced_folder "../data", "/vagrant_data"

  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  config.vm.provision "shell", path: "make-etcd.sh", binary: "true"
  config.vm.provision "shell", inline: <<-SHELL

  
    # generate ssh keys for this host and copy to a common location so that we can distribute to all the vms
    echo 'generate ssd keys'
    (cd /home/vagrant; sudo -u  vagrant ssh-keygen -q -t rsa -b 4096 -N "" -f /home/vagrant/.ssh/id_rsa )
    cat ~vagrant/.ssh/id_rsa.pub >> /vagrant/keys


SHELL
"""


dbBoxContents = """
  # dbbox is the databse.  install the server there and once again, note the fixed ip address
  config.vm.define "$hostname" do |$hostname|

    $hostname.vm.network "private_network", ip: "$ip"
    $hostname.vm.provision "shell", inline: <<-SHELL
      echo "$hostname" > /etc/hostname
      hostname $hostname
        
      # install foundationdb, this also starts a running instance
      apt-get install -f /vagrant/foundationdb-server_6.0.15-1_amd64.deb

      # by defualt the fdb.cluster file points to a local instance, and the server only listens on 
      # 127.0.0.1.  this command modifies the cluster file to refer to an ip address. 
      /usr/lib/foundationdb/make_public.py -a 192.168.50.3

      # now that the cluster file has changed need to stop then start the database server to pick up 
      # change
      service foundationdb stop
      service foundationdb start

      # copy the cluster file to a shared location so that we can use it on other boxes. 
      cp /etc/foundationdb/fdb.cluster /vagrant/fdb.cluster
    SHELL
  end
"""

clientBoxContents = """
  config.vm.define "$hostname" do |$hostname|

    $hostname.vm.network "private_network", ip: "$ip"
    $hostname.vm.provision "shell", inline: <<-SHELL
	echo "$hostname" > /etc/hostname
	hostname $hostname
    SHELL
  end
"""

# delete the keys file in the common area which is use to communicate ssh keys between the vm's


def runCommand ( cmd ) :
    print( "executing command: " + cmd + "\n" )
    ret = subprocess.run( cmd, shell=True )
    if ret.returncode :
        print( "error running: " + cmd + "\n" )
        exit( 1 )

#now we finally get to create the vagrant file. 

f = open( "vagrantfile", "w")
f.write( commonBoxFileContents )
f.write( makeEtcHosts( boxes ) )

# now iterate over the boxes and then write box specific command to the vagrant file. 
from string import Template
for box in boxes:
    if box[0] == "client":
        s = Template( clientBoxContents )
        f.write( s.substitute( ip= box[1], hostname=box[2] ) )
    if box[0] == "db" :
        s = Template( dbBoxContents )
        f.write( s.substitute( ip=box[1], hostname=box[2] ) )

f.write( "end\n")
f.close()

# now execute the commands.
runCommand("del keys")
runCommand("vagrant up" )

# now some post processing commands.  First get the ssh keys in place, then get the cluster file right, then build the go lib and finally do a quick test. 
for box in boxes:
    runCommand( Template("vagrant ssh $name -c \"cat /vagrant/keys >>.ssh/authorized_keys\" ").substitute(name=box[2]) ) 
    #runCommand( Template("vagrant ssh $name -c \"sudo cp /vagrant/fdb.cluster /etc/foundationdb/fdb.cluster\" ").substitute( name=box[2] ) )
    # couldn't get the go lib to build as root in part of provisioning so do here 
    #runCommand( Template("vagrant ssh $name -c \"cd /home/vagrant/foundationdb/bindings/go; ./fdb-go-install.sh install --fdbver release-6.0 \" ").substitute( name = box[2]))
         #runCommand( "vagrant ssh box1 -c \"cat /vagrant/keys >>.ssh/authorized_keys\" " ) 
    #runCommand( Template("vagrant ssh $name -c \"cp /vagrant/foo.go .; go run foo.go\" ").substitute( name = box[2]) )
