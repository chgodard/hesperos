# ============ Import python packages ============
import napari
from qtpy import QtCore


# ============ Define napari widgets to disable ============
label_layer_widget_list = [
    'blendComboBox',
    'colorModeComboBox',
    'colormapUpdate',
    'contigCheckBox',
    'contourSpinBox',
    'ndimSpinBox',
    'pick_button',
    'preserveLabelsCheckBox',
    'renderComboBox',
    'renderLabel',
    'selectionSpinBox',
]

image_layer_widget_list = [
    'attenuationLabel',
    'attenuationSlider',
    'blendComboBox',
    'colorbarLabel',
    'colormapComboBox',
    'gammaSlider',
    'interpComboBox',
    'interpLabel',
    'isoThresholdLabel',
    'isoThresholdSlider'
]

label_colors = {
    0: 'transparent',
    1: 'red',
    2: 'cyan',
    3: (87/255, 219/255, 0/255, 1),
    4: 'yellow',
    5: 'pink',
    6: 'blue',
    7: 'magenta',
    8: (15/255, 73/255, 55/255, 1),
    9: (178/255, 119/255, 255/255, 1),
    10: 'orange',
    11: (127/255, 162/255, 168/255, 1),
    12: (37/255, 22/255, 43/255, 1),
    13: (249/255, 214/255, 255/255, 1),
    14: (109/255, 155/255, 52/255, 1),
    15: (132/255, 127/255, 25/255, 1),
    16: (96/255, 11/255, 224/255, 1),
    17: 'green',
    18: (104/255, 39/255, 127/255, 1),
    19: (99/255, 97/255, 97/255, 1),
    20: (38/255, 24/255, 201/255, 1),
    21: (61/255, 67/255, 119/255, 1),
    22: (105/255, 255/255, 30/255, 1),
    23: (65/255, 127/255, 252/255, 1),
    24: (153/255, 153/255, 153/255, 1),
    25: (193/255, 193/255, 48/255, 1),
    26: (223/255, 131/255, 226/255, 1),
    27: (55/255, 5/255, 68/255, 1),
    28: (56/255, 40/255, 5/255, 1),
    29: (226/255, 61/255, 97/255, 1),
    30: (43/255, 13/255, 119/255, 1),
    31: (119/255, 3/255, 50/255, 1),
    32: (13/255, 140/255, 163/255, 1),
    33: (198/255, 169/255, 95/255, 1),
    34: (117/255, 198/255, 113/255, 1),
    35: (221/255, 108/255, 59/255, 1),
}

# ============ Function to custom napari viewer buttons ============
def disable_napari_buttons(viewer):
    """
    Disable some napari functions to hide them from user interation

    Parameters
    ----------
    viewer : napari.Viewer
        active (unique) instance of the napari viewer

    """
    viewer.window._qt_viewer.viewerButtons.consoleButton.setVisible(False)
    viewer.window._qt_viewer.viewerButtons.gridViewButton.setVisible(False)
    viewer.window._qt_viewer.viewerButtons.ndisplayButton.setVisible(False)
    viewer.window._qt_viewer.viewerButtons.resetViewButton.setVisible(False)

    viewer.window._qt_viewer.layerButtons.newShapesButton.setVisible(False)
    viewer.window._qt_viewer.layerButtons.newPointsButton.setVisible(False)
    viewer.window._qt_viewer.layerButtons.newLabelsButton.setVisible(False)
    viewer.window._qt_viewer.layerButtons.deleteButton.setVisible(False)

def disable_dock_widget_buttons(viewer):
    """_summary_

    Args:
        viewer (_type_): _description_
    """
    # for dw in list(viewer.window._dock_widgets.values()):
    #     dw.title.close_button.hide()

def increase_napari_buttons_size(viewer):
    """
    Increase napari button size

    Parameters
    ----------
    viewer : napari.Viewer
        active (unique) instance of the napari viewer
    
    """
    viewer.window._qt_viewer.viewerButtons.rollDimsButton.setGeometry(100, 100, 2000, 2000)
    viewer.window._qt_viewer.viewerButtons.transposeDimsButton.setGeometry(100, 100, 2000, 2000)

def reset_dock_widget(viewer):
    if hasattr(napari, 'DOCK_WIDGETS'):
        while len(napari.DOCK_WIDGETS) !=0:
            for layers in ("image", "annotations", "segmentation", "probabilities"):
                if layers in viewer.layers:
                    viewer.layers.remove(layers)

            viewer.window.remove_dock_widget(napari.DOCK_WIDGETS[-1])
            napari.DOCK_WIDGETS.pop(-1)

def disable_layer_widgets(viewer, layer_name, layer_type):
    """
    Disable some options in the selected layer to hide them from user interation

    Parameters
    ----------
    viewer : napari.Viewer
        active (unique) instance of the napari viewer
    layer_name: int
        name of the layer to clean

    """

    if layer_type == 'image':
        layer = viewer.layers[layer_name]
        list_widget_to_remove = image_layer_widget_list
        indx_while = 4
        indx_item = 4

    elif layer_type == 'label':
        layer = viewer.layers[layer_name]
        list_widget_to_remove = label_layer_widget_list
        indx_while = 9
        indx_item = 7       

    else:
        return

    qctrl = viewer.window._qt_viewer.controls.widgets[layer]
    for wdg in list_widget_to_remove:
        getattr(qctrl, wdg).setVisible(False)

    glayout = qctrl.grid_layout
    glayout.setAlignment(QtCore.Qt.AlignTop)
    
    while glayout.count() != indx_while:
        item = glayout.takeAt(indx_item)
        widget = item.widget()
        if widget:
            widget.deleteLater()
        glayout.removeItem(item)