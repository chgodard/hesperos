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