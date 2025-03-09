Theme Guide
===========
In PingPY theme files are used for the game as well.

Rule for assigning object_id to an element
------------------------------------------
- The first in ID is the container where the element is stored.  
There are 4 containers in the game:
    - self.main_container - main menu / title screen container
    - self.preparation_container - before game starts menu
    - self.shop_container - player upgrades menu
    - self.end_container - "Game over" label container
- The second in ID is the class_id of the element if there are multiple and / or the object_id of the element.
- And the last thing in ID is the *optional* subelement object_id.

Besides this pygame_gui also has global element ids for every element. It has no prefix and you can also use this for theming. E.g. "button", "panel", "label" ([pygame_gui object IDs - in depth](https://pygame-gui.readthedocs.io/en/latest/theme_guide.html#object-ids-in-depth)).

Structure:
```
prep.#size_slider.#label
  ↑       ↑          ↑
 element  |          |
container |          |
          |          |
      element id     |
                     |
                subelement id
```

> Note: "game" is global element container, for now only two elements using it - background panel (game.@background_panel) and back button (game.@back_button). **"game" element container only uses in case when there is an element, which contains in the most of containers**

Game elements
-------------
- **Main container**
    - **background panel**  
    class_id = "game.@background_panel"  
    object_id = "main.#background_panel"
    - **main label | game label**  
    object_id = "main.#label"
    - **volume slider**  
    class_id = "main.@slider"  
    object_id = "main.#volume_slider"
    - **volume slider label**  
    class_id = "main.@slider.#label"  
    object_id = "main.#volume_slider.#label"
    - **play button**  
    class_id = "main.@button"  
    object_id = "main.#play_button"
    - **shop button**  
    class_id = "main.@button"  
    object_id = "main.#shop_button"
    - **exit button**  
    class_id = "main.@button"  
    object_id = "main.#exit_button"
- **Preparation container (prep)**
    - **background panel**  
    class_id = "game.@background_panel"  
    object_id = "prep.#background_panel"
    - **back button**  
    class_id = "game.@back_button"  
    object_id = "prep.#back_button"
    - **size slider**  
    class_id = "prep.@slider"  
    object_id = "prep.#size_slider"
    - **size slider label**  
    class_id = "prep.@slider.#label"  
    object_id = "prep.#size_slider.#label"
    - **start button**  
    class_id = "prep.@button"  
    object_id = "prep.#start_button"
- **Shop container**
    - **background panel**  
    class_id = "game.@background_panel"  
    object_id = "shop.#background_panel"
    - **shop label**  
    object_id = "shop.#label"
    - **score panel**  
    object_id = "shop.#score_panel"
    - **score panel label**  
    object_id = "shop.#score_panel.#label"
    - **back button**  
    class_id = "game.@back_button"  
    object_id = "shop.#back_button"
- **End container**
    - **background panel**  
    class_id = "game.@background_panel"  
    object_id = "end.#background_panel"


> see [pygame_gui theme options per element](https://pygame-gui.readthedocs.io/en/latest/theme_guide.html#theme-options-per-element) for more info about theming any other element