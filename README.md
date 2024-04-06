``cv_pro``
==========
``cv_pro`` is a command line tool for processing CV data files (.bin format) created from the CH Instruments chi760e electrochemical workstation.

Contents
--------
- [Installation](#installation)
- [Command Line Interface](#command-line-interface)
- [Command Line Arguments](#command-line-arguments)
- [Examples](#examples)
- [Multiview Mode](#multiview-mode)
- [Uninstall](#uninstall)

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
- [Data Processing Args](#data-processing-args)
- [User Config Args](#user-config-args)
- [Other Args](#other-args)

### Data Processing Args
Args related to data processing.

#### ``-p``, ``--path`` : string, required
The path to the CV data .bin file. You can use a path relative to the current working directory, an absolute path, or a path relative to the root directory (if one has been set).

#### ``-fc``, ``--ferrocenium`` : float, optional
Set the relative potential of the Fc/Fc<sup>+</sup> redox couple (given in V) to adjust the x-axis for data reporting.

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

#### ``-v`` : flag, optional
Enable view only mode. No data processing is performed and a plot of the data set is shown.

### User Config Args
Args related to user-configured settings.

#### ``-crd``, ``-–clear_root_dir`` : flag, optional
Reset the root directory back to the default location (in the user's home directory).

#### ``-grd``, ``–-get_root_dir`` : flag, optional
Print the current root directory to the console.

#### ``-srd``, ``-–set_root_dir`` : string, optional
Specify a root directory to simplify file path entry. For instance, if you store all your CV data files in a common folder, you can designate it as the root directory. Subsequently, any path provided with ``-p`` is assumed to be relative to the root directory.

**Without root directory:**
```
# Must type full file path
cvp -p C:\mydata\CV_Data\mydata.bin
```

Without a root directory, you must type the full path to the data. 

**With root directory:**
```
# Set the root directory
cvp -srd C:\mydata\CV_Data

# Only need short file path
cvp -p mydata.bin
```

By setting a root directory, you can omit the root directory part of the path. The root directory is saved between runs in a config file.

### Other args
Other miscellaneous args.

#### ``-h``, ``--help`` : flag
Use ``-h`` to get help with command line arguments.

#### ``-fp``, ``--file_picker`` : flag, optional
Interactively pick a .bin file from the terminal. The file is opened in view only mode.

#### ``--tree`` : flag, optional
Print the ``root_directory`` file tree to the console.

Examples
--------
Import the data from ``myfile.bin``, set the ferrocenium reference couple to +0.08 V, trim the data to keep two segments, starting from the second segment:
```
cvp -p C:\Desktop\MyData\myfile.bin -t 2 2 -fc 0.08
```

Multiview Mode
--------------
You can open multiple .bin files (in view-only mode) from the command line at once with the ``Multiviewer`` script. Navigate to a directory containing .bin files and run the command:
```
cvpmv -f some search filters
```

The script will open .bin files which contain any of the supplied search filters in view_only mode.

The default search behavior is an *OR* search. You can use supply the ``-a`` or ``--and_filter`` argument to perform an *AND* search:
```
cvpmv -f some search filters -a
```

Now only .bin files with contain *all* of the search filters in their name will be opened.

**Examples:**
```
cvpmv -f copper DMF
```
OR search, open .bin files with ``copper`` *OR* ``DMF`` in their filename.

```
cvpmv -f copper DMF FcPF6 -a
```
AND search, open .bin files with ``copper``, ``DMF``, *AND* ``FcPF6`` in their filename.

Uninstall
---------
To uninstall ``cv_pro``, run the following command:
```
pip uninstall cv_pro
```
