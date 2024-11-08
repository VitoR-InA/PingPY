# PingPY
![showcase](https://github.com/user-attachments/assets/716d07a7-c7a3-4454-95d7-488263be6232)

![GitHub License](https://img.shields.io/github/license/VitoR-InA/PingPY)
![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)

## Description
**PingPY** - A game written in python using the pygame library for creating 2D games, pygame integration that adds a user interface - pygame-gui and the pymunk library for simulating physics.

## Build it yourself
```sh
git clone https://github.com/VitoR-InA/PingPY
cd PingPY
```
### You can build it using pyinstaller
```sh
pyinstaller --windowed --clean Ping.py
```
**!The game uses the _internal folder to store logs and music, the absence of logs and music folders will cause the game to crash!** Before playing, copy the music and logs folders from _internal to dest\\_internal after building via pyinstaller

### or you can use [build.bat](build.bat)
```sh
build
```

> See [pygame gui freezing issue](https://pygame-gui.readthedocs.io/en/latest/freezing.html) if you have any problems