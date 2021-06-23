.. _zfs:

OpenZFS*
########

This tutorial shows how to set up `OpenZFS* file system and volume manager`_ on |CL-ATTR|, using a non-root device for zpools. 

.. contents::
   :local:
   :depth: 1

Background
**********

The OpenZFS storage platform provides volume management, snapshot capabilities, and redundancy detection. |CL| **does not** ship with a binary ZFS kernel module (zfs.ko). |CL| users who wish to incorporate the zfs.ko kernel module must build and maintain this work themselves.

.. CAUTION::

   Use of the OpenZFS kernel module in connection with |CL| is neither recommended nor officially endorsed by the Clear Linux* Project.  Users who follow this tutorial and build zfs.ko kernel module are encouraged to seek independent legal counsel regarding any plan to redistribute a software package containing zfs.ko and |CL|. 

Known Issues
************

Using a long-term-support (LTS) kernel when running OpenZFS reduces the risk of incompatibilities with kernel updates. When new kernels or new versions of OpenZFS are released, users bear the responsibility to test those releases and ensure compatibility before deploying any updates. 

Prerequisites
*************

* Learn to :ref:`kernel-modules-dkms`
* Learn to use :ref:`swupd-guide`

Install the DKMS kernel
=======================

.. include:: ../guides/kernel/kernel-modules-dkms.rst
   :start-after: kernel-modules-dkms-install-begin-alt:
   :end-before: kernel-modules-dkms-install-end:

Bundles
=======

Before installing OpenZFS, install the bundles that contain the build dependencies.

.. code-block:: console

    sudo swupd bundle-add wget devpkg-openssl devpkg-util-linux

Install
*******

Download OpenZFS release
========================

In this section, we download release 2.0.0 directly from the `OpenZFS repository` (the latest available as of the latest revision of this page).

Download release 2.0.0

   .. code-block:: console
   
      cd /usr/src
      sudo wget https://github.com/openzfs/zfs/releases/download/zfs-2.0.0/zfs-2.0.0.tar.gz
      sudo tar -xvf zfs-2.0.0.tar.gz

Compile the module
==================

We will build the module using DKMS. This will enable us to keep the module up to date as new kernels are released in the future.

The ZFS distribution provides a script to build a suitable dkms.conf file.

   Build dkms.conf and install it into the DKMS tree.

   .. code-block:: console

      cd /usr/src/zfs-2.0.0
      sudo scripts/dkms.mkconf -n zfs -v 2.0.0 -f dkms.conf
      sudo dkms add -m zfs -v 2.0.0
      sudo dkms build -m zfs -v 2.0.0
      sudo dkms install -m zfs -v 2.0.0
      
Observe that this install the zfs kernel modules to: 

   :file:`/usr/lib/modules/<kernel-name>/extra/zfs`
   
Compile userspace tools
=======================

Here we compile and install the zfs userspace tools (e.g., zpool, zfs, etc.).

   .. code-block:: console
   
      cd /usr/src/zfs-2.0.0
      sudo ./configure
      sudo make
      sudo make install

The binaries are installed at the following directory. While not required, it's recommended to add :file:`/usr/local/sbin` to your path variable.

   .. code-block:: console

      + /usr/local/
      |--+ bin/
         |--zvol_wait
         |--zgenhostid
         |--raidz_test
      |--+ etc/
         |--+ zfs/
            |--* zed.d/
            |--+ zpool.d/
            |--zfs-functions
      |--+ include/libzfs/ [contents omitted]
      |--+ lib/
      |--+ libexec/
         |--+ zfs/
            |-- zpool.d/
            |-- zed.d
      |--+ share/zfs/ [contents omitted]
      |--+ sbin/
         |--fsck.zfs
         |--zpool
         |--zdb
         |--zed
         |--zfs
         |--zhack
         |--zinject
         |--zpool
         |--ztest
         |--zstreamdump
      |--+ src/
         |--+ zfs-2.0.0/
         |--+ spl-2.0.0/


Set up systemd
==============

We now have these unit files available. 

.. code-block:: console

   zfs-env-bootfs.service
   zfs-zed.service
   zfs-import-cache.service
   zfs-import-scan.service
   zfs-mount.service
   zfs-share.service
   zfs-volume-wait.service
  
  
OpenZFS requires that we  explicitly install and enable the services desired. 

To use ZFS automatic zpool import and filesystem mount services, enable them.

.. code-block:: console

   sudo systemctl enable zfs-import-cache
   sudo systemctl enable zfs-import.target
   sudo systemctl enable zfs-import-scan
   sudo systemctl enable zfs-mount
   sudo systemctl enable zfs.target


Load the kernel module at boot
==============================

OpenZFS kernel modules must be loaded before any OpenZFS filesystems are mounted. For convenience, load the kernel modules at boot.

Systemd uses the `/etc/modules-load.d/` directory to load out-of-tree kernel modules. Make sure that the directory exists:

   .. code-block:: bash

      sudo mkdir -p /etc/modules-load.d

Create the configuration file:

   .. code-block:: bash

      echo "zfs" | sudo tee /etc/modules-load.d/01-zfs.conf

Reboot your system. zfs.ko should be loaded automatically (the module should appear in the outout of command :file:`lsmod`).

.. CAUTION::

   When the |CL| kernel is upgraded, DKMS will attempt to rebuild the OpenZFS module for the new kernel. 

   - DKMS may not have rebuilt the module
   - DKMS may not have auto-installed the module
   - The new kernel might introduce breaking changes that prevent zfs
     from compiling

To fix this situation, recompile zfs.ko with the new kernel code. OpenZFS *might* not compile at all with the new kernel.

.. CAUTION::
   
   **Be sure not to put anything on an OpenZFS pool that will be needed to rebuild kernel modules.** Ensure compatibility of OpenZFS with new Linux kernels when released.

Troubleshooting
===============

If you suspect an issue with DKMS rebuilding your module, you can check two places for information. The dkms-new-kernel service will show status that may help in troubleshooting:

.. code-block:: console

   systemctl status dkms-new-kernel.service

The systemd journal may also have important information:

.. code-block:: console

   journalctl -xe

.. CAUTION::
   As of OpenZFS 2.0.0, the included file :file:`script/dkms.mkconf` contains a minor incompability -- it calls the command :file:`lsb_release`, which is not available on Clear    Linux by default. It is trivial to edit :file:`dkms.mkconf` and remove the singular reference to :file:`lsb_release` without any ill effects, and then execute the :file:`dkms` commands above. However, keeping the file as provided is perfectly fine, but **will result in :file:`dkms` warnings**.

Next steps
**********
You're now ready to create zpools and datasets! For more information on using ZFS, see:

* `FreeBSD Handbook chapter on ZFS`_
* `ZFS-on-Linux issue tracker`_

.. _FreeBSD Handbook chapter on ZFS: https://www.freebsd.org/doc/handbook/zfs.html
.. _ZFS-on-Linux issue tracker: https://github.com/openzfs/zfs/issues/10068
.. _ZFS on Linux repository: https://github.com/openzfs/zfs
.. _OpenZFS* file system and volume manager: https://github.com/openzfs/zfs
