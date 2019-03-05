#! /bin/bash
sudo -H -u vagrant git clone https://github.com/etcd-io/etcd 
cd etcd
sudo -H -u vagrant make build 
sudo -H -u vagrant make build-functional 

