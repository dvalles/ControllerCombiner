We've all been there.. you've got 5 people who want to game it up, but it's a 4 person game. You think to yourself.. I wish I could combine controls with my friend and we could act as one virtual controller. Then we could all game. Then all would be right in the world.

But you can't combine controls, you can't all game, you can't have fun... until now!

Setup:

I'm not going to go that into it before people are even using the thing, but basically -

Install latest stable python version

Install Vigembus, which creates a virtual controller

Install HidHide, which hides physical controllers

Download this repo, create a shortcut for the start.bat file

Setup an environment variable called HID_HIDE that points to the folder HidHideClient.exe is in

How To:

Currently have tested with xbox one, ds4, and dualsense (ps5). Maybe it works with others, maybe not

There's a little gui that allows you to set timeframe and framerate -

timeframe - the time window in which if all n physical controllers press the button, the virtual button is pressed
framerate - the rate at which the virtual controller checks for updates. if you set this higher than the framerate of the
            game, the game will miss controller events. Just set it to fps/2 for some nyquist action