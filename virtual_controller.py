import data
import vgamepad as vg

"""
Handles setting the virtual controller buttons
"""

#sets a xbox virtual controller button
def SetXboxVirtualButton(virtual_gamepad, virtual_button, pressed):
    SetButton(virtual_gamepad, virtual_button, pressed)

#sets a ds4 virtual controller button
def SetDS4VirtualButton(virtual_gamepad, virtual_button, pressed):
    if virtual_button == vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS: 
        SetSpecialButton(virtual_gamepad, virtual_button, pressed)
    elif virtual_button in data.ds4_special_buttons:
        SetDPadButton(virtual_gamepad, virtual_button, pressed)
    else:
        SetButton(virtual_gamepad, virtual_button, pressed)

#wrapper for press/release
def SetButton(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.press_button(vigemButton)
    else:
        gamepad.release_button(vigemButton)

def SetSpecialButton(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.press_special_button(vigemButton)
    else:
        gamepad.release_special_button(vigemButton)

def SetDPadButton(gamepad, vigemButton, pressed):
    if pressed:
        gamepad.directional_pad(vigemButton)