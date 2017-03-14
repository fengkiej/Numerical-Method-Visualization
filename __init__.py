from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application, rationalize, \
    convert_xor, parse_expr
from PyQt5 import QtGui
from pyqtgraph import setConfigOption, PlotWidget
from re import compile, search
from numpy import vectorize, arange, array
from sympy import lambdify
from src.SecantMethod import SecantMethod

APPLICATION_NAME = "Numerical Method"
ENABLE_IMPLICIT_MULTIPLICATION = \
    (standard_transformations + (implicit_multiplication_application, rationalize, convert_xor,))

setConfigOption('background', 'w')
setConfigOption('foreground', 'k')
app = QtGui.QApplication([APPLICATION_NAME])

# defining window components
enter_btn = QtGui.QPushButton('Find root')
function_txt = QtGui.QLineEdit('')
fx_label = QtGui.QLabel('f(x) = ')
method_dropdown = QtGui.QComboBox()
plot_widget = PlotWidget()

next_btn = QtGui.QPushButton('>')
prev_btn = QtGui.QPushButton('<')
fastfwd_btn = QtGui.QPushButton('>>')
fastbwd_btn = QtGui.QPushButton('<<')
text_edit = QtGui.QTextEdit()


def enter_btn_clicked():
    REGEX_PATTERN = "((\d*[cos sin tan]*x*\s*[\/ \+ \- \* \^]\s*)*\d*[cos sin tan]*x*)$"
    REGEX = compile(REGEX_PATTERN)
    text_edit.setText("")
    f_str = function_txt.text()

    # workaround
    step = Step()
    step.reset_step() #just to make sure
    ############

    try:
        if not REGEX.fullmatch(f_str): raise SyntaxError
        if search(r"^\b\d+\b$", f_str): raise AssertionError
        fx = parse_expr(f_str, transformations=ENABLE_IMPLICIT_MULTIPLICATION)
    except SyntaxError:
        function_txt.setText("invalid input")
        return
    except AssertionError:
        function_txt.setText("constant function")
        return

    method = SecantMethod(fx)
    method.start()

    point_list = [[round(x, 2), round(y, 2)] for [x, y] in method.get_point_list()]
    root_str = "\n\nRoot: " + str(method.get_root())
    point_list_str = '\n'.join(list(map(lambda item: str(item), point_list)))
    text_edit.setText(point_list_str + root_str)

    fx_eq = vectorize(lambdify('x', fx))
    plot_widget.getPlotItem().sigRangeChanged.connect(lambda: update_graph(fx_eq, point_list, step.get_step()))
    update_graph(fx_eq, point_list, step.get_step())

    next_btn.clicked.connect(lambda: next(fx_eq, point_list, step))
    prev_btn.clicked.connect(lambda: prev(fx_eq, point_list, step))


def next(fx_eq, point_list, step):
    if step.get_step() < len(point_list) - 2:
        step.increment_step()
        update_graph(fx_eq, point_list, step.get_step())


def prev(fx_eq, point_list, step):
    if step.get_step() > 0:
        step.decrement_step()
        update_graph(fx_eq, point_list, step.get_step())


def update_graph(fx_eq, point_list, step):
    plot_widget.clear()
    update_fx_graph(fx_eq, 'k')
    update_secant_graph(point_list, step)


def update_secant_graph(point_list, step):
    x_l1 = [point_list[step][0], point_list[step + 1][0]]
    y_l1 = [point_list[step][1], point_list[step + 1][1]]

    try:
        m = (y_l1[1] - y_l1[0]) / (x_l1[1] - x_l1[0])
    except ZeroDivisionError:
        m = (y_l1[1] - y_l1[0]) / (x_l1[1] - x_l1[0] + 10 ** -5)
    func = "%f(x - %f) + %f" % (m, x_l1[0], y_l1[0])
    fx = parse_expr(func, transformations=ENABLE_IMPLICIT_MULTIPLICATION)

    update_fx_graph(vectorize(lambdify('x', fx)), 'b')

    try:
        xn = point_list[step + 2][0]
        x_l2 = [point_list[step + 1][0], point_list[step + 2][0]]
        y_l2 = [point_list[step + 1][1], point_list[step + 2][1]]
    except IndexError:
        xn = point_list[step + 1][0]
        plot_widget.getPlotItem().addLine(x=xn)
        plot_widget.plot(x_l1, y_l1, pen='b', symbol='o')
        return

    plot_widget.plot(x_l1, y_l1, pen='b', symbol='o')
    plot_widget.plot(x_l2, y_l2, pen='r', symbol='o')
    plot_widget.getPlotItem().addLine(x=xn)


def update_fx_graph(fx_eq, color):
    cur_range = plot_widget.viewRange()
    x_min = cur_range[0][0]
    x_max = cur_range[0][1]
    y_min = cur_range[1][0]
    y_max = cur_range[1][1]

    x_coord = arange(x_min, x_max, 0.07)
    y_coord = fx_eq(x_coord)
    xy_coord = array([[x, y] for x, y in zip(x_coord, y_coord) if y_min <= y <= y_max])
    plot_widget.getPlotItem().plot(xy_coord, pen=color)


def make_gui():
    w = QtGui.QWidget()

    layout = QtGui.QGridLayout()
    w.setLayout(layout)

    method_dropdown.addItem('Secant Method')
    text_edit.setReadOnly(True)
    text_edit.setMaximumWidth(next_btn.sizeHint().width() * 1.5)

    layout.addWidget(plot_widget, 1, 1, 8, 4)
    layout.addWidget(fx_label, 9, 1)
    layout.addWidget(function_txt, 9, 2)
    layout.addWidget(enter_btn, 9, 3, 1, 3)
    layout.addWidget(method_dropdown, 10, 1, 1, 5)
    layout.addWidget(fastbwd_btn, 1, 5)
    layout.addWidget(prev_btn, 2, 5)
    layout.addWidget(next_btn, 3, 5)
    layout.addWidget(fastfwd_btn, 4, 5)
    layout.addWidget(text_edit, 5, 5, 4, 1)

    w.show()
    app.exec_()


def main():
    # define widget behaviour
    enter_btn.clicked.connect(lambda: enter_btn_clicked())
    plot_item = plot_widget.getPlotItem()
    plot_item.enableAutoScale()
    plot_item.showGrid(True, True, .45)
    plot_item.setDownsampling(True, True, 'subsample')
    plot_item.clipToViewMode()
    plot_item.getViewBox().setRange(xRange=[-10, 10], yRange=[-10, 10])
    make_gui()


# Dirty hack, a workaround for saving the state of the step
class Step:
    step = 0

    def __init__(self):
        self.reset_step()

    def reset_step(self):
        self.step = 0

    def increment_step(self):
        self.step += 1

    def decrement_step(self):
        if self.step > 0:
            self.step -= 1

    def get_step(self):
        return self.step


if __name__ == "__main__":
    main()
