.. _lamp-server-install:

LAMP Web Server
###############

This tutorial provides instructions on how to set up a
:abbr:`LAMP (Linux\*, Apache\*, MySQL\*, PHP)` web server on |CL-ATTR| and how
to use phpMyAdmin\* to manage an associated database. Note that this
tutorial installs MariaDB\*, which is a drop-in replacement for MySQL\*.

In order to create a web server using |CL| as the host OS, your host system
must be running |CL|. This tutorial assumes you have installed |CL| on your
host system. For detailed instructions on installing |CL| on a bare metal
system, visit :ref:`bare-metal-install-desktop`.

This tutorial covers:

.. contents:: :local:
   :depth: 1

Install Apache
**************

Apache is an open source HTTP web server application that can run on several
operating systems, including |CL|. Go to the `Apache HTTP Server Project`_
for more information.

Install the httpd bundle
========================

The **httpd** bundle contains the packages needed to install the
Apache software bundle on |CL|.

.. note::

   Before you install new packages, update the |CL| with the following
   console command:

   .. code-block:: bash

      sudo swupd update

#. To install the bundle, enter the following command:

   .. code-block:: bash

      sudo swupd bundle-add httpd

#. Start the Apache service and set it start automatically on boot, 
   enter the following commands:

   .. code-block:: bash

      sudo systemctl enable --now httpd.service

#. To verify that the Apache server application is running, open a web
   browser and navigate to: \http://localhost.

   If the service is running, a confirmation message will appear, similar to the
   message shown in figure 1.

   .. rst-class:: dropshadow

   .. figure:: ../_figures/wordpress/web-server-install-1.png
      :alt: This web server is operational from host.
      :scale: 50%

      `Figure 1: Confirmation that the Apache service is running.`

   .. note::

      The :file:`index.html` file is located in the :file:`/var/www/html` directory
      of your host system. You will copy this file into a new location after you
      modify the configuration in the next step.

Change the default configuration and data directory
***************************************************

|CL| is designed to be a :ref:`stateless` operating system which means that you
must create an optional configuration file to override the default values.
The default location of the Apache configuration file, :file:`httpd.conf`,
is located in the :file:`/usr/share/defaults/httpd` directory. |CL| can
override this directory as part of the stateless paradigm. This default
:file:`.conf` file includes the following directives that allow for additional
locations of configuration definitions:

.. code-block:: console

   # Virtual hosts
   IncludeOptional /usr/share/defaults/httpd/conf.d/*.conf
   IncludeOptional /usr/share/defaults/httpd/conf.modules.d/*.conf
   IncludeOptional /etc/httpd/conf.d/*.conf
   IncludeOptional /etc/httpd/conf.modules.d/*.conf

In this section you will define your own httpd.conf file to override the
default values, and define a custom DocumentRoot for your web server.

#. Create the directory structure for :file:`/etc/httpd/conf.d`.

   .. code-block:: bash

      sudo mkdir -p /etc/httpd/conf.d

#. Create and open the :file:`httpd.conf` file in your new :file:`/etc/httpd/conf.d`
   directory.

   .. code-block:: bash

      sudo nano /etc/httpd/conf.d/httpd.conf

#. Add the ``DocumentRoot`` variable to :file:`httpd.conf`. Copy the content
   listed below into the new :file:`/etc/httpd/conf.d/httpd.conf` file.

   .. code-block:: console

      #
      # Set a new location for DocumentRoot
      #
      DocumentRoot "/var/www/tutorial"

      #
      # Relax access to content within /var/www/tutorial for this example
      #
      <Directory "/var/www/tutorial">
        AllowOverride none
        Require all granted
      </Directory>

#. Create a new ``DocumentRoot`` directory structure and copy the
   :file:`index.html` file from :file:`/var/www/html` directory to
   :file:`/var/www/tutorial`.

   .. code-block:: bash

      sudo mkdir –p /var/www/tutorial
      cd /var/www/tutorial
      sudo cp /var/www/html/index.html .

#. To ensure a successful setup, edit the new :file:`index.html` file with an
   obvious change.

   .. code-block:: bash

      sudo nano index.html

   For example, we changed the default message

   "It works!"

   to

   "It works from its new location!"

#. Restart ``httpd.service``.

   .. code-block:: bash

      sudo systemctl restart httpd.service

#. Go to \http://localhost to view the new screen. You should see your updated
   default message from step 5.

#. Change the configuration back to the default :file:`/var/www/html`
   location. To do this, edit the :file:`/etc/httpd/conf.d/httpd.conf` file
   again and replace any instance of /var/www/tutorial with /var/www/html.

   .. code-block:: bash

      sudo nano /etc/httpd/conf.d/httpd.conf

#. Restart ``httpd.service``.

   .. code-block:: bash

      sudo systemctl restart httpd.service

#. Go to \http://localhost and verify that you can see the default screen
   again.

#. Optionally, remove the /var/www/tutorial directory you previously created.

   .. code-block:: bash

      sudo rm /var/www/tutorial/index.html
      sudo rmdir /var/www/tutorial

Install PHP
***********

An Apache installation allows you to display static web pages. Enabling PHP
allows you to generate and display dynamic web pages. To add this
functionality to your web server, install PHP on your system.

#. To get the php components, enter the following command:

   .. code-block:: bash

      sudo swupd bundle-add php-basic

#. To enable PHP and set it to start automatically on boot, enter the 
   following commands:

   .. code-block:: bash

      sudo systemctl enable --now php-fpm.service
      sudo systemctl restart httpd.service

   After restarting the Apache service, test your PHP installation.

#. Create and open a file named :file:`phpinfo.php` in the :file:`/var/www/html/`
   directory using a text editor.

   .. code-block:: bash

      sudo nano /var/www/html/phpinfo.php

#. Add the following line to the file:

   .. code-block:: php

      <?PHP phpinfo() ?>

#. Go to \http://localhost/phpinfo.php.

#. Verify that the PHP information screen appears, similar to figure 2:

   .. rst-class:: dropshadow

   .. figure:: ../_figures/wordpress/web-server-install-2.png
      :alt: PHP information screen
      :width: 600

      `Figure 2: The PHP information screen.`

If the PHP information screen is displayed, you have successfully installed
the PHP components and are now ready to add your database application to
complete your LAMP server implementation.

Install MariaDB
***************

Install MariaDB to store content. MariaDB is a drop-in replacement for MySQL
and is available in the database-basic |CL| bundle.

#. To install the database-basic bundle, enter the following command:

   .. code-block:: bash

      sudo swupd bundle-add mariadb

#. To start MariaDB after it is installed and set it to start automatically on
   boot, enter the following commands:

   .. code-block:: bash

      sudo systemctl enable --now mariadb

#. To check the status of MariaDB, enter the following command:

   .. code-block:: bash

      sudo systemctl status mariadb

   Press :kbd:`Ctrl` + :kbd:`c` or :kbd:`q` to exit.

Security hardening
==================

With the MariaDB service running, we can perform some basic security
hardening.

#. To add a basic layer of security, enter the following command:

   .. code-block:: bash

      sudo mysql_secure_installation

#. Respond to the questions that appear in the script below.

   .. note::

      Our suggested responses follow each question.

   .. code-block:: none

      Enter current password for root (enter for none):

   In order to secure MariaDB, we need the current password for the root
   user. For a newly installed MariaDB without a set root password, the
   password is blank. Thus, press enter to continue.

   .. code-block:: none

      OK, successfully used password, moving on...

      Set root password? [Y/n]

   .. _set-password:

   Set the root password to prevent unauthorized MariaDB root user logins.
   To set a root password, type 'y'.

   .. code-block:: none

      New password:

   Type the desired password for the root user.

   .. code-block:: none

      Re-enter new password:

   Re-type the desired password for the root user.

   .. code-block:: none

      Password updated successfully!
      Reloading privilege tables..
      ... Success!

      Remove anonymous users? [Y/n]

   By default, a MariaDB installation includes an anonymous user that allows
   anyone to log in to MariaDB without a user account. This anonymous user
   is intended only for testing and for a smoother installation. To remove
   the anonymous user and make your database more secure, type 'y'.

   .. code-block:: none

      ... Success!
      Disallow root login remotely? [Y/n]

   Normally, root should only be allowed to connect from the 'localhost'. This
   ensures that someone cannot guess the root password from the network. To
   block any remote root login, type 'y'.

   .. code-block:: none

      ... Success!
      Remove test database and access to it? [Y/n]

   By default, MariaDB includes a database named 'test' which anyone can access.
   This database is also intended only for testing and should be removed. To
   remove the test database, type 'y'.

   .. code-block:: none

      - Dropping test database...
      ... Success!
      - Removing privileges on test database...
      ... Success!
      Reload privilege tables now? [Y/n]

   Reloading the privilege tables ensures all changes made so far take
   effect immediately. To reload the privilege tables, type 'y'.

   .. code-block:: none

      ... Success!

      Cleaning up...

   All done!  If you've completed all of the above steps, your MariaDB
   installation should now be secure.

   Thanks for using MariaDB!

The MariaDB installation is complete, and we can now install phpMyAdmin to
manage the databases.

Install phpMyAdmin
******************

The web-based tool phpMyAdmin is a straightforward way to manage MySQL or
MariaDB databases. Visit the `phpMyAdmin`_ website for the complete
discussion regarding phpMyAdmin, its documentation, the latest downloads,
and other useful information.

In this tutorial, we use the latest English version of phpMyAdmin.

#. Download the :file:`phpMyAdmin-<version>-english.tar.gz` file to your
   :file:`~/Downloads` directory. Here, <version> refers to the current
   version available at https://www.phpmyadmin.net/downloads.

   .. note::

      This example downloads and uses version 4.6.4.

#. Once the file has been successfully downloaded and verified, decompress
   the file and directories into the Apache web server document root
   directory. Use the following commands:

   .. code-block:: bash

      cd /var/www/html
      sudo tar –xzvf ~/Downloads/phpMyAdmin-4.6.4-english.tar.gz

#. To keep things simple, rename the newly created
   :file:`phpMyAdmin-4.6.4-english` directory to :file:`phpMyAdmin` with the
   following command:

   .. code-block:: bash

      sudo mv phpMyAdmin-4.6.4-english phpMyAdmin

Use phpMyAdmin to manage a database
***********************************

You can use the phpMyAdmin web-based tool to manage your databases. Follow the
steps below for setting up a database called "WordPress".

#. Verify that a successful installation of all LAMP server components by
   going to \http://localhost/phpMyAdmin. See figure 3.

#. Log in with your root userid and the password you set up when you ran the
   :ref:`mysql_secure_installation command <set-password>`. Enter your
   credentials and select :guilabel:`Go` to log in:

   .. rst-class:: dropshadow

   .. figure:: ../_figures/wordpress/web-server-install-3.png
      :alt: phpMyAdmin login page
      :width:     600

      `Figure 3: The phpMyAdmin login page.`

#. Verify a successful login by confirming that the main phpMyAdmin page
   displays, as shown in figure 4:

   .. rst-class:: dropshadow

   .. figure:: ../_figures/wordpress/web-server-install-4.png
      :alt: phpMyAdmin dashboard
      :width:     600

      `Figure 4: The phpMyAdmin dashboard.`

#. Set up a database by selecting the :guilabel:`Databases` tab, as shown in
   figure 5.

#. Enter `WordPress` in the text field below the :guilabel:`Create database`
   label.

#. Select the :guilabel:`utf8_unicode_ci` option from the
   :guilabel:`Collation` drop-down menu beside the text field.

#. Click :guilabel:`Create`.

   .. rst-class:: dropshadow

   .. figure:: ../_figures/wordpress/web-server-install-5.png
      :alt: Databases tab
      :width:     600

      `Figure 5: The Databases tab.`

#. Set up user permissions by selecting the :guilabel:`WordPress` database
   located in the left panel. See figure 6.

#. Select the :guilabel:`Privileges` tab. Figure 6 shows its contents.

   .. rst-class:: dropshadow

   .. figure:: ../_figures/wordpress/web-server-install-6.png
      :alt: Privileges tab
      :width:     600

      `Figure 6: The Privileges tab.`

#. Click :guilabel:`Add user account` located at the bottom of the
   :guilabel:`Privileges` tab. The `Add user account` page appears, as shown
   in figure 7.

   .. rst-class:: dropshadow

   .. figure:: ../_figures/wordpress/web-server-install-7.png
      :alt: User accounts tab
      :width:     600

      `Figure 7: The User accounts tab.`

#. Enter the following information in the corresponding fields that appear
   in figure 7 above:

   * User name: wordpressuser

   * Password: wp-example

   * Re-type: wp-example

#. In the `Database for user account` section, select
   :guilabel:`Grant all privileges on database “WordPress”.`

#. At the bottom of the page, click :guilabel:`Go`.

If successful, you should see the screen shown in figure 8:

.. rst-class:: dropshadow

.. figure:: ../_figures/wordpress/web-server-install-8.png
   :alt: User added successfully
   :width:     600

   `Figure 8: The user wordpressuser is successfully added.`

**Congratulations!**

You have now created a fully functional LAMP server along with a
WordPress\*-ready database using |CL|.

Next steps
**********

Next, add the WordPress components needed to host a WordPress website with :ref:`wp-install`.

.. _Apache HTTP Server Project: https://httpd.apache.org/
.. _phpMyAdmin: https://www.phpmyadmin.net/
