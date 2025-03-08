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
└── themes/
    ├── breeze_dark.json
    └── breeze_ligth.json
```

Theme Guide
===========

In PingPY theme files are used for the game as well. So defaults.dark_bg is responsible for the background color of the game in all states.

```json
{
    "defaults":
    {
        "colours":
        {
            "dark_bg":"#1b1e20"
        }
    }
}
```
The code above will change game background to "1b1e20". Game theming also supports [supported colour inputs](https://pygame-gui.readthedocs.io/en/latest/theme_guide.html#id3).

> see [pygame_gui theming](https://pygame-gui.readthedocs.io/en/latest/theme_guide.html#theme-options-per-element) for more info about theming any other element