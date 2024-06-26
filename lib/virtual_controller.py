import data
import vgamepad as vg

"""
Handles setting the virtual controller buttons
"""

#intializes the state of the module
def initialize(virtual_is_xbox):
    #controller type
    global is_xbox
    is_xbox = virtual_is_xbox

    # Create a virtual Xbox 360 or ds4 gamepad
    global virtual_gamepad
    if is_xbox:
        virtual_gamepad = vg.VX360Gamepad()
    else:
        virtual_gamepad = vg.VDS4Gamepad()

#reset necessary state of virtual controller
def reset():
    virtual_gamepad.reset()
    # if is_ds4: <- I'll leave for posterity
    #     #because it uses a none enum to turn off they're all tied and I can't handle them individually, reset before frame
    #     virtual_gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE) 

#update state of virtual controller with a combined controller
def update(combined_controller):
    #triggers
    triggers = combined_controller.triggers
    _update_triggers(triggers)

    #analog sticks
    analogs = combined_controller.analogs
    _update_analog_sticks(analogs)

    #buttons
    buttons = combined_controller.buttons
    _update_buttons(buttons)
    
    #update vigembus
    virtual_gamepad.update()

#update the virtual controller triggers
def _update_triggers(triggers):
    virtual_gamepad.left_trigger_float(value_float=triggers[0])
    virtual_gamepad.right_trigger_float(value_float=triggers[1])

#update the virtual controller analog sticks
def _update_analog_sticks(analogs):
    #need to flip vertical components for xbox 360
    if is_xbox:
        flip = -1
    else:
        flip = 1

    # Set the averaged values to the virtual gamepad
    virtual_gamepad.left_joystick_float(x_value_float=analogs[0], y_value_float=flip*analogs[1])
    virtual_gamepad.right_joystick_float(x_value_float=analogs[2], y_value_float=flip*analogs[3])

#update the virtual controller buttons
def _update_buttons(buttons):
    for virtual_button, is_pressed in buttons.items():
        if is_xbox:
            _set_xbox_virtual_button(virtual_gamepad, virtual_button, is_pressed)
        else:
            virtual_button = data.xbox_to_ds4_vigembus[virtual_button]
            _set_ds4_virtual_button(virtual_gamepad, virtual_button, is_pressed)

#sets a xbox virtual controller button
def _set_xbox_virtual_button(virtual_gamepad, virtual_button, pressed):
    _set_button(virtual_gamepad, virtual_button, pressed)

#sets a ds4 virtual controller button
def _set_ds4_virtual_button(virtual_gamepad, virtual_button, pressed):
    if virtual_button == vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS: 
        _set_special_button(virtual_gamepad, virtual_button, pressed)
    elif virtual_button in data.ds4_special_buttons:
        _set_dpad_button(virtual_gamepad, virtual_button, pressed)
    else:
        _set_button(virtual_gamepad, virtual_button, pressed)

#wrapper for press/release
def _set_button(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.press_button(vigemButton)
    else:
        gamepad.release_button(vigemButton)

def _set_special_button(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.press_special_button(vigemButton)
    else:
        gamepad.release_special_button(vigemButton)

def _set_dpad_button(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.directional_pad(vigemButton)