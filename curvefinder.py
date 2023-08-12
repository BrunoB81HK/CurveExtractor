import cv2
from tkinter import Tk, filedialog, messagebox, simpledialog
from screeninfo.screeninfo import get_monitors
from numpy import zeros, append, array, polyfit, linspace
from math import atan, pi, cos, log10
import matplotlib.pyplot as plt


class CurveFinder:
    pts = zeros(4, dtype=tuple)
    coord = zeros(4, dtype=float)
    pts_final = zeros((0, 2))
    origin = (0, 0)
    angle = 0
    curve1 = {}
    curve2 = {}
    Xpr = 0
    Ypr = 0
    ratio = 7/8
    k = 0
    g = 0

    def __init__(self):
        root = Tk()
        root.withdraw()
        self.eq_y_from_x = messagebox.askyesno("Mode selection", "Select the equation you want to extract :\n"
                                                                 "y = f(x) : (YES)\n"
                                                                 "x = f(y) : (NO)")

        # Get the filepath to the picture
        self.file_path = filedialog.askopenfilename(title="Select the graph picture",
                                                    filetypes=(("png files", "*.png"), ("jpeg files", "*.jpg")))

        # Get the ratio of the picture
        self.graph = cv2.imread(self.file_path)
        self.new_graph = cv2.imread(self.file_path)
        (self.h, self.w, d) = self.graph.shape

        # Create the window and
        self.create_window()

        cv2.setMouseCallback('Graph', self.on_mouse_click)
        cv2.waitKey(0)

        # Ask if logarithmic or linear
        self.xlin = messagebox.askyesno("X-Axis type", "Is the X-Axis linear or logarithmic base 10?\n"
                                                                 "Linear : (YES)\n"
                                                                 "Log : (NO)")
        self.ylin = messagebox.askyesno("Y-Axis type", "Is the Y-Axis linear or logarithmic base 10?\n"
                                                                 "Linear : (YES)\n"
                                                                 "Log : (NO)")

        # Resize and rotate the image
        self.resize_and_rotate()

        # Ask for the order of the polynomial
        self.order = simpledialog.askinteger("Order of the equation",
                                             "What is the desired order for the desired equation? (0 to 5)")
        if 0 < self.order <= 5:
            good_answer = True
        else:
            good_answer = False
        while not good_answer:
            self.order = simpledialog.askinteger("Order of the equation",
                                                 "Invalid order...\n"
                                                 "What is the desired order for the desired equation? (0 to 5)")
            if 0 < self.order <= 5:
                good_answer = True

        # Find the curve(s) and find the points
        cv2.setMouseCallback('Graph', self.on_mouse_click_collect)
        key = 0
        text = 'Press "q" when you have enough points.'
        print(text + "\n")
        cv2.putText(self.new_graph, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('Graph', self.new_graph)
        while key is not 113:
            key = cv2.waitKey(1)
        cv2.destroyWindow('Graph')

        # Get the curve function with curve smoothing
        if self.eq_y_from_x:
            self.coef = polyfit(self.pts_final[:, 0], self.pts_final[:, 1], self.order)
            var = "x"
        else:
            self.coef = polyfit(self.pts_final[:, 1], self.pts_final[:, 0], self.order)
            var = "y"

        # Output the formula
        for (i, c) in enumerate(self.coef):
            if i == 0:
                print("{0:0.3f}*".format(c) + var + "**{0}".format(self.order - i), end='')
            else:
                print(" + {0:0.3f}*".format(c) + var + "**{0}".format(self.order - i), end='')

        print("\n\nCoeffs : \n" + str(self.coef))

        root = Tk()
        root.withdraw()
        self.show_data = messagebox.askyesno("Print data points?", "Do you want to print the data points in the console?")
        if self.show_data:
            print(self.pts_final)

        # Graph the plot
        plt.plot(self.pts_final[:, 0], self.pts_final[:, 1], 'or')

        if self.eq_y_from_x:
            xx = linspace(min(self.pts_final[:, 0]), max(self.pts_final[:, 0]), 100)
            yy = self.get_pts(xx)
        else:
            yy = linspace(min(self.pts_final[:, 1]), max(self.pts_final[:, 1]), 100)
            xx = self.get_pts(yy)
        plt.plot(xx, yy, '-b')
        plt.xlim([min(self.pts_final[:, 0]), max(self.pts_final[:, 0])])
        plt.ylim([min(self.pts_final[:, 1]), max(self.pts_final[:, 1])])
        plt.show()

    def on_mouse_click(self, event, x, y, flags, user_params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pts[self.k] = (x, y)
            if self.k == 0:
                col = (204, 0, 0)
                txt = "X1"
            elif self.k == 1:
                col = (0, 153, 0)
                txt = "X2"
            elif self.k == 2:
                col = (0, 0, 153)
                txt = "Y1"
            else:
                col = (204, 204, 0)
                txt = "Y2"
            cv2.circle(self.new_graph, self.pts[self.k], 5, col, -1)
            cv2.putText(self.new_graph, txt, self.pts[self.k], cv2.FONT_HERSHEY_SIMPLEX, 1, col, 2)
            cv2.imshow('Graph', self.new_graph)
            self.k += 1

            if self.k == 4:
                self.k = 0
                msg_box = messagebox.askquestion('Warning', 'Satisfied with your choices?')
                if msg_box == 'yes':
                    self.coord[0] = simpledialog.askfloat("Coordinates", "X1?")
                    self.coord[1] = simpledialog.askfloat("Coordinates", "X2?")
                    self.coord[2] = simpledialog.askfloat("Coordinates", "Y1?")
                    self.coord[3] = simpledialog.askfloat("Coordinates", "Y2?")
                    self.new_graph = self.graph
                    cv2.destroyWindow('Graph')
                else:
                    self.new_graph = self.graph
                    cv2.imshow('Graph', self.new_graph)
                    messagebox.showinfo('Retry', 'You can now re-enter the coordinates.')

    def create_window(self):
        # Create the window
        mon = get_monitors()[0]
        mon_ratio = mon.width / mon.height

        cv2.namedWindow('Graph', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow('Graph', self.graph)

        if self.w/self.h < mon_ratio:
            cv2.resizeWindow('Graph', (int((self.ratio*mon.height)*self.w/self.h), int(self.ratio*mon.height)))
        else:
            cv2.resizeWindow('Graph', (int(self.ratio*mon.width), int((self.ratio*mon.width)*self.h/self.w)))

    def resize_and_rotate(self):
        self.create_window()
        if self.xlin:
            X1 = self.curve1["X1"] = self.pts[0][0]
            X2 = self.curve1["X2"] = self.pts[1][0]
            XL = self.curve2["XL"] = self.pts[2][0]
            dX = self.curve2["dX"] = self.pts[3][0] - XL
        else:
            X1 = self.curve1["X1"] = log10(self.pts[0][0])
            X2 = self.curve1["X2"] = log10(self.pts[1][0])
            XL = self.curve2["XL"] = log10(self.pts[2][0])
            dX = self.curve2["dX"] = log10(self.pts[3][0]) - XL

        if self.ylin:
            Y1 = self.curve2["Y1"] = self.pts[2][1]
            Y2 = self.curve2["Y2"] = self.pts[3][1]
            YL = self.curve1["YL"] = self.pts[0][1]
            dY = self.curve1["dY"] = self.pts[1][1] - YL
        else:
            Y1 = self.curve2["Y1"] = log10(self.pts[2][1])
            Y2 = self.curve2["Y2"] = log10(self.pts[3][1])
            YL = self.curve1["YL"] = log10(self.pts[0][1])
            dY = self.curve1["dY"] = log10(self.pts[1][1]) - YL

        A1 = self.curve1["A1"] = dY/(X2 - X1)
        A2 = self.curve2["A2"] = (Y2 - Y1)/dX

        X0 = int((A1*X1 - A2*XL + Y1 - YL)/(A1 - A2))
        Y0 = int(A1*(X0 - X1) + YL)
        self.origin = (X0, Y0)
        self.angle = theta = (atan(dY/(X2 - X1)) + atan(-dX/(Y2 - Y1)))/2

        pts_prime = zeros(4, dtype=tuple)
        pts_prime[0] = (int(X0 + (X1 - X0)/cos(theta)), Y0)
        pts_prime[1] = (int(X0 + (X2 - X0)/cos(theta)), Y0)
        pts_prime[2] = (X0, int(Y0 + (Y1 - Y0)/cos(theta)))
        pts_prime[3] = (X0, int(Y0 + (Y2 - Y0)/cos(theta)))

        self.Xpr = (self.coord[1] - self.coord[0])/(X2 - X1)
        self.Ypr = (self.coord[3] - self.coord[2])/(Y2 - Y1)

        M = cv2.getRotationMatrix2D(self.origin, 180*self.angle/pi, 1)
        self.new_graph = cv2.warpAffine(self.new_graph, M, self.new_graph.shape[1::-1], flags=cv2.INTER_LINEAR)

        for pt in pts_prime:
            cv2.circle(self.new_graph, pt, 5, (0, 0, 255), -1)

        cv2.imshow('Graph', self.new_graph)

    def on_mouse_click_collect(self, event, x, y, flags, user_params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pts_final = append(self.pts_final, array([[0, 0]]), axis=0)
            (a, b) = self.transform_p_to_r((x, y))
            if self.xlin:
                xr = a
            else:
                xr = 10**a
            if self.xlin:
                yr = b
            else:
                yr = 10**b
            self.pts_final[self.g] = array([xr, yr])
            self.g += 1
            cv2.circle(self.new_graph, (x, y), 5, (255, 0, 0), -1)
            cv2.imshow('Graph', self.new_graph)

    def transform_p_to_r(self, pt):
        (x, y) = pt
        xr = self.Xpr*(x - self.curve1["X1"]) + self.coord[0]
        yr = self.Ypr*(y - self.curve2["Y1"]) + self.coord[2]
        return array([xr, yr])

    def get_pts(self, aa):
        bb = zeros(len(aa))
        for (i, a) in enumerate(aa):
            for (j, c) in enumerate(self.coef):
                bb[i] += c*a**(self.order - j)

        return bb


if __name__ == "__main__":
    cf = CurveFinder()
