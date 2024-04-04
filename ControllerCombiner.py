import pygame
import vgamepad as vg
import time
import data
import argparse

#prints the hat values
def PrintHats(joysticks):
    for joystick in joysticks:
        if "Xbox" in joystick.get_name():
            print(joystick.get_hat(0))

#prints out the buttons for mapping
def PrintButtons(joysticks):
    for joystick in joysticks:
        for i in range(16):
            held = joystick.get_button(i)
            if held and "PS4" in joystick.get_name():
                print(f"PS4 - {i}")
            if held and "Xbox" in joystick.get_name():
                print(f"Xbox - {i}")

#gets if a button is down assuming a ds4
def IsPressedDS4(joystick, vigemButton):
    correct_index = data.button_to_ps4_index[vigemButton]
    return joystick.get_button(correct_index)

#gets if a button is down assuming an xbox one
def IsPressedXbox(joystick, vigemButton):
    #d-pad is special case
    if vigemButton == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT:
        return joystick.get_hat(0)[0] == -1
    if vigemButton == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT:
        return joystick.get_hat(0)[0] == 1
    if vigemButton == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP:
        return joystick.get_hat(0)[1] == 1
    if vigemButton == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN:
        return joystick.get_hat(0)[1] == -1
    #otherwise just button
    correct_index = data.button_to_xbox_index[vigemButton]
    return joystick.get_button(correct_index)

#sets a xbox virtual controller button
def SetXboxVirtualButton(gamepad, vigemButton, pressed):
    SetButton(gamepad, vigemButton, pressed)

#sets a ds4 virtual controller button
def SetDS4VirtualButton(gamepad, vigemButton, pressed):
    if vigemButton == vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS: 
        SetSpecialButton(gamepad, vigemButton, pressed)
    elif vigemButton in data.ds4_special_buttons:
        SetDPadButton(gamepad, vigemButton, pressed)
    else:
        SetButton(gamepad, vigemButton, pressed)

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
    # else:
        # gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)

#handles the buttons
def HandleButtons(joysticks, virtual_gamepad):
    #cleanup from last frame
    if args.ds4:
        #because it uses a none enum to turn off they're all tied and I can't handle them individually, reset before frame
        virtual_gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE) 

    #for each button check if pressed
    for button in data.vg_buttons_xbox:
        bothPressing = True
        for joystick in joysticks:
            if "PS4" in joystick.get_name():
                bothPressing &= IsPressedDS4(joystick, button)
            elif "Xbox" in joystick.get_name():
                bothPressing &= IsPressedXbox(joystick, button)

        #set virtual controller accordingly
        if args.ds4:
            button = data.xbox_to_ds4_vigembus[button]
            SetDS4VirtualButton(virtual_gamepad, button, bothPressing)
        else:
            SetXboxVirtualButton(virtual_gamepad, button, bothPressing)

#Handles the left and right trigger buttons
def HandleTriggerButtons(joysticks, virtual_gamepad):
    lt_sum = 0
    rt_sum = 0

    for joystick in joysticks:
        lt_sum += joystick.get_axis(4)
        rt_sum += joystick.get_axis(5)
    
    lt_avg = lt_sum / num_joysticks
    rt_avg = rt_sum / num_joysticks
    lt_avg = lt_avg*.5 + .5 #remap from [-1,1] to [0,1]
    rt_avg = rt_avg*.5 + .5

    # print(f"LT: {lt_avg}, RT: {rt_avg}")

    # Set the averaged values to the virtual gamepad
    virtual_gamepad.left_trigger_float(value_float=lt_avg)
    virtual_gamepad.right_trigger_float(value_float=rt_avg)

#Handles the left and right analog sticks
def HandleAnalogSticks(joysticks, virtual_gamepad):
    # Read and average analog stick positions
    lx_sum = 0
    ly_sum = 0
    rx_sum = 0
    ry_sum = 0

    for joystick in joysticks:
        # Assuming the left stick axes are 0 (X axis) and 1 (Y axis)
        # Assuming the right stick axes are 3 (X axis) and 4 (Y axis)
        # Adjust these axis numbers based on your controller
        lx_sum += joystick.get_axis(0)
        ly_sum += joystick.get_axis(1)
        rx_sum += joystick.get_axis(2)
        ry_sum += joystick.get_axis(3)

        # if "PS4" in joystick.get_name():
            # print(f"PS4 - LX: {joystick.get_axis(0)}, LY: {joystick.get_axis(1)}, RX: {joystick.get_axis(2)}, RY: {joystick.get_axis(3)}")
        # if "Xbox" in joystick.get_name():
            # print(f"Xbox - LX: {joystick.get_axis(0)}, LY: {joystick.get_axis(1)}, RX: {joystick.get_axis(2)}, RY: {joystick.get_axis(3)}")


    # Compute the simple average
    lx_avg = lx_sum / num_joysticks
    ly_avg = ly_sum / num_joysticks
    rx_avg = rx_sum / num_joysticks
    ry_avg = ry_sum / num_joysticks

    #need to flip vertical components for xbox 360
    if args.ds4:
        flip = 1
    else:
        flip = -1

    # Set the averaged values to the virtual gamepad
    virtual_gamepad.left_joystick_float(x_value_float=lx_avg, y_value_float=flip*ly_avg)
    virtual_gamepad.right_joystick_float(x_value_float=rx_avg, y_value_float=flip*ry_avg)

# Create the parser
parser = argparse.ArgumentParser(description="Combines 2 controllers into a single virtual one")
parser.add_argument('--ds4', action='store_true', help='Makes the virtual controller a DS4, instead of Xbox 360')
args = parser.parse_args()

# Initialize Pygame for controller input
pygame.init()
pygame.joystick.init()

# Check for connected joysticks
num_joysticks = pygame.joystick.get_count()
if num_joysticks == 0:
    print("No physical controllers detected.")
    pygame.quit()
    exit()

# Initialize all connected joysticks
joysticks = [pygame.joystick.Joystick(i) for i in range(num_joysticks)]
for joystick in joysticks:
    joystick.init()

#print out controller names
for joystick in joysticks:
    print(joystick.get_name())

# Create a virtual Xbox 360 gamepad
if args.ds4:
    virtual_gamepad = vg.VDS4Gamepad()
else:
    virtual_gamepad = vg.VX360Gamepad()

# Main loop
running = True
while running:
    # Event loop (necessary to process joystick events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    HandleAnalogSticks(joysticks, virtual_gamepad)
    HandleTriggerButtons(joysticks, virtual_gamepad)
    HandleButtons(joysticks, virtual_gamepad)
    # PrintButtons(joysticks)
    # PrintHats(joysticks)

    #update at end of frame
    virtual_gamepad.update()

    #small delay
    time.sleep(0.001)

# Cleanup
pygame.quit()
virtual_gamepad.reset()
virtual_gamepad.update()
