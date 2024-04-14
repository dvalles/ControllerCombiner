"""
Some prints that might be useful
"""

#prints the hat values of a physical joystick
def PrintHats(joysticks):
    for joystick in joysticks:
        if "Xbox" in joystick.get_name():
            print(joystick.get_hat(0))

#prints the button index when they're pressed and denotes the controller type
def PrintButtons(joysticks):
    for joystick in joysticks:
        for i in range(16):
            held = joystick.get_button(i)
            if held:
                print(f"{joystick.get_name()} {i}")