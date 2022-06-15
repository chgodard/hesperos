set anaconda_dir=PATH_TO_ADD

call %anaconda_dir%\Scripts\activate.bat %anaconda_dir%

call conda create -n hesperos_env python=3.9

call conda activate hesperos_env

call conda install -c conda-forge napari=0.4.14

call conda install -c anaconda pyqt

exit