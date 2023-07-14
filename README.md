``cv_pro``
==========
``cv_pro`` is a command line tool for processing CV data files (.bin format) created from the CH Instruments chi760e electrochemical workstation.

Installation
------------
``cv_pro`` can be installed directly from this repo using pip:

```
pip install git+https://github.com/dd-hebert/cv_pro.git
```

Command Line Interface
----------------------
With ``cv_pro`` installed, you can run the script directly from the command line using the ``cvp`` shortcut. To begin processing data, use ``-p`` and specify the path to your data:

**Process .bin file:**
```
cvp -p path\to\your\data.bin
```

**Tip:** You can use shorter paths by setting a **root directory** or by simply opening a terminal session inside the same folder as your data files.


Command Line Arguments
----------------------
#### ``-p``, ``--path`` : string, required
The path to the CV data .bin file. You can use a path relative to the current working directory, an absolute path, or a path relative to the root directory (if one has been set).

___

#### ``-crd``, ``-–clear_root_dir`` : flag, optional
Reset the root directory back to the default location (in the user's home directory).

#### ``-fc``, ``--ferrocenium`` : float, optional
Set the relative potential of the Fc/Fc<sup>+</sup> redox couple (given in V) to adjust the x-axis for data reporting.

#### ``-fp``, ``--file_picker`` : flag, optional
Interactively pick a .bin file from the terminal. The file is opened in view only mode.

#### ``-grd``, ``–-get_root_dir`` : flag, optional
Print the current root directory to the console.

#### ``-h``, ``--help`` : flag
Use ``-h`` to get help with command line arguments.

#### ``-rd``, ``-–root_dir`` : string, optional
Set the root directory so you don’t have to type full length file paths. For example, if all your CV data files are stored inside a common folder, you can set it as the root directory. Then, the path you give with ``-p`` is assumed to be inside the root directory. With a root directory set, you'll no longer have to type the root directory portion of the file path.

**Without root directory:**
```
# Must type full file path
cvp -p C:\mydata\CV_Data\mydata.bin
```

Without a root directory, you must type the full path to the data. 

**With root directory:**
```
# Set the root directory
cvp -rd C:\mydata\CV_Data

# Only need short file path
cvp -p mydata.bin
```

With a root directory set, the root directory portion of the path can be omitted. The root directory is saved between runs in a config file.

#### ``-sep``, ``--peak_sep_limit`` : float, optional
The maximum distance (given in V) between two peaks for them to be considered "reversible". If the distance between two peaks if within the limit, E<sub>1/2</sub> calculations will be attempted.

#### ``-t``, ``--trim`` : 2 integers, optional
Use ``-t`` to select a specific portion of CV data. The first integer is the first sweep to select, and the second integer is the total number of sweeps to show. Give ``0`` for the second value to show all sweeps following the sweep specified by the first value.

```
# Show 2 sweeps starting from the 2nd sweep
cvp -p C:\Desktop\MyData\myfile.bin -t 2 2

# Show all sweeps after the 3rd sweep
cvp -p C:\Desktop\MyData\myfile.bin -t 3 0
```

#### ``-tr``, ``--tree`` : flag, optional
Print the ``root_directory`` file tree to the console.

#### ``-v`` : flag, optional
Enable view only mode. No data processing is performed and a plot of the data set is shown.

Examples
--------
Coming soon.

Uninstall
---------
To uninstall ``cv_pro``, run the following command:
```
pip uninstall cv_pro
```
