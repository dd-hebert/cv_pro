File Paths
==========

``cv_pro`` is flexible in handling file paths. When you give a path at the terminal with ``-p``, you can provide
a full absolute path::

    cvp -p C:\full\path\to\your\data\file.bin


Alternatively, you can open a terminal session inside a folder containing a data file and a relative path::

    # Current working directory = C:\full\path\to\you\data
    cvp -p file.bin

``cv_pro`` has a helpful root directory feature ``-r`` which you can use to shorten the file paths you type.
The ``cv_pro`` workflow works best when you keep all of your data files inside a common root folder. If this is
the case, you can set the root directory at the terminal::

    cvp -r C:\full\path\to\your\data

With the root directory set, you can now use shorter relative paths from *anywhere*::

    # From inside any directory
    cvp -p file.bin

.. Note::
    You can check if a root directory is set with ``-grd``::

        cvp -grd
    
    You can delete the root directory with ``-crd``::

        cvp -crd

