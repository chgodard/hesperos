source PATH_TO_ADD/etc/profile.d/conda.sh

conda create -n hesperos_env python=3.9

conda activate hesperos_env

pip install napari==0.4.14

conda install -c anaconda pyqt

exit
