set anaconda_dir=PATH_TO_ADD

call %anaconda_dir%\Scripts\activate.bat %anaconda_dir%

call conda create -n hesperos_env python=3.9

call conda activate hesperos_env

call pip install napari==0.4.14

call conda install -c anaconda pyqt

call pip install vispy==0.9.6

exit
