``cv_pro``
==========
``cv_pro`` is a command line tool for processing CV data files (``.bin`` format) created from the CH Instruments chi760e electrochemical workstation.

Key Features
------------
✅ Parse binary ``.bin`` files and export as directly plottable and nicely formatted ``.csv`` files

✅ Process CV traces (truncate segments, x-axis correction)

✅ Automatic determination of E½ values

✅ Interactive plotting with Matplotlib


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
Clone this repo and use [setuptools](https://setuptools.pypa.io/en/latest/userguide/quickstart.html) and [build](https://pypi.org/project/build/) to build the package (``python -m build``) then use pip to install the resulting ``.whl`` file.

Command Line Interface
----------------------
With ``cv_pro`` installed, you can run the script directly from the command line using the ``cvp`` shortcut. To begin processing data, use ``process`` and specify the path to your data:

**Process .bin file:**
```
cvp process path\to\your\data.bin
```

**Tip:** You can use shorter paths by setting a [**root directory**](#file-paths--root-directory) or by simply opening a terminal session inside the same directory as your data files.


Command Line Arguments
----------------------
- [Data Processing Args](#data-processing-args-process-proc-p)
- [User Config Args](#user-config-args-config-cfg)
- [Other Args](#other-args-and-subcommands)

### Data Processing Args (process, proc, p)
Process CV data with the ``process`` subcommand.

**Usage:**
``cvp process <path> <options>``, ``cvp proc <path> <options>``, or ``cvp p <path> <options>``

#### ``path`` : string, required
The path to a CV data .bin file. You have three options for specifying the path: you can use a **path relative to the current working directory**, an **absolute path**, or a **path relative to the root directory** (if one has been set).

#### ``-ne``, ``--no-export`` : flag, optional
Bypass the data export prompt at the end of the script.

#### ``-v`` : flag, optional
Enable view only mode. No data processing is performed and a plot of the data set is shown.

#### ``-fc``, ``--ferrocenium`` : float, optional
Set the relative potential of the Fc/Fc<sup>+/0</sup> redox couple (given in V) to adjust the x-axis for data reporting.

#### ``-sep``, ``--peak_sep_limit`` : float, optional
The maximum distance (given in V) between two peaks for them to be considered "reversible". If the distance between two peaks if within the limit, E<sub>1/2</sub> calculations will be attempted.

#### ``-tr``, ``--trim`` : 2 integers, optional
Use ``-tr`` to select a range of CV segment traces. Segments are numbered in order starting from 1. Segments before the first integer and after the second integer will be removed. Give ``-1`` for the second value to show all sweeps following the sweep specified by the first value.

```
# Keep only the second and third sweep
cvp p C:\Desktop\MyData\myfile.bin -tr 2 3

# Show all sweeps after the 4th sweep
cvp p C:\Desktop\MyData\myfile.bin -tr 4 -1
```

#### ``--pub`` : flag, optional
Generate a publication quality figure (BETA).

___
### User Config Args (config, cfg)
View, edit, or reset user-configured settings with the ``config`` subcommand.

**Usage:**
``cvp config <option>`` or ``cvp cfg <option>``

Current user-configurable settings:

- ``root_directory`` - A base directory which contains UV-vis data files. Set a root directory to enable the use of shorter, relative file paths.

- ``primary_color`` - The main color used in terminal output. Can be set to any of the 8 basic ANSI colors.

#### ``--delete`` : flag, optional
Delete the config file and directory. The config file is located in ``.config/uv_pro/`` inside the user's home directory.

#### ``-e``, ``--edit`` : flag, optional
Edit configuration settings. Will prompt the user for a selection of configuration settings to edit.

#### ``-l``, ``--list`` : flag, optional
Print the current configuration settings to the console.

#### ``-r``, ``--reset`` : flag, optional
Reset configuration settings back to their default value. Will prompt the user for a selection of configuration settings to reset.

___
### Other args and subcommands
Other miscellaneous args and subcommands.

#### ``-h``, ``--help`` : flag, optional
Use ``-h`` to get help with command line arguments. Get help for specific commands with ``cvp <command> -h``.

#### ``tree`` : subcommand
Print the root directory file tree to the console. Usage: ``cvp tree``.

Examples
--------
Import the data from ``myfile.bin``, set the ferrocenium reference couple to +0.08 V, trim the data to keep two segments, starting from the second segment:
```
cvp -p C:\Desktop\MyData\myfile.bin -t 2 2 -fc 0.08
```

File Paths & Root Directory
---------------------------
``cv_pro`` is flexible in handling file paths. When you give a path at the terminal, you can provide a full absolute path:
```
cvp p C:\full\path\to\your\data\file.KD
```
Alternatively, you can open a terminal session inside a directory containing a data file and use a relative path:
```
# Current working directory = C:\full\path\to\your\data
cvp p file.bin
```

Setting a root directory can simplify file path entry. For instance, if you store all your CV data files in a common folder, you can designate it as the root directory. Subsequently, any path provided with ``process`` can be given relative to the root directory.

***Without* root directory:**
```
# Must type full file path
cvp p "C:\mydata\CV Data\mydata.bin"
```

Without a root directory, you must type the full path ``"C:\mydata\CV Data\mydata.bin"`` to the data. 

***With* root directory:**
```
# Set the root directory.
cvp config -edit

# Select the root directory setting and enter the desired path, for example:
"C:\mydata\CV Data"

# Now, a shorter relative path can be used.
cvp p mydata.bin
```

With a root directory set, for example ``"C:\mydata\CV Data"``, you can omit that part of the path and just give a relative path ``mydata.bin``. The root directory is saved between runs in a config file.

Multiview Mode
--------------
You can open multiple .KD files (in *view-only* mode) simultaneously with the ``multiviewer`` subcommand. Navigate to a directory containing .bin files and run the command:
```
cvp mv -f some search filters
```

The script will open .bin files which contain any of the supplied search filters in *view-only* mode. You can omit the ``-f`` argument to open *all* .bin files in the current working directory.

The default search behavior is an *OR* search. You can use the ``-a`` or ``--and-filter`` argument to perform an *AND* search:
```
cvp mv -f some search filters -a
```

Now only .bin files with contain *all* of the search filters in their name will be opened.

**Examples:**
```
cvp mv -f copper DMF
```
OR search, open .bin files with ``copper`` *OR* ``DMF`` in their filename.

```
cvp mv -f copper DMF RT -a
```
AND search, open .bin files with ``copper``, ``DMF``, *AND* ``RT`` in their filename.

Uninstall
---------
To uninstall ``cv_pro``, run the following command:
```
pip uninstall cv_pro
```
