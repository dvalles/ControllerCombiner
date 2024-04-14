import sys
import pygame
import vgamepad as vg
import time
import argparse
import input_combiners as ic
import virtual_controller as vc
import gui
import printers

#----- MAIN ------

# Create the parser
parser = argparse.ArgumentParser(description="Combines 2 controllers into a single virtual one")
parser.add_argument('--xbox', action='store_true', help='Makes the virtual controller an xbox 360, instead of a DS4')
args = parser.parse_args()

# Initialize Pygame for controller input
pygame.init()
pygame.joystick.init()

# Check for connected joysticks
num_controllers = pygame.joystick.get_count()
if num_controllers == 0:
    print("No physical controllers detected.")
    pygame.quit()
    exit()

# Initialize all connected joysticks
controllers = [pygame.joystick.Joystick(i) for i in range(num_controllers)]
for controller in controllers:
    controller.init()
    print(controller.get_name())

# Initialize input combiner and virtual controller
ic.initialize(controllers)
vc.initialize(args.xbox)

#run the gui, wait a sec for initialization on other thread
gui.start()
time.sleep(.1)

# Main loop
running = True
while running:
    #gui has stopped
    if gui.has_stopped():
        break

    #run pygame to update physical controllers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #get gui values
    params = gui.get_values()

    #combine physical into unified virtual
    combined = ic.get_combined_controllers(controllers, params.timeframe)

    #reset then set
    vc.reset()
    vc.update(combined)

    #small delay
    time.sleep(1/params.framerate)

# Cleanup
pygame.quit()
sys.exit()
