# gcs-loopback
Test steps and results of using loopback as gluster block

We use gcs project to create vms in the hypervisor. These VMs will be the kubernetes cluster nodes and also gluster cluster nodes.

## Setup Hypervisor

##### Hypervisor specs
OS: Centos 7.6  
RAM: 128 G RAM  
CPU: 24 core  

##### Setup disks on the hypervisor to be used by the kube VMs
Skip the below section if you already know how to create disks to attach to the Kube VMs.  
  
Mount the disks on the hypervisor
  ```
  $ rm -f /var/lib/libvirt/images/disk* #Caution do not delete other VMs' images
  $ mkdir -p /disks/kube{1..3}c
  $ mkdir -p /disks/kube{1..3}d
  
  $ mount -t xfs /dev/sdb /disks/kube1c
  $ mount -t xfs /dev/sdb /disks/kube1c
  $ mount -t xfs /dev/sde /disks/kube2c
  $ mount -t xfs /dev/sdf /disks/kube3c
  $ mount -t xfs /dev/sdg /disks/kube1d
  $ mount -t xfs /dev/sdh /disks/kube2d
  $ mount -t xfs /dev/sdi /disks/kube3d

  $ df -h
    /dev/sdb                        1.9T   35G  1.8T   2% /disks/kube1c
    /dev/sde                        1.9T   32G  1.8T   2% /disks/kube2c
    /dev/sdf                        1.9T   32G  1.8T   2% /disks/kube3c
    /dev/sdg                        1.9T   34M  1.9T   1% /disks/kube1d
    /dev/sdh                        1.9T   34M  1.9T   1% /disks/kube2d
    /dev/sdi                        1.8T   34M  1.8T   1% /disks/kube3d
  ```

Create 1.2 T disks to be used by VMs
  ```
  $ #rm -f /disks/kube??/disk* #Cleanup if required

  $ qemu-img create -f qcow2 /disks/kube1c/disk.qcow2 1300G
  $ qemu-img create -f qcow2 /disks/kube2c/disk.qcow2 1300G
  $ qemu-img create -f qcow2 /disks/kube3c/disk.qcow2 1300G
  $ qemu-img create -f qcow2 /disks/kube1d/disk.qcow2 1300G
  $ qemu-img create -f qcow2 /disks/kube2d/disk.qcow2 1300G
  $ qemu-img create -f qcow2 /disks/kube3d/disk.qcow2 1300G
  ```
Create a symlink in the deafult libvirt directory, so that the Vagrantfile can use these files as disks to the VMs:
  ```
  $ ln -s /disks/kube1c/disk.qcow2 /var/lib/libvirt/images/diskc1.qcow2
  $ ln -s /disks/kube1d/disk.qcow2 /var/lib/libvirt/images/diskd1.qcow2
  $ ln -s /disks/kube2c/disk.qcow2 /var/lib/libvirt/images/diskc2.qcow2
  $ ln -s /disks/kube2d/disk.qcow2 /var/lib/libvirt/images/diskd2.qcow2
  $ ln -s /disks/kube3c/disk.qcow2 /var/lib/libvirt/images/diskc3.qcow2
  $ ln -s /disks/kube3d/disk.qcow2 /var/lib/libvirt/images/diskd3.qcow2

  $ systemctl stop libvirtd #May not be necessary
  $ systemctl start libvirtd
  ```
  
 ##### Clone the GCS cluster
 
 Create the gcs repo
 
  ``` 
  $ git clone https://github.com/gluster/gcs.git  
  $ cd gcs/deploy/kubespray
  #If its empty or doesn’t exist, do the following:
  $ cd gcs/deploy/ ; git clone https://github.com/kubernetes-sigs/kubespray.git
  ```
Change the Vagrantfile in gcs repo, to have higher CPU, memory and disks. In our tests, the disks in the hypervisor are attached to the VMs. We attached 2, 1.3T disks to each VM. Vagrantfile is copied into the repo for reference.
  ```
  $ cd gcs/deploy/
  $ vagrant up
  ```
Once the vagrant up succesfully completes, login to the kubernetes master(kube1).
  ```
  $ vagrant ssh kube1
  #Make sure all the containers are up and running fine:
  $ kuectl get pods -ngcs
  #If this command throws error”The connection to the server localhost:8080...”, execute below commamds
  $ sudo cp /etc/kubernetes/admin.conf $HOME/
  $ sudo chown $(id -u):$(id -g) $HOME/admin.conf
  $ export KUBECONFIG=$HOME/admin.conf
  $ echo "export KUBECONFIG=$HOME/admin.conf" >> ~/.bashrc
  $ kuectl get pods -ngcs
  ```

##### Deploy gluster loopback CSI driver:
There is an unsolved issue with gluster loopback driver, that the csi containers fail to create loop devices if it already doesn’t exist. Hence the following workaround:

Ssh to all kube systems kube{1..3} and execute the following:
for i in {1..3000} ; do touch /tmp/abcd$i ;  losetup --find --show /tmp/abcd$i ; done ; losetup -D ; rm -f /tmp/abc*

Copy the below files to kube1(master node):
https://github.com/gluster/gluster-csi-driver/pull/105/files#diff-6b90f49172d8a10e75aa23917602ad23      ⇒ csi-deployment.yaml
https://github.com/gluster/gluster-csi-driver/pull/105/files#diff-145bdc1c1d484621d4ed29e4bb64b32d     ⇒ storage-class.yaml

kubectl create -f csi-deployment.yaml -ngcs
kubectl get pods -ngcs
NAME                                      READY   STATUS    RESTARTS   AGE
csi-attacher-glusterblockplugin-0         2/2     Running   0          69m
csi-attacher-glusterfsplugin-0            2/2     Running   0          94m
csi-nodeplugin-glusterblockplugin-5qglz   2/2     Running   0          69m
csi-nodeplugin-glusterblockplugin-hh5d6   2/2     Running   0          69m
csi-nodeplugin-glusterblockplugin-lrd4c   2/2     Running   0          69m
csi-nodeplugin-glusterfsplugin-8f5kh      2/2     Running   0          94m
csi-nodeplugin-glusterfsplugin-cg2f9      2/2     Running   1          94m
csi-nodeplugin-glusterfsplugin-gx2nb      2/2     Running   0          94m
csi-provisioner-glusterblockplugin-0      2/2     Running   0          69m
csi-provisioner-glusterfsplugin-0         3/3     Running   0          94m
etcd-85ps2f9lxl                           1/1     Running   0          99m
etcd-dmhrjmxmpj                           1/1     Running   0          100m
etcd-operator-7cb5bd459b-pctwz            1/1     Running   0          101m
etcd-w7lm7vthnz                           1/1     Running   0          101m
gluster-kube1-0                           1/1     Running   1          99m
gluster-kube2-0                           1/1     Running   1          99m
gluster-kube3-0                           1/1     Running   1          99m

Wait for the glusterblock csi containers to goto the Running state. Then create the storage class:
kubectl create -f storage-class.yaml

Unset glusterfs-csi storage class as not default(this step may be unnecessary):

kubectl patch storageclass glusterfs-csi -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'

The setup is complete, gluster block storage based on loopback is ready to be consumed by the applications.
Create the app using the gluster block storage:
Kubectl create -f app.yaml 

Kubectl get pods # Should show the pod in running state
Kubectl get pvc # Should show the pvc in BOUND state

