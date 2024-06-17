import time
import pygetwindow as gw
import pyautogui

# Get the size of the screen
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

def center_window(window):
  """
  Centers a given window on the screen.

  Parameters:
  - window: The window object to be centered. This should be an instance of a class that has attributes like `size` and methods like `moveTo`.

  This function calculates the new position for the window so that it is centered on the screen,
  taking into account both the screen dimensions and the window's own dimensions.
  """
  # Retrieve the width and height of the window
  window_width, window_height = window.size
  
  # Calculate the new x and y coordinates for the top-left corner of the window
  new_x = (SCREEN_WIDTH - window_width) // 2
  new_y = (SCREEN_HEIGHT - window_height) // 2
  
  # Move the window to the calculated position
  window.moveTo(new_x, new_y)

def main():
  """
  Continuously monitors for new windows opening on the screen and centers them.
  
  This script uses the `pygetwindow` library to get a list of all currently open windows and checks for new ones appearing.
  When a new window is detected, it attempts to center the window on the screen using the `center_window` function.
  """
  # Initialize a set to keep track of existing window handles (HWNDs)
  existing_hwnds = set([w._hWnd for w in gw.getAllWindows()])
  
  while True:
    # Sleep for a short period to reduce CPU usage
    time.sleep(0.1)
    
    # Update the list of current windows
    current_windows = gw.getAllWindows()
    
    # Iterate through the current windows
    for window in current_windows:
      # Check if the window's handle is not in the set of existing HWNDs
      if window._hWnd not in existing_hwnds:
        try:
          # Attempt to center the new window
          center_window(window)
        except Exception as e:
          # Print an error message if an exception occurs
          print(f"Error centering window '{window.title}': {e}")
        
        # Add the new window's handle to the set of existing HWNDs
        existing_hwnds.add(window._hWnd)

if __name__ == "__main__":
  # Execute the main function
  main()
