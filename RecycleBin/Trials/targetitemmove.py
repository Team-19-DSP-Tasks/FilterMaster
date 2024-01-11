import pyqtgraph as pg
from PyQt5.QtCore import QPointF


class MyPlot(pg.PlotWidget):
    def __init__(self):
        super(MyPlot, self).__init__()

        # Create a TargetItem
        self.target_item = pg.TargetItem()

        # Add the TargetItem to the plot
        self.addItem(self.target_item)

        # Connect the sigRegionChanged signal to the custom function
        self.target_item.sigPositionChanged.connect(self.target_item_moved)

    def target_item_moved(self):
        # Get the position of the TargetItem
        position = self.target_item.pos()

        # Do something with the position, e.g., print it
        print(f"TargetItem moved to: {position}")


if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    plot = MyPlot()
    plot.show()
    sys.exit(app.exec_())
