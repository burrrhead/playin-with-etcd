#! /bin/bash
git clone https://github.com/etcd-io/etcd 
cd etcd 
make build 
make build-functional 

