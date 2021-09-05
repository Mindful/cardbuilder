Installation & Setup
=======================================

Cardbuilder is a command line tool for generating flashcards. If you have never used your computer's command line before, it may be difficult for you to use Cardbuilder. That said, even a rudimentary understanding should be more than sufficient, so if you would like to take the opportunity to learn: the University of Washington has an `excellent guide <https://itconnect.uw.edu/learn/workshops/online-tutorials/web-publishing/what-is-a-terminal/>`_ to using the terminal/command line.

Mac & Linux Installation
------------------------

Installation Cardbuilder is as easy as installing a pip (Python) package. Most modern operating sytems come with one or both of these installed, but if you are missing one, a quick google search should clarify how to install them for your given operating system. After that, Cardbuilder can be installed by simply running the commands below.

.. code-block:: bash

    pip install cardbuilder

Note that if you actively use Python for other things, it's recommended that you install Cardbuilder in its own virtual environment so that its lengthy list of requirements doesn't cause package conflicts.

Windows Installation
-----------------------

Windows installation is fundamentally the same as the Mac & Linux installation described above, with one exception - because of `issues <https://github.com/Mindful/cardbuilder/issues/10>`_ with how Windows handles some aspects of installation, it is *highly* recommended that you `install Anaconda <https://docs.anaconda.com/anaconda/install/windows/>`_ and then use the Anaconda Prompt as your command line for installing and using Cardbuilder. The actual installation process should still just involve running the below command.

.. code-block:: bash

    pip install cardbuilder

Note that virtual environment managers other than Anaconda will also likely work fine, but installations outside of virtual environments may have problems.

Updating
------------------
Once you have successfully installed Cardbuilder, it can be updated like this:

.. code-block:: bash

    pip install cardbuilder --upgrade

Installation worked - what now?
-------------------------------

The easiest way to use Cardbuilder is by calling the :ref:`console commands <commands>` for generating flashcards across specific language pairs.

