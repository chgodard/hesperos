<div align="justify">
    
# Hesperos plugin for Napari

[![License](https://img.shields.io/pypi/l/hesperos.svg?color=green)](https://github.com/DBC/hesperos/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/hesperos.svg?color=green)](https://pypi.org/project/hesperos)
[![Python Version](https://img.shields.io/pypi/pyversions/hesperos.svg?color=green)](https://python.org)
[![tests](https://github.com/DBC/hesperos/workflows/tests/badge.svg)](https://github.com/DBC/hesperos/actions)
[![codecov](https://codecov.io/gh/DBC/hesperos/branch/main/graph/badge.svg)](https://codecov.io/gh/DBC/hesperos)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/hesperos)](https://napari-hub.org/plugins/hesperos)

    TODO : DESCRIPTION

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

# Table of Contents
- [Installation and Requirements](#installation-and-requirements)
    * [Automatic installation](#automatic-installation)
    * [Manual installation](#manual-installation)
- [Use Hesperos plugin](#use-hesperos-plugin)

    
# Installation and Requirements
Hesperos plugin is designed to run on Windows or Macos with python 3.8, 3.9 or 3.10.
     
## Automatic installation
1. Install [Anaconda] and deselect *Add to PATH*. Note the path where you install anaconda.
2. Download only the installation folder: [*script_files*]](/script_files)
3. Add Anaconda path:
    1. <ins>For Windows</ins>: Right click on the .bat files (for [installation](/script_files/for_Windows/install_hesperos_env.bat) and [running](/script_files/for_Windows/run_hesperos.bat)) and select *Modify*. Change the anaconda_dir to your anaconda path. Then save changes.
        > for exemple: $ `anaconda_dir=C:\Users\chgodard\anaconda3 ` 
    2. <ins>For Macos</ins>:
        1. Right click on the .command files (for [installation](/script_files/for_Macos/install_hesperos_env.command) and [running](/script_files/for_Macos/run_hesperos.command)) and select *Open with TextEdit*. Change the PATH_TO_ADD with your anaconda3 path. Then save changes.
            > for exemple: $ `source ~/opt/anaconda3/etc/profile.d/conda.sh ` 
        2. On your terminal allow running of your .command files (change PATH with the path of your .command files) : 
            > $ `chmod u+x PATH/install_hesperos_env.command `
    
            > $ `chmod u+x PATH/run_hesperos.command `
4. Double click on the **install_hesperos_env file** to create a anaconda virtual environment with python 3.9 and napari 0.4.14
5. Double click on the **run_hesperos file** to run napari from your virtual environment.
6. On Napari: 
    1. Go to *Plugins/Install Plugins...*
    2. Search for "hesperos" (it can take a while to load).
    3. Install **hesperos** plugin.
    4. When installation is done, close Napari. A restart of Napari is needed to take in consideration the new installed plugin.
7. Double click on the **run_hesperos file** to run napari.
8. Use the hesperos plugin in *Plugins/hesperos*

## Manual installation
1. Install [Anaconda] and deselect *Add to PATH*. Note the path where you install anaconda.
2. Open your anaconda prompt command
3. Install python 3.8, 3.9 or 3.10
4. Install Python packages (in the conda virtual environment)
    > $ ` conda install -c conda-forge napari=0.4.14`
    
    > $ ` pip install hesperos`                            
5. Launch Napari 
    > $ ` napari`

    
# Use Hesperos plugin
    TODO
    
## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"hesperos" is free and open source software

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
    
[Anaconda](https://www.anaconda.com/products/distribution#Downloads)
