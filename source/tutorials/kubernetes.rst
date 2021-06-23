.. _kubernetes:

Kubernetes\*
############

This tutorial describes how to install, configure, and start the `Kubernetes
container orchestration system`_ on |CL-ATTR|.

A Kubernetes cluster can be setup on |CL| using the |CL| cloud-native-setup
scripts to automate the process or can be setup through a manual step-by-step
process. This tutorial covers both scenarios.


.. contents::
   :local:
   :depth: 1

Background
***********

|CL| has builtin integrations to make setting up Kubernetes using a variety of
`container runtimes
<https://kubernetes.io/docs/setup/production-environment/container-runtimes/>`_.

For more background information see:

* `What is Kubernetes?`_
* `What is a Container Network Interface (CNI)?`_

* `What is a Container Runtime Interface (CRI)?`_ 

  * `What is CRI+O?`_

  * `What is containerd?`_

  * `What is Docker?`_

* `What is Kata Containers\*?`_

Prerequisites
*************

This tutorial assumes you have already installed |CL|. For detailed
instructions on installing |CL| on a bare metal system, follow the :ref:`bare
metal installation tutorial<bare-metal-install-desktop>`.

#. Review and make sure the `requirements for kubeadm
   <https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#before-you-begin>`_
   are satisfied for the host system.

#. Before you continue, update your |CL| installation with the following
   command:

   .. code-block:: bash

      sudo swupd update

   Learn about the benefits of having an up-to-date system for cloud
   orchestration on the :ref:`swupd-guide` page.

#. Kubernetes, a set of supported :abbr:`CRI (Container Runtime Interface)`
   runtimes, :abbr:`CNI (Container Network Interface)` and `cloud-native-setup
   scripts`_ are included in the `cloud-native-basic`_ bundle. Install the
   cloud-native-basic bundle to get these components:

   .. code-block:: bash

      sudo swupd bundle-add cloud-native-basic


Set up Kubernetes automatically
*******************************

|CL| provides `cloud-native-setup scripts`_ to automate system setup and
Kubernetes cluster initialization which allows you to get a cluster up and
running quickly.

.. note::

   By default, the scripts will update |CL| to the latest version, set up the
   system as a Kubernetes master-node with **canal for container networking**
   and **crio for container runtime**, and taint the master node to allow
   workloads to run on it. Kata is installed as an optional alternative
   runtime. The script can be configured to use other CNI's and CRI's by
   following the directions on the `README
   <https://github.com/clearlinux/cloud-native-setup/blob/master/clr-k8s-examples/README.md>`_.
   
   See `What is a Container Network Interface (CNI)?`_ and `What is a
   Container Runtime Interface (CRI)?`_ for more information.

.. important::

   If network proxy settings are required for Internet connectivity, configure
   them now because the scripts will propagate proxy configuration based on
   the running configuration. It is especially important to set the
   :command:`no_proxy` variable appropriately for Kubernetes. 
   
   The script will also modify the :file:`/etc/environment` and
   :file:`/etc/profile.d/proxy.sh` files, if they exist, with the proxy
   environment variables in the running shell when the script is executed.
   
   See the `Setting proxy servers for Kubernetes`_ section for details.

#. Run the :file:`system-setup.sh` script to configure the |CL| system
   settings.

   .. code-block:: bash

      sudo /usr/share/clr-k8s-examples/setup_system.sh

#. Stop docker and containerd to avoid conflicting CRIs being detected. The
   scripts use CRIO for the CRI.

   .. code-block:: bash

      sudo systemctl stop docker
      sudo systemctl stop containerd
      

#. Install git as it's a dependency of the :file:`create_stack.sh`.

   .. code-block:: bash

      sudo swupd bundle-add git


#. Run the :file:`create_stack.sh` script to initialize the Kubernetes node
   and setup a container network plugin.

   .. code-block:: bash

      sudo /usr/share/clr-k8s-examples/create_stack.sh minimal

#. Follow the output on the screen and continue onto the section on `using
   your cluster <Use your cluster>`_.


Uninstalling
============

#. If you need to delete the Kubernetes cluster or want to start from scratch
   run the :file:`reset_stack.sh` script.

   .. warning::

      This will stop components in the stack including Kubernetes, all CNI and
      CRIs **and will delete** all containers and networks.

   .. code-block:: bash

      sudo /usr/share/clr-k8s-examples/reset_stack.sh


Set up Kubernetes manually
**************************

Configure host system
=====================

This tutorial uses the basic default Kubernetes configuration to get started.
You can customize your Kubernetes configuration according to your specific
deployment and security needs.

The Kubernetes administration tool, :command:`kubeadm`, performs some
"`preflight checks`_" when initializing and starting a cluster. The steps
below are necessary to ensure those preflight checks pass successfully.


#. Enable IP forwarding:

   - Create the file :file:`/etc/sysctl.d/60-k8s.conf` to set the
     :command:`net.ipv4.ip_forward` parameter

     .. code-block:: bash

        sudo mkdir -p /etc/sysctl.d/

        sudo tee /etc/sysctl.d/99-kubernetes-cri.conf > /dev/null <<EOF
        net.bridge.bridge-nf-call-iptables  = 1
        net.ipv4.ip_forward                 = 1
        net.bridge.bridge-nf-call-ip6tables = 1
        EOF

   - Apply the change:

     .. code-block:: bash

        sudo sysctl --system


#. Disable swap:

   .. code-block:: bash

      sudo systemctl mask $(sed -n -e 's#^/var/\([0-9a-z]*\).*#var-\1.swap#p' /proc/swaps) 2>/dev/null
      sudo swapoff -a

   .. note::

      Kubernetes is designed to work without swap. Performance degradation of other workloads can occur
      with swap disabled on systems with constrained memory resources.

#. Add the the system's hostname to the :file:`/etc/hosts` file. Kubernetes
   will read this file to locate the master host.

   .. code-block:: bash

      echo "127.0.0.1 localhost `hostname`" | sudo tee --append /etc/hosts


#. Enable the kubelet agent service to start at boot automatically:

   .. code-block:: bash

      sudo systemctl enable kubelet.service


.. important::

   If network proxy settings are required for Internet connectivity, configure
   them now because the scripts will propagate proxy configuration based on
   the running configuration. It is especially important to set the
   :command:`no_proxy` variable for Kubernetes. See the `Setting proxy servers
   for Kubernetes`_ section for details.


Initialize the master node
**************************

In Kubernetes, a master node is part of the `Kubernetes Control Plane
<https://kubernetes.io/docs/concepts/#kubernetes-control-plane>`_. 

Initializing a new Kubernetes cluster involves crafting a :command:`kubeadm
init` command. Adding parameters to this command can control the fundamental
operating components of the cluster. This means it is important to understand
and choose network and runtime options before running a :command:`kubeadm
init` command.


Choose a pod network add-on
===========================

See `What is a Container Network Interface (CNI)?`_ for information on what
pod network add-ons and CNIs.

It is important to decide which CNI will be used early because some pod
network add-ons require configuration during cluster initialization. Check
whether or not your add-on requires special flags when you initialize the
master control plane.

If your chosen network add-on requires appending to the :command:`kubeadm
init` command, make note of it before continuing. For example, if you choose
the *flannel* pod network add-on, then in later steps you must add the
following to the :command:`kubeadm init` command:

.. code-block:: console

   --pod-network-cidr 10.244.0.0/16

.. important::

   The version of CNI plugins installed needs to be compatible with the
   version of Kubernetes that is installed otherwise the cluster may fail.
   Check the Kubernetes version with :command:`kubeadm version -o short` and
   refer to the documentation of the CNI plugins to obtain a compatible
   version.

Choose a container runtime
==========================

See `What is a Container Runtime Interface (CRI)?`_ for more information on
what a CRI is.

|CL| supports Kubernetes with the various runtimes
below with or without `Kata Containers`_:

* `CRI+O`_
* `containerd`_
* `Docker`_

The container runtime that you choose will dictate the steps necessary to
initialize the master cluster with :command:`kubeadm init`.

CRI+O
-----

For information on CRI+O as a Kubernetes CRI, see `What is
CRI+O?`_. To use CRI+O as the Kubernetes CRI:

#. Start the CRI-O service and enable it to run at boot automatically:

   .. code-block:: bash

      sudo systemctl enable --now crio.service

   When the crio service starts for the first time, it will create a
   configuration file for crio at :file:`/etc/crio/crio.conf`.

#. Run the kubeadm command to initialize the master node with the
   :command:`--cri-socket` parameter:

   .. important:: 

      You may need to add additional parameters to the command below,
      depending the pod network addon in use. 
      
      In this example, the :command:`--pod-network-cidr 10.244.0.0/16`
      parameter is to use *flannel* as the pod networking. See `Choose a pod
      network add-on`_ for more information.

   .. code-block:: bash

      sudo kubeadm init \
      --cri-socket=unix:///run/crio/crio.sock \
      --pod-network-cidr 10.244.0.0/16


#. (Optional) By default, CRI+O will use runc as the default
   runtime. CRI+O can optionally provide Kata Containers as a runtime. See
   the `Add the Kata runtime to Kubernetes`_ section for details.

   With CRI+O, the `Kata Containers`_  can be set as the runtime with a
   per-pod *RuntimeClass* annotation. 

   .. note:: 

      If you are using CRI-O + Kata Containers as the runtime and choose the
      *flannel* for pod networking (see `Choose a pod network add-on`_), the
      :file:`/etc/crio/crio.conf` file needs to include the value below. On
      |CL| this is done automatically. 

      .. code-block:: console

         [crio.runtime]
         manage_network_ns_lifecycle = true


#. Once the cluster initialization is complete, continue reading about how to
   `Use your cluster`_.


containerd
----------

For information on containerd as as Kubernetes CRI, see `What is
containerd?`_. To use containerd as the Kubernetes CRI:

#. Start the containerd service and enable it to run at boot automatically:

   .. code-block:: bash

      sudo systemctl enable --now containerd.service


#. Configure kubelet to use containerd. and reload the service.

   .. code-block:: bash

      sudo mkdir -p  /etc/systemd/system/kubelet.service.d/

      cat << EOF | sudo tee  /etc/systemd/system/kubelet.service.d/0-containerd.conf
      [Service]                                                 
      Environment="KUBELET_EXTRA_ARGS=--container-runtime=remote --runtime-request-timeout=15m --container-runtime-endpoint=unix:///run/containerd/containerd.sock"
      EOF

#. Configure kubelet to use systemd as the cgroup driver. and reload the
   service.

   .. code-block:: bash

      sudo mkdir -p /etc/systemd/system/kubelet.service.d/

      cat << EOF | sudo tee  /etc/systemd/system/kubelet.service.d/10-cgroup-driver.conf
      [Service]
      Environment="KUBELET_EXTRA_ARGS=--cgroup-driver=systemd"
      EOF

#. Reload the systemd manager configuration.

   .. code:: bash

      sudo systemctl daemon-reload

#. Run the kubeadm command to initialize the master node with the
   :command:`--cri-socket` parameter:

   .. important:: 

      You may need to add additional parameters to the command below,
      depending the pod network addon in use. 
      
      In this example, the :command:`--pod-network-cidr 10.244.0.0/16`
      parameter is to use *flannel* as the pod networking. See `Choose a pod
      network add-on`_ for more information.

   .. code-block:: bash

      sudo kubeadm init \
      --cri-socket=/run/containerd/containerd.sock
      --pod-network-cidr 10.244.0.0/16


#. (Optional) By default, containerd will use runc as the default
   runtime. containerd can optionally provide Kata Containers as a runtime.
   See the `Add the Kata runtime to Kubernetes`_ section for details.

   With containerd, the `Kata Containers`_  can be set as the runtime with a
   per-pod *RuntimeClass* annotation. 

#. Once the cluster initialization is complete, continue reading about how to
   `Use your cluster`_.


Docker
------

For information on Docker, see `What is Docker?`_. To use Docker as the
Kubernetes container runtime:

#. Make sure Docker is installed:

   .. code:: bash

      sudo swupd bundle-add containers-basic

#. Start the Docker service and enable it to start automatically at boot:

   .. code::

      sudo systemctl enable --now docker.service

#. Configure kubelet to use the |CL| directory for cni-plugins and reload the
   service.

   .. code-block:: bash

      sudo mkdir -p  /etc/systemd/system/kubelet.service.d/

      cat << EOF | sudo tee  /etc/systemd/system/kubelet.service.d/0-cni.conf
      [Service]                                                 
      Environment="KUBELET_EXTRA_ARGS=--cni-bin-dir=/usr/libexec/cni"
      EOF

   .. code:: bash

      sudo systemctl daemon-reload


#. Run the kubeadm command to initialize the master node:

   .. important:: 

      You may need to add additional parameters to the command below,
      depending the pod network addon in use. 
      
      In this example, the :command:`--pod-network-cidr 10.244.0.0/16`
      parameter is to use *flannel* as the pod networking. See `Choose a pod
      network add-on`_ for more information.

   .. code:: bash

      sudo kubeadm init \
      --pod-network-cidr 10.244.0.0/16 


#. Once the cluster initialization is complete, continue reading about how to
   `Use your cluster`_.
   


Add the Kata runtime to Kubernetes
-----------------------------------

For information on Kata as a container runtime, see `What is Kata Containers\*?`_.
Using Kata Containers is optional.

You can use *kata-deploy* to install all the necessary parts of Kata
Containers after you have a Kubernetes cluster running with one of the CRI's
using the default runc runtime. Follow the steps in the Kubernetes quick start
section of the  `kata-containers GitHub README
<https://github.com/kata-containers/packaging/tree/master/kata-deploy#kubernetes-quick-start>`_
to install Kata.



Use your cluster
****************

Once your master control plane is successfully initialized, follow the
instructions presented about how to use your cluster and its *IP*, *token*,
and *hash* values are displayed. It is important that you record this
information because it is required to join additional nodes to the cluster.

A successful initialization looks like this:

.. code-block:: console

   Your Kubernetes control-plane has initialized successfully!

   To start using your cluster, you need to run the following as a regular user:

   mkdir -p $HOME/.kube
   sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
   sudo chown $(id -u):$(id -g) $HOME/.kube/config

   ...

   You can now join any number of machines by running the following on each node
   as root:

   kubeadm join <control-plane-host>:<control-plane-port> --token <token> --discovery-token-ca-cert-hash sha256:<hash>


With the first node of the cluster setup, you can continue expanding the
cluster with additional nodes and start deploying containerized applications.
For further information on using Kubernetes, see `Related topics`_. 

.. note:: 

   By default, the master node does not run any pods for security reasons. To
   setup a single-node cluster and allow the master node to also run pods, the
   master node will need to be untained. See the Kubernetes documentation on
   `control plane node isolation
   <https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/#control-plane-node-isolation>`_.


Troubleshooting
***************

Package configuration customization
===================================

|CL| is a stateless system that looks for user-defined package configuration
files in the :file:`/etc/<package-name>` directory to be used as default. If
user-defined files are not found, |CL| uses the distribution-provided
configuration files for each package.

If you customize any of the default package configuration files, you **must**
store the customized files in the :file:`/etc/` directory. If you edit any of
the distribution-provided default files, your changes will be lost in the next
system update as the default files will be overwritten with the updated files.

Learn more about :ref:`stateless` in |CL|.


Logs
====

* Check the kubelet service logs :command:`sudo journalctl -u kubelet`


Setting proxy servers for Kubernetes
====================================

If you receive any of the messages below, check outbound Internet access. You
may be behind a proxy server. 

   * Images cannot be pulled.
   * Connection refused error.
   * Connection timed-out or Access Refused errors.
   * The warnings when :command:`kubeadm init` is run.

     .. code-block:: console
   
        [WARNING HTTPProxy]: Connection to "https://<HOST-IP>" uses proxy "<PROXY-SERVER>". If that is not intended, adjust your proxy settings
        [WARNING HTTPProxyCIDR]: connection to "10.96.0.0/12" uses proxy "<PROXY-SERVER>". This may lead to malfunctional cluster setup. Make sure that Pod and Services IP ranges specified correctly as exceptions in proxy configuration
        [WARNING HTTPProxyCIDR]: connection to "10.244.0.0/16" uses proxy "<PROXY-SERVER>". This may lead to malfunctional cluster setup. Make sure that Pod and Services IP ranges specified correctly as exceptions in proxy configuration


If you use an outbound proxy server, you must configure proxy settings
appropriately for all components in the stack including :command:`kubectl` and
container runtime services. 

Configure the :ref:`proxy settings <proxy>`, using the standard *HTTP_PROXY*,
*HTTPS_PROXY*, and *NO_PROXY* environment variables. The *NO_PROXY* values are
especially important for Kubernetes to ensure private IP traffic does not try
to go out the proxy.

#. Set your environment proxy variables. Ensure that your local IP address is
   **explicitly included** in the environment variable *NO_PROXY*. Setting
   *localhost* is not sufficient!

   .. code-block:: bash

      export http_proxy=http://proxy.example.com:80
      export https_proxy=http://proxy.example.com:443
      export no_proxy=.svc,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,`hostname`,localhost

   .. important::

      :command:`kubeadm` commands specifically use these shell variables for proxy
      configuration. Ensure they are set your running terminal before running
      :command:`kubeadm` commands.

#. Run the following command to add systemd drop-in configurations for each
   service to include proxy settings:

   .. code-block:: bash

      services=(kubelet docker crio containerd)
      for s in "${services[@]}"; do
      sudo mkdir -p "/etc/systemd/system/${s}.service.d/"
      cat << EOF | sudo tee "/etc/systemd/system/${s}.service.d/proxy.conf"
      [Service]
      Environment="HTTP_PROXY=${http_proxy}"
      Environment="HTTPS_PROXY=${https_proxy}"
      Environment="SOCKS_PROXY=${socks_proxy}"
      Environment="NO_PROXY=${no_proxy}"
      EOF
      done


#. Reload the systemd manager configuration.

   .. code-block:: bash
      
      sudo systemctl daemon-reload


If you had a previously failed initialization due to a proxy issue, restart
the process with the :command:`kubeadm reset` command.


DNS issues
==========

* <HOSTNAME> not found in <IP> message.

   Your DNS server may not be appropriately configured. Try adding an entry
   to the :file:`/etc/hosts` file with your host's IP and Name.

   Use the commands :command:`hostname` and :command:`hostname -I` to
   retrieve them.

   For example: 
   
   .. code:: bash
   
      10.200.50.20 myhost


* coredns pods are stuck in container creating state and logs show entries
  similar to one of the following: 
  
  .. code:: console
  
     Warning  FailedCreatePodSandBox  5m7s                 kubelet, kata3     Failed to create pod sandbox: rpc error: code = Unknown desc = failed to get network JSON for pod sandbox k8s_coredns-<ID>>-5gpj2_kube-system_<UUID>): cannot convert version ["" "0.1.0" "0.2.0"] to 0.4.0

   In this case the :file:`/etc/cni/net.d/10-flannel.conf` or another CNI file
   is using an incompatible version. Delete the file and restart the stack.
   

  .. code:: console

     Warning  FailedCreatePodSandBox  117s (x197 over 45m)  kubelet, kata3     (combined from similar events): Failed to create pod sandbox: rpc error: code = Unknown desc = failed to create pod network sandbox k8s_coredns-<ID>>-npsm5_kube-system_<UUID>: error getting ClusterInformation: Get https://[10.96.0.1]:443/apis/crd.projectcalico.org/v1/clusterinformations/default: x509: certificate signed by unknown authority (possibly because of "crypto/rsa: verification error" while trying to verify candidate authority certificate "kubernetes")

  In this case, there may be multiple CNI configuration files in the
  :file:`/etc/cni/net.d` folder. Delete all the files in this directory and
  restart the stack.

  .. code:: console

     Warning  FailedScheduling  55s (x3 over 2m12s)  default-scheduler  0/1
     nodes are available: 1 node(s) had taints that the pod didn't tolerate.
     
  In this case, there may be multiple CNI configuration files in the
  :file:`/etc/cni/net.d` folder. Delete all the files in this directory, apply
  a CNI plugin, and restart the stack.

Reference
*********

What is Kubernetes?
===================

Kubernetes (K8s) is an open source system for automating deployment, scaling,
and management of containerized applications. It groups containers that make
up an application into logical units for easy management and discovery.

Kubernetes supports using a variety of `container runtimes
<https://kubernetes.io/docs/setup/production-environment/container-runtimes/>`_.

What is a Container Network Interface (CNI)?
============================================

In Kubernetes, a `pod
<https://kubernetes.io/docs/concepts/workloads/pods/pod/>`_ is a group of one
or more containers and is the smallest deployable unit of computing in a
Kubernetes cluster. Pods have shared storage/network internally but
communication between pods requires additional configuration. If you want your
pods to be able to communicate with each other you must choose and install a
`pod network add-on`_.

Some pod network add-ons enable advanced functionality with physical networks
or cloud provider networks.

What is a Container Runtime Interface (CRI)?
============================================

Container runtimes are the underlying fabric that pod workloads execute inside
of. Different container runtimes offer different balances between features,
performance, and security. 

Kubernetes allows integration various container runtimes via a container
runtime interface (CRI). 

What is CRI+O?
--------------

`CRI+O <https://cri-o.io/>`_ is a lightweight alternative to using Docker as
the runtime for kubernetes. It allows Kubernetes to use any OCI-compliant
runtime as the container runtime for running pods, such as runc and
Kata Containers as the container runtimes.

CRI+O allows setting a different runtime per-pod.

What is containerd?
-------------------

`containerd <https://containerd.io/>`_ is the runtime that the Docker engine
is built on top of. 

Kubernetes can use containerd directly instead of going through the Docker
engine for increased robustness and performance. See the `blog post on
kubernetes containerd integration
<https://kubernetes.io/blog/2018/05/24/kubernetes-containerd-integration-goes-ga/>`_
for more details.

containerd allows setting a different runtime per-pod.

What is Docker?
---------------

`Docker <https://www.docker.com/>`_ is an engine for running software packaged
as functionally complete units, called containers, using the same operating
system kernel.

The default built-in runtime provided by Kubernetes is using the system Docker
installation via Dockershim and as a result is one of the simplest to use. One
limitation of using Dockershim is that all pods on the Kubernetes node will
inherit and use the default runtime that Docker is set to use. To be able to
specify a container runtime per-Kerbernetes service, use CRI+O or containerd. 

What is Kata Containers\*?
==========================

`Kata Containers`_ is an alternative OCI compatible runtime that secures
container workloads in a lightweight virtual machine. It provides stronger
workloads isolation using hardware virtualization technology as a second layer
of defense for untrusted workloads or multi-tenant scenarios.

The Kata Containers (kata-runtime) adheres to :abbr:`OCI (Open Container
Initiative*)` guidelines and works seamlessly with Kubernetes through Docker,
containerd, or CRI+O.


Related topics
==============

* `Understanding basic Kubernetes architecture`_

* Installing a `pod network add-on`_

* `Joining your nodes`_

* `Deploying an application to your cluster`_

*  See our document on :ref:`Kubernetes best practices <kubernetes-bp>`



.. _Kubernetes container orchestration system: https://kubernetes.io/

.. _Kata Containers: https://katacontainers.io/

.. _cloud-native-basic: https://github.com/clearlinux/clr-bundles/blob/master/bundles/cloud-native-basic

.. _preflight checks: https://kubernetes.io/docs/reference/setup-tools/kubeadm/implementation-details/#preflight-checks

.. _Understanding basic Kubernetes architecture: https://kubernetes.io/docs/user-journeys/users/application-developer/foundational/#section-3

.. _Deploying an application to your cluster: https://kubernetes.io/docs/user-journeys/users/application-developer/foundational/#section-2

.. _pod network add-on: https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/#pod-network

.. _Joining your nodes: https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/#join-nodes

.. _cloud-native-setup scripts: https://github.com/clearlinux/cloud-native-setup/tree/master/clr-k8s-examples

.. _control-plane node: https://kubernetes.io/docs/concepts/#kubernetes-control-plane

.. _RuntimeClass handler: https://kubernetes.io/docs/concepts/containers/runtime-class/
