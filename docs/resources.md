Resources Guide
=============== 

PingPY uses zip files for comressing all data in one file. So this way is easier for customizing your own theme. PingPY supports many resource files in resources directory.

You can see resource directory example below.
```
.
├── sounds/
│   ├── ball/
│   │   ├── jump1.wav
│   │   ├── jump2.wav
│   │   └── ...
│   ├── game/
│   │   ├── music.wav
│   │   └── start.wav
│   └── player/
│       ├── damage.wav
│       ├── die.wav
│       └── win.wav
├── textures/
│   ├── ball.png
│   └── player.png
└── ui_theme.json
```

How it works
------------
- **sounds**
    - **ball** - This is where the jump sounds are stored. When bouncing off a block, the game selects a random sound from this directory. There can be an infinite number of them.
    - **game** - Two sounds are reserved. Game music (music.wav) and game start (start.wav). Other names will not be detected.
    - **player** - Three sounds are reserved. Player takes damage (damage.wav), player die (die.wav) and player win (win.wav). Other names will not be detected.
- **textures** (Used only in pygame_gui)
    - It's recommended to use this directory to store element textures for solid structure. pygame_gui supports any directory in the theme file, but in the future all game textures will be stored here.
    - see [pygame_gui element images theming](https://pygame-gui.readthedocs.io/en/latest/theme_guide.html#theme-options-per-element).
- **theme**
    - Only one name is reserved - ui_theme.json. Other names will not be detected.
    - see [theming docs](https://github.com/VitoR-InA/PingPY/tree/main/docs/theming.md) for more info.