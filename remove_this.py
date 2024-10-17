import sys
from pandas import read_csv, to_datetime, Timestamp
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QWidget, QComboBox, QLabel, QGridLayout, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.widgets import RectangleSelector

class TimeSeriesPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = None
        self.selected_points = []
        self.date_column = None
        self.parameter_column = None

        # Initialize UI components
        self.initUI()

    def initUI(self):
        # Set window title and size
        self.setWindowTitle("Interactive Time Series Plotter")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Use QGridLayout for more control
        grid_layout = QGridLayout(self.central_widget)

        # Add widgets to the grid layout

        # Add a button to load CSV
        self.btn_load_csv = QPushButton('Load CSV', self)
        self.btn_load_csv.clicked.connect(self.load_csv)
        grid_layout.addWidget(self.btn_load_csv, 0, 0)

        # Add combo boxes and labels for selecting date and parameter columns
        self.lbl_date_col = QLabel('Select Date Column:', self)
        grid_layout.addWidget(self.lbl_date_col, 1, 0)

        self.combo_date_col = QComboBox(self)
        grid_layout.addWidget(self.combo_date_col, 2, 0)

        self.lbl_param_col = QLabel('Select Parameter Column:', self)
        grid_layout.addWidget(self.lbl_param_col, 3, 0)

        self.combo_param_col = QComboBox(self)
        grid_layout.addWidget(self.combo_param_col, 4, 0)

        # Add a button to plot the time series based on the selected columns
        self.btn_plot = QPushButton('Plot', self)
        self.btn_plot.clicked.connect(self.plot_time_series)
        grid_layout.addWidget(self.btn_plot, 5, 0)

        # Add a button to select points
        self.btn_select_points = QPushButton('Select Points', self)
        self.btn_select_points.clicked.connect(self.activate_selector)
        grid_layout.addWidget(self.btn_select_points, 0, 1)

        # Add a button to delete selected points
        self.btn_delete_points = QPushButton('Set Selected Points to No Data', self)
        self.btn_delete_points.clicked.connect(self.set_selected_points_to_no_data)
        grid_layout.addWidget(self.btn_delete_points, 1, 1)

        # Add a button to save the modified CSV
        self.btn_save_csv = QPushButton('Save CSV', self)
        self.btn_save_csv.clicked.connect(self.save_csv)
        grid_layout.addWidget(self.btn_save_csv, 2, 1)

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Add the canvas to the layout
        grid_layout.addWidget(self.canvas, 6, 0, 1, 2)

        # Create a navigation toolbar and add it to the layout
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        grid_layout.addWidget(self.toolbar, 7, 0, 1, 2)

        # Initialize RectangleSelector
        self.selector = RectangleSelector(self.ax, self.on_select, useblit=True,
                                          minspanx=5, minspany=5, spancoords='pixels',
                                          interactive=True)
        self.selector.set_active(False)

    def load_csv(self):
        # Open file dialog to load CSV
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            # Read CSV file into pandas DataFrame
            self.data = read_csv(file_path)

            # Populate the combo boxes with column names
            self.combo_date_col.clear()
            self.combo_param_col.clear()
            self.combo_date_col.addItems(self.data.columns)
            self.combo_param_col.addItems(self.data.columns)

    def plot_time_series(self):
        if self.data is not None:
            # Get selected columns for date and parameter
            self.date_column = self.combo_date_col.currentText()
            self.parameter_column = self.combo_param_col.currentText()

            # Check if the date column is already the index, and parse it if not
            if self.data.index.name != self.date_column:
                self.data[self.date_column] = to_datetime(self.data[self.date_column])
                self.data.set_index(self.date_column, inplace=True)

            # Clear the previous plot
            self.ax.clear()

            # Plot time series
            self.line, = self.ax.plot(self.data.index, self.data[self.parameter_column], 'bo-', picker=5, markersize=2)

            # Set titles and labels
            self.ax.set_title(f'{self.parameter_column} time series')
            self.ax.set_xlabel(self.date_column)
            self.ax.set_ylabel(self.parameter_column)

            # Refresh the canvas
            self.canvas.draw()

    def activate_selector(self):
        # Activate the rectangle selector
        self.selector.set_active(True)

    def on_select(self, eclick, erelease):
        # Get the coordinates of the rectangle
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        # Convert x1, x2 to datetime using mdates.num2date and remove timezone info
        x1 = Timestamp(mdates.num2date(x1)).tz_localize(None)
        x2 = Timestamp(mdates.num2date(x2)).tz_localize(None)

        # Find the points within the rectangle
        mask = (self.data.index >= min(x1, x2)) & (self.data.index <= max(x1, x2)) & \
               (self.data[self.parameter_column] >= min(y1, y2)) & (self.data[self.parameter_column] <= max(y1, y2))
        self.selected_points = self.data[mask].index

        # Highlight the selected points
        for point in self.selected_points:
            self.ax.plot(point, self.data.loc[point, self.parameter_column], 'ro')
        self.canvas.draw()

    def set_selected_points_to_no_data(self):
        if len(self.selected_points) > 0:
            # Set the selected points' parameter value to NaN
            self.data.loc[self.selected_points, self.parameter_column] = float('nan')
            self.selected_points = []

            # Update plot after setting points to NaN
            self.plot_time_series()

    def save_csv(self):
        if self.data is not None:
            # Open file dialog to save CSV
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_path:
                # Save the modified DataFrame to a new CSV file
                self.data.to_csv(file_path)
                print(f"CSV saved to {file_path}")

def main():
    # Initialize the application
    app = QApplication(sys.argv)

    # Create the main window
    main_window = TimeSeriesPlot()

    # Show the main window
    main_window.show()

    # Run the application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
