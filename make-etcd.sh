#! /bin/bash
sudo -u vagrant git clone https://github.com/etcd-io/etcd 
cd etcd 
sudo -u vagrant make build 
sudo -u vagrant make build-functional 

