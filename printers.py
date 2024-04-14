"""
Some prints that might be useful
"""

#prints the hat values of a physical xbox controller
def PrintHats(controllers):
    for controller in controllers:
        if "Xbox" in controller.get_name():
            print(controller.get_hat(0))

#prints the button index when they're pressed and denotes the physical controller type
def PrintButtons(controllers):
    for controller in controllers:
        for i in range(16):
            held = controller.get_button(i)
            if held:
                print(f"{controller.get_name()} {i}")