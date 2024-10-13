import argparse
import pathlib
import platform
import shutil
import sys
import os

import PyInstaller.__main__

from curve_extractor.constants import VER


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Script to build the executable for the CurveExtractor software."
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        default=False,
        help="Clean the current directory. " "[Default : False]",
    )
    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        default=False,
        help="Build the app. [Default : False]",
    )
    args = parser.parse_args()
    ####################################################

    match platform.system():
        case "Windows":
            os_name = "win"
            separator = ";"
            splash = True

        case "Linux":
            os_name = "linux"
            separator = ":"
            splash = True

        case "Darwin":
            os_name = "macos"
            separator = ":"
            splash = False

        case _:
            print(f"Os {os_name:s} is not supported!")
            sys.exit(1)

    project_root = pathlib.Path(__file__).parent.parent.parent

    # Remove dist and build folder
    if args.clean:
        shutil.rmtree(f"{project_root.as_posix():s}/dist/")
        shutil.rmtree(f"{project_root.as_posix():s}/build/")
        os.remove(
            f"{project_root.as_posix():s}/CurveExtractor_v{VER:s}_{os_name:s}.spec"
        )

    # Build the executable
    if args.build:
        arguments = [
            f"{project_root.as_posix():s}/src/curve_extractor/main.py",
            "--onefile",
            "--noconsole",
            f"--icon={project_root.as_posix():s}/assets/icon.ico",
            f"--name=CurveExtractor_v{VER:s}_{os_name:s}",
            f"--add-data={project_root.as_posix():s}/assets/icon.ico{separator:s}resources",
            f"--add-data={project_root.as_posix():s}/assets/placeholder.png{separator:s}resources",
        ]

        if splash:
            arguments.append(f"--splash={project_root.as_posix():s}assets/splash.png")

        PyInstaller.__main__.run(arguments)

    sys.exit(0)


if __name__ == "__main__":
    main()
