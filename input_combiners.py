import data
import vgamepad as vg
import time
import virtual_controller

"""
Handles combining the inputs of multiple controllers
"""

# last time button pressed (joystick, button) -> timestamp
physical_button_to_timestamp = {}
# should reset button timestamps? button -> bool
should_reset = {}
# is virtual gamepad a ds4?
virtual_is_ds4 = False
# timeframe within which pressing both buttons will consider a virtual button pressed
press_timeframe = 0

#Initializes the necessary state
def Initialize(controllers, is_xbox, timeframe):
    global virtual_is_ds4, press_timeframe

    #initialize timestamp dict
    for controller in controllers:
        for button in data.vg_buttons_xbox:
            physical_button_to_timestamp[(controller, button)] = 0
    #initialize should reset
    for button in data.vg_buttons_xbox:
        should_reset[button] = False
    #set ds4
    virtual_is_ds4 = not is_xbox
    #set timeframe
    press_timeframe = timeframe

#Handles the left and right trigger buttons
def HandleTriggerButtons(controllers, virtual_gamepad):
    num_controllers = len(controllers)
    lt_sum = 0
    rt_sum = 0

    for controller in controllers:
        lt_sum += controller.get_axis(4)
        rt_sum += controller.get_axis(5)
    
    lt_avg = lt_sum / num_controllers
    rt_avg = rt_sum / num_controllers
    lt_avg = lt_avg*.5 + .5 #remap from [-1,1] to [0,1]
    rt_avg = rt_avg*.5 + .5

    # Set the averaged values to the virtual gamepad
    virtual_gamepad.left_trigger_float(value_float=lt_avg)
    virtual_gamepad.right_trigger_float(value_float=rt_avg)

#Handles the left and right analog sticks
def HandleAnalogSticks(controllers, virtual_gamepad):
    num_controllers = len(controllers)
    lx_sum = 0
    ly_sum = 0
    rx_sum = 0
    ry_sum = 0

    for controller in controllers:
        lx_sum += controller.get_axis(0)
        ly_sum += controller.get_axis(1)
        rx_sum += controller.get_axis(2)
        ry_sum += controller.get_axis(3)

    # Compute the simple average
    lx_avg = lx_sum / num_controllers
    ly_avg = ly_sum / num_controllers
    rx_avg = rx_sum / num_controllers
    ry_avg = ry_sum / num_controllers

    #need to flip vertical components for xbox 360
    if virtual_is_ds4:
        flip = 1
    else:
        flip = -1

    # Set the averaged values to the virtual gamepad
    virtual_gamepad.left_joystick_float(x_value_float=lx_avg, y_value_float=flip*ly_avg)
    virtual_gamepad.right_joystick_float(x_value_float=rx_avg, y_value_float=flip*ry_avg)

#gets if a button is down assuming a ds4
def IsPressedDS4(controller, virtual_button):
    correct_index = data.button_to_ps4_index[virtual_button]
    return controller.get_button(correct_index)

#gets if a button is down assuming an xbox one
def IsPressedXbox(controller, virtual_button):
    #d-pad is special case
    if virtual_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT:
        return controller.get_hat(0)[0] == -1
    if virtual_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT:
        return controller.get_hat(0)[0] == 1
    if virtual_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP:
        return controller.get_hat(0)[1] == 1
    if virtual_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN:
        return controller.get_hat(0)[1] == -1
    #otherwise just button
    correct_index = data.button_to_xbox_index[virtual_button]
    return controller.get_button(correct_index)

#checks timestamps are within time frame of eachother
def WithinTimeframe(timestamps):
    max_value = max(timestamps)
    min_value = min(timestamps)
    return (max_value - min_value) < press_timeframe

def ClearTimestamps(controllers, button):
    for controller in controllers:
        physical_button_to_timestamp[(controller, button)] = 0

#handles the buttons
def HandleButtons(controllers, virtual_gamepad):
    #cleanup from last frame
    if virtual_is_ds4:
        #because it uses a none enum to turn off they're all tied and I can't handle them individually, reset before frame
        virtual_gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE) 

    #for each virtual button check if physical counterpart is 'pressed' in that all physical controllers are pressing
    for virtual_button in data.vg_buttons_xbox:
        timestamps = []
        anyonePressing = False
        allPressing = True
        for controller in controllers:
            #get pressed
            if "PS4" in controller.get_name():
                pressed = IsPressedDS4(controller, virtual_button)
            elif "Xbox" in controller.get_name():
                pressed = IsPressedXbox(controller, virtual_button)

            #set state
            allPressing &= pressed
            anyonePressing |= pressed

            #set timestamp if needed
            if pressed:
                physical_button_to_timestamp[(controller, virtual_button)] = time.time()
            
            #reset if needed
            if should_reset[virtual_button]:
                physical_button_to_timestamp[(controller, virtual_button)] = 0

            #accumulate if not zero
            currTimestamp = physical_button_to_timestamp[(controller, virtual_button)]
            if currTimestamp != 0:
                timestamps.append(currTimestamp)
        
        #if resetting timestamps was true but no one is pressing still
        if should_reset[virtual_button] and not anyonePressing:
            should_reset[virtual_button] = False

        #check if within time interval
        within = False
        if len(timestamps) == len(controllers):
            within = WithinTimeframe(timestamps)
        
        #clear timestamp and set button pressed
        if within:
            allPressing = True
            ClearTimestamps(controllers, virtual_button)

        #it's been pressed, reset until everyone releases button
        if allPressing:
            should_reset[virtual_button] = True

        #set virtual controller accordingly
        if virtual_is_ds4:
            virtual_button = data.xbox_to_ds4_vigembus[virtual_button]
            virtual_controller.SetDS4VirtualButton(virtual_gamepad, virtual_button, allPressing)
        else:
            virtual_controller.SetXboxVirtualButton(virtual_gamepad, virtual_button, allPressing)