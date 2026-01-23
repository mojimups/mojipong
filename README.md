# MOJIPONG
MOJIPONG is my fast-paced rendition of Pong, featuring satisfying visual and auditory flares, a humanized AI opponent that is tough but beatable, and both solo and multiplayer modes. This game was built with Pygame in 2023 as a college assignment.

### Dependency installation
1. Open cmd in this folder
2. Type in:
   1. python -m venv venv
   2. venv\Scripts\Activate
   3. pip install -r requirements.txt

### Local run instructions
1. Open cmd in this folder
2. Type in:
   - .\venv\Scripts\activate
   - cd project
   - python main.py

### Web run instructions
1. Open cmd in this folder
2. Type in:
   - .\venv\Scripts\activate
   - pygbag project
3. The finished "web folder" will be in /build
4. (Optional) Replace these colors in index.html
   - powderblue -> black
   - #7f7f7f -> black

### Build instructions
1. Open cmd in this folder
2. Type in:
   - .\venv\Scripts\activate
   - cd project
   - pyinstaller --name "MOJIPONG" --onefile --noconsole --icon=icon.ico --add-data "assets;assets" main.py
3. The finished build will be in /dist
