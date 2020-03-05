CUPS drivers for FGL-based printers
===================================

This project provides CUPS drivers for ticket printers that work with the "Friendly Ghost Language" FGL.
Theoretically, this should be basically all ticket printers from BOCA, Practical Automation, and others, although we
obviously did not test all of them. We also only include PPD specification files for two series from Practical
Automation, but it is straightforward to add more. We are looking forward to your contributions!

Supported models
----------------

* Practical Automation ITL-2002 series
* Practical Automation ITL-2003 series

Tested models
^^^^^^^^^^^^^

* Practical Automation uITL+2003CF

Known bugs
----------

* Printing from GUI applications might not work and we don't know, why. Printing the same file with ``lpr`` almost
  always works.

Installation
------------

Debian
^^^^^^

You can install our package like this::

    # apt-get install apt-transport-https
    # curl https://download.pretix.eu/apt/repo.key | apt-key add -
    # echo "deb https://download.pretix.eu/cups-fgl-printers ./" > /etc/apt/sources.list.d/pretix.list
    # apt-get update
    # apt-get install cups-fgl-printers

Arch Linux
^^^^^^^^^^

Our package is available from the Arch User Repository::

    # yay -S cups-fgl-printers-git

Development
-----------

You can compile the ``.drv`` files to ``.ppd`` files by executing::

    make ppds

in the project's main directory.

Ubuntu/Debian package
^^^^^^^^^^^^^^^^^^^^^

To build the Ubuntu/Debian package, execute::

    ./packaging/build_deb.sh

If you are on linux, but not on a debian-based distribution that lacks the ``dpkg`` command,
a docker image will be downloaded and executed to get the debian toolchain. There is a similar
command ``build_deb_repo.sh`` that you probably won't need, except if you are myself reading
this in a couple of years.

Contributing
------------

If you like to contribute to this project, you are very welcome to do so. If you have any
questions in the process, please do not hesitate to ask us.

Please note that we have a `Code of Conduct`_
in place that applies to all project contributions, including issues, pull requests, etc.

License
-------

The code in this repository is published under the terms of the GPLv3 License.
See the LICENSE file for the complete license text.

This project is maintained by Raphael Michel <mail@raphaelmichel.de>. See the
AUTHORS file for a list of all the awesome folks who contributed to this project.

This project is 100 percent free and open source software. If you are interested in
commercial support, hosting services or supporting this project financially, please
go to `pretix.eu`_ or contact Raphael directly.

.. _pretix.eu: https://pretix.eu
.. _Code of Conduct: https://docs.pretix.eu/en/latest/development/contribution/codeofconduct.html
