# CurveExtractor

![Build status](https://github.com/BrunoB81HK/CurveFinder/actions/workflows/build_and_release.yml/badge.svg)

Simple app to let you extract the equations from a graph

### Building with pyinstaller

1. Create a virtual environment.
   ```shellsession
   user@computer:.../CurveFinder$ python -m venv ./venv
   ```
2. Activate the virtual environment.
   ```shellsession
   user@computer:.../CurveFinder$ source ./venv/bin/activate
   ```
3. Install the dependencies from `requirements.txt`.
   ```shellsession
   user@computer:.../CurveFinder$ pip install -r requirements.txt
   ```
4. Build the executable.
   ```shellsession
   user@computer:.../CurveFinder$ python build.py -b
5. The executable is now available in the `./dist` directory.
