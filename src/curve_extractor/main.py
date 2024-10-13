import random
import sys

from QCurveFinder.application import QCurveFinder
from PyQt5.QtWidgets import QApplication

try:
    import pyi_splash

    splash = True
except ModuleNotFoundError:
    splash = False


def main() -> None:
    random.seed(123456)
    app = QApplication([])
    window = QCurveFinder()

    if splash:
        pyi_splash.close()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
