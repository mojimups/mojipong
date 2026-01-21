# mojipong
A fast-paced pong rendition featuring satisfying visual and auditory flares, a tough but fair and humanized AI opponent, and both solo and multiplayer modes — built with Pygame in 2023 as a college assignment.

### Dependency installation
1. Open cmd in this folder
2. Type in:
   1. python -m venv venv
   2. venv\Scripts\Activate
   3. pip install -r requirements.txt

### Run instructions
1. Open cmd in this folder
2. Type in:
   - python main.py

### Build instructions
1. Open cmd in this folder
2. Type in:
   - pyinstaller --onefile --noconsole --icon=icon.ico --add-data "assets;assets" main.py
3. The finished build will be in /dist
