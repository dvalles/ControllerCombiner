import data
import vgamepad as vg
import time
import configs

"""
Handles combining the inputs of however many physical controllers connected
"""

# last time button pressed (joystick, button) -> timestamp
physical_button_to_timestamp = {}
# should reset button timestamps? button -> bool
should_reset = {}

#holds data on which buttons are pressed/how much they're pressed
class CombinedController:
    def __init__(self):
        self.analogs = (0,0,0,0)
        self.triggers = (0,0)
        self.buttons = {button: False for button in data.vg_buttons_xbox}

#Combine controllers into one representation, return that representation
def get_combined_controllers(controllers, button_press_timeframe, use_config, consensus_at):
    cc = CombinedController()
    cc.analogs = _handle_analog_sticks(controllers)
    cc.triggers = _handle_trigger_buttons(controllers)
    cc.buttons = _handle_buttons(controllers, button_press_timeframe, use_config, consensus_at)
    return cc

#Initializes the necessary state
def initialize(controllers):
    #initialize timestamp dict
    for controller in controllers:
        for button in data.vg_buttons_xbox:
            physical_button_to_timestamp[(controller, button)] = 0
    #initialize should reset
    for button in data.vg_buttons_xbox:
        should_reset[button] = False

#Handles the left and right trigger buttons
def _handle_trigger_buttons(controllers):
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

    return (lt_avg, rt_avg)

#Handles the left and right analog sticks
def _handle_analog_sticks(controllers):
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

    return (lx_avg, ly_avg, rx_avg, ry_avg)

#handles the buttons
def _handle_buttons(controllers, press_timeframe, use_config, consensus_at):
    result = {}

    #for each virtual button check if physical counterpart is 'pressed' in that all physical controllers are pressing
    for virtual_button in data.vg_buttons_xbox:
        all_pressed = _check_button(controllers, virtual_button, press_timeframe, use_config, consensus_at)
        result[virtual_button] = all_pressed

    return result

#checks if a button is pressed across all controllers
def _check_button(controllers, virtual_button, press_timeframe, use_config, consensus_at):
    timestamps = []
    anyone_pressing = False
    all_pressing = True
    num_pressed = 0
    for controller in controllers:
        #get pressed
        if "Xbox" in controller.get_name():
            pressed = _is_pressed_xbox(controller, virtual_button)
            #config mapping
            if use_config and virtual_button in configs.temoor_rocket_league:
                vb_configged = configs.temoor_rocket_league[virtual_button]
                pressed |= _is_pressed_xbox(controller, vb_configged)
        else:
            pressed = _is_pressed_playstation(controller, virtual_button)

        #set state
        all_pressing &= pressed
        anyone_pressing |= pressed
        num_pressed += pressed

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
    if should_reset[virtual_button] and not anyone_pressing:
        should_reset[virtual_button] = False

    #check if within time interval
    within = False
    if len(timestamps) >= min(consensus_at, len(controllers)):
        within = _within_timeframe(timestamps, press_timeframe)
    
    #clear timestamp and set button pressed
    if within:
        all_pressing = True
        _clear_timestamps(controllers, virtual_button)
    
    #enough have pressed to be considered pressed
    if num_pressed >= consensus_at:
        all_pressing = True

    #it's been pressed, reset until everyone releases button
    if all_pressing:
        should_reset[virtual_button] = True
    
    return all_pressing


#gets if a button is down assuming a playstation controller (ds4, dualsense)
def _is_pressed_playstation(controller, physical_button):
    correct_index = data.button_to_ps4_index[physical_button]
    return controller.get_button(correct_index)

#gets if a button is down assuming an xbox one
def _is_pressed_xbox(controller, physical_button):
    #d-pad is special case
    if physical_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT:
        return controller.get_hat(0)[0] == -1
    if physical_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT:
        return controller.get_hat(0)[0] == 1
    if physical_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP:
        return controller.get_hat(0)[1] == 1
    if physical_button == vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN:
        return controller.get_hat(0)[1] == -1
    #otherwise just button
    correct_index = data.button_to_xbox_index[physical_button]
    return controller.get_button(correct_index)

#checks timestamps are within time frame of eachother
def _within_timeframe(timestamps, press_timeframe):
    max_value = max(timestamps)
    min_value = min(timestamps)
    return (max_value - min_value) < press_timeframe

def _clear_timestamps(controllers, button):
    for controller in controllers:
        physical_button_to_timestamp[(controller, button)] = 0