/home/vagrant/etcd/bin/etcd --name infra3 --initial-advertise-peer-urls http://192.168.50.4:2380 \
  --listen-peer-urls http://192.168.50.4:2380 \
  --listen-client-urls http://192.168.50.4:2379,http://127.0.0.1:2379 \
  --advertise-client-urls http://192.168.50.4:2379 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-cluster infra1=http://192.168.50.2:2380,infra2=http://192.168.50.3:2380,infra3=http://192.168.50.4:2380 \
  --initial-cluster-state new



