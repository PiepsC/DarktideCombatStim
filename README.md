## Introduction

CombatStim is a small macro-like script that allows you to pull of some fancy moves in Darktide without having to break all your fingers or accept Carpal tunnel as a sacrifice.

The script is set-up in a fairly generic way, allowing people to expand upon it easily.

### Install

- Install the newest version of Python

- Either download as compressed folder or clone the directory: ``git clone https://github.com/PiepsC/DarktideCombatStim.git``

- Navigate to the source folder then install the dependencies: ``pip install -r requirements.txt``

### How to use

All the script does is emulate key presses. In order to make use of it you need to instruct the script what keys you want to map. Navigate to the 'combatstim.ini' file and adjust it according to your desires. Note that 'dodgemask' is the actual key you press, and 'dodge' is the key you would use to dodge in-game. Since these conflict you will need to rebind the dodge key in Darktide itself. For most users this will be the spacebar. It is expected to be bound to 'p' in the ini file, while still being effectively activated with spacebar when the script is run.

As I assume you probably use the same keys for every characters these sections are application wide. However, you can adjust the "length" of the dash per setup. Simply add a new section with any desired name (similar to the '[zealot]' example already present) and specify the duration of the dash. Note that if the dash falls below a certain treshold the game will not register the inputs properly.

Now that your .ini file is set up run the script: ```python Darktide_CombatStim.py YOUR_CONFIG```, where the last part is to be replaced with the profile you want to run. The provided .ini file would be run as ```python Darktide_CombatStim.py zealot``` for example.

The special controls allow you to modify the script's behavior. The chat key will pause the script (so you can actually type without being interrupted by unintended keystrokes) and the terminate key will stop the script. The prefix entry is added before any directional input. Darktide recognizes dash+directional input as a directed dash. The script works similarly.

### Demonstration

I first use the regular dash for a demonstration, then enable the script. The script adds crouch inputs at the beginning and end of the dash, reducing your hitbox size and making it easier to leverage cover.

[![CombatStim demo](https://img.youtube.com/vi/L91rHNg-6Mk/0.jpg)](https://www.youtube.com/watch?v=YsjZ9gZ2gg8)
