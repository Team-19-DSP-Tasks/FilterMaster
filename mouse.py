import pyqtgraph as pg


def update_plot(event):
    x, y = event[0]["pos"]
    # Calculate frequency based on mouse speed
    freq = abs(x - prev_x) + abs(y - prev_y)
    # Update plot data
    data.append(freq)
    curve.setData(data)
    # Update previous mouse position
    prev_x, prev_y = x, y


# Create plot widget
pw = pg.PlotWidget()
pw.show()

# Create plot data
data = []
curve = pw.plot(data)

# Connect mouse move signal to update_plot function
proxy = pg.SignalProxy(pw.scene().sigMouseMoved, rateLimit=60, slot=update_plot)

# Start Qt event loop
pg.QtGui.QApplication.exec_()
