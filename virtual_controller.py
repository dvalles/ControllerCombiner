import data
import vgamepad as vg

"""
Handles setting the virtual controller buttons
"""

#intializes the state of the module
def Initialize(virtual_is_xbox):
    #controller type
    global is_ds4
    is_ds4 = not virtual_is_xbox

    # Create a virtual Xbox 360 or ds4 gamepad
    global virtual_gamepad
    if not is_ds4:
        virtual_gamepad = vg.VX360Gamepad()
    else:
        virtual_gamepad = vg.VDS4Gamepad()

#reset necessary state of virtual controller
def Reset():
    virtual_gamepad.reset()
    # if is_ds4:
    #     #because it uses a none enum to turn off they're all tied and I can't handle them individually, reset before frame
    #     virtual_gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE) 

#update state of virtual controller with a combined controller
def Update(combined_controller):
    triggers = combined_controller.triggers
    virtual_gamepad.left_trigger_float(value_float=triggers[0])
    virtual_gamepad.right_trigger_float(value_float=triggers[1])

    analogs = combined_controller.analogs
    #need to flip vertical components for xbox 360
    if is_ds4:
        flip = 1
    else:
        flip = -1

    # Set the averaged values to the virtual gamepad
    virtual_gamepad.left_joystick_float(x_value_float=analogs[0], y_value_float=flip*analogs[1])
    virtual_gamepad.right_joystick_float(x_value_float=analogs[2], y_value_float=flip*analogs[3])

    #set virtual controller accordingly
    buttons = combined_controller.buttons
    for virtual_button, is_pressed in buttons.items():
        if is_ds4:
            virtual_button = data.xbox_to_ds4_vigembus[virtual_button]
            _setDS4VirtualButton(virtual_gamepad, virtual_button, is_pressed)
        else:
            _setXboxVirtualButton(virtual_gamepad, virtual_button, is_pressed)
    
    #update vigembus
    virtual_gamepad.update()

#sets a xbox virtual controller button
def _setXboxVirtualButton(virtual_gamepad, virtual_button, pressed):
    _setButton(virtual_gamepad, virtual_button, pressed)

#sets a ds4 virtual controller button
def _setDS4VirtualButton(virtual_gamepad, virtual_button, pressed):
    if virtual_button == vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS: 
        _setSpecialButton(virtual_gamepad, virtual_button, pressed)
    elif virtual_button in data.ds4_special_buttons:
        _setDPadButton(virtual_gamepad, virtual_button, pressed)
    else:
        _setButton(virtual_gamepad, virtual_button, pressed)

#wrapper for press/release
def _setButton(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.press_button(vigemButton)
    else:
        gamepad.release_button(vigemButton)

def _setSpecialButton(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.press_special_button(vigemButton)
    else:
        gamepad.release_special_button(vigemButton)

def _setDPadButton(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.directional_pad(vigemButton)