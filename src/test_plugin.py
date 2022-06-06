import napari

from hesperos._manual_widget import ManualSegmentationWidget
from hesperos._oneshot_widget import OneShotWidget

def main():
    with napari.gui_qt():
        viewer = napari.Viewer()
        widget = ManualSegmentationWidget(viewer)
        dw1 = viewer.window.add_dock_widget(widget, name="FUCKINGPOTATOS", area="right")
        dw1.NoDockWidgetFeatures = 1
        napari.run()


if __name__ == "__main__":
    main()