# -*- mode: ruby -*-
# vi: set ft=ruby :

driveletters = ('a'..'z').to_a

Vagrant.configure("2") do |config|

  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/home/vagrant/sync", disabled: true
  config.vm.box = "centos/atomic-host"
  config.vm.box_version = "1808.01"
  host_vars = {}
  (1..3).each do |i|
    config.vm.define vm_name = "kube#{i}" do |vm|
      vm.vm.hostname = vm_name
      if i == 1
        config.vm.network "forwarded_port", guest: 30600, host: 9090, host_ip: "127.0.0.1"
        config.vm.network "forwarded_port", guest: 30800, host: 9000, host_ip: "127.0.0.1"
      end
      vm.vm.provider :libvirt do |lv|
        lv.default_prefix = "gcs"
        lv.cpus = 8
        lv.memory = 32768
        lv.nested = false
        lv.cpu_mode = "host-passthrough"
        lv.volume_cache = "writeback"
        lv.graphics_type = "none"
        lv.video_type = "vga"
        lv.video_vram = 1024
        # lv.usb_controller :model => "none"  # (requires vagrant-libvirt 0.44 which is not in Fedora yet)
        lv.random :model => 'random'
        lv.channel :type => 'unix', :target_name => 'org.qemu.guest_agent.0', :target_type => 'virtio'

        lv.storage :file, :device => "vdb", :size => '20G'

        disks = []
	lv.storage :file, :allow_existing => true, :path => "diskc#{i}.qcow2", :device => "vdc", :size => '1224G'
	disks.push "/dev/vdc"
	lv.storage :file, :allow_existing => true, :path => "diskd#{i}.qcow2", :device => "vdd", :size => '1224G'
        disks.push "/dev/vdd"
        host_vars[vm_name] = {"gcs_disks" => disks.to_s}
      end
      # TODO: Maybe support other providers... like VirtualBox

      if i == 3
        vm.vm.provision :ansible do |ansible|
          ansible.playbook = "vagrant-playbook.yml"
          ansible.become = true
          ansible.limit = "all"
          ansible.groups = {
            "etcd" => ["kube[1:3]"],
            "kube-master" => ["kube[1:2]"],
            "kube-node" => ["kube[1:3]"],
            "k8s-cluster:children" => ["kube-master", "kube-node"],
            "gcs-node" => ["kube[1:3]"]
          }
          ansible.host_vars = host_vars
        end
      end
    end
  end
end
