import pygame
import vgamepad as vg
import time
import argparse
import printers
import input_combiners as ic
import virtual_controller as vc

#----- MAIN ------

# Create the parser
parser = argparse.ArgumentParser(description="Combines 2 controllers into a single virtual one")
parser.add_argument('--xbox', action='store_true', help='Makes the virtual controller an xbox 360, instead of a DS4')
parser.add_argument('--framerate', type=float, default=60, help='Set the update framerate')
parser.add_argument('--timeframe', type=float, default=.5, help='Set the time interval for checking button presses')
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
ic.Initialize(controllers, args.xbox, args.timeframe)
vc.Initialize(args.xbox)

sleep_time = 1/args.framerate

# Main loop
running = True
while running:
    #run pygame to update physical controllers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #combine physical into unified virtual
    combined = ic.GetCombinedControllers(controllers, args.timeframe)

    #reset then set
    vc.Reset()
    vc.Update(combined)

    #small delay
    time.sleep(sleep_time)

# Cleanup
pygame.quit()
