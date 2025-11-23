import ctypes
import time
import webbrowser
import pygetwindow as gw
import pyautogui
import threading
import os
import json
import pkg_resources  # Ensures pkg_resources is bundled for infi.systray when frozen
from ctypes import wintypes
from infi.systray import SysTrayIcon

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()  # Screen dimensions
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "center_windows_config.json")

# Global Variables
running = True  # Controls the main loop execution
quit_event = threading.Event()  # Signals application exit

DEFAULT_IGNORE_TITLES = [  # Built-in window titles to ignore
    "Task Switching",
    "PopupHost",
    "Start",
    "Search",
    "Cortana",
    "Task Manager",
    "Notification Center",
    "Volume Mixer",
    "LockApp",
    "Windows Shell Experience Host",
    "On-Screen Keyboard",
    "System tray overflow window.",
]

ignore_list = list(DEFAULT_IGNORE_TITLES)

hover_text = "Center-Windows"  # Text displayed when hovering over the system tray icon

respect_taskbar = True


def load_config():
  global respect_taskbar, ignore_list
  try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
      data = json.load(f)

    value = data.get("respect_taskbar")
    if isinstance(value, bool):
      respect_taskbar = value

    extra_titles = data.get("extra_ignore_titles")
    if isinstance(extra_titles, list):
      for title in extra_titles:
        if isinstance(title, str) and title not in ignore_list:
          ignore_list.append(title)
  except Exception:
    pass


def save_config():
  try:
    data = {}
    try:
      with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f) or {}
    except Exception:
      data = {}

    data["respect_taskbar"] = respect_taskbar

    extra_titles = [
      title for title in ignore_list
      if title not in DEFAULT_IGNORE_TITLES
    ]
    data["extra_ignore_titles"] = extra_titles

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2)
  except Exception:
    pass

user32 = ctypes.windll.user32
MONITOR_DEFAULTTONEAREST = 2

EVENT_OBJECT_SHOW = 0x8002
WINEVENT_OUTOFCONTEXT = 0x0000
OBJID_WINDOW = 0

WinEventProcType = ctypes.WINFUNCTYPE(
  None,
  ctypes.c_void_p,
  ctypes.c_uint,
  ctypes.c_void_p,
  ctypes.c_long,
  ctypes.c_long,
  ctypes.c_uint,
  ctypes.c_uint,
)

win_event_proc = None

user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = ctypes.c_int
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = ctypes.c_bool
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = ctypes.c_long


class RECT(ctypes.Structure):
  _fields_ = [
    ("left", ctypes.c_long),
    ("top", ctypes.c_long),
    ("right", ctypes.c_long),
    ("bottom", ctypes.c_long),
  ]


class MONITORINFO(ctypes.Structure):
  _fields_ = [
    ("cbSize", ctypes.c_ulong),
    ("rcMonitor", RECT),
    ("rcWork", RECT),
    ("dwFlags", ctypes.c_ulong),
  ]


def get_monitor_work_area(hwnd):
  monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
  if not monitor:
    return 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT

  mi = MONITORINFO()
  mi.cbSize = ctypes.sizeof(MONITORINFO)
  if not user32.GetMonitorInfoW(monitor, ctypes.byref(mi)):
    return 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT

  if respect_taskbar:
    area = mi.rcWork
  else:
    area = mi.rcMonitor

  left = area.left
  top = area.top
  width = area.right - area.left
  height = area.bottom - area.top
  return left, top, width, height


def handle_win_event(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
  global existing_hwnds
  if not hwnd:
    return
  if idObject != OBJID_WINDOW:
    return
  try:
    hwnd_int = ctypes.c_void_p(hwnd).value
    if hwnd_int in existing_hwnds:
      return
    window_title = get_window_title_from_hwnd(hwnd_int)
    if not window_title or window_title in ignore_list:
      existing_hwnds.add(hwnd_int)
      return
    print(window_title)
    target_window = None
    for w in gw.getAllWindows():
      if w._hWnd == hwnd_int:
        target_window = w
        break
    if target_window is None:
      existing_hwnds.add(hwnd_int)
      return
    if not target_window.isMaximized:
      center_window(target_window)
    existing_hwnds.add(hwnd_int)
  except Exception as e:
    try:
      print(f"Error centering window from event: {e}")
    except Exception:
      pass


def window_event_loop():
  global win_event_proc
  WinEventProc = WinEventProcType(handle_win_event)
  win_event_proc = WinEventProc
  hook = user32.SetWinEventHook(EVENT_OBJECT_SHOW, EVENT_OBJECT_SHOW, 0, WinEventProc, 0, 0, WINEVENT_OUTOFCONTEXT)
  if not hook:
    return
  msg = wintypes.MSG()
  while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))


def get_window_title_from_hwnd(hwnd):
  """
  Retrieves the title of the window associated with a given window handle (HWND).

  Parameters:
  hwnd (int): The window handle (HWND) for which to retrieve the window title.

  Returns:
  str: The title of the window associated with the given HWND. 
        Returns "Unknown Title" if an error occurs during the retrieval process.

  Raises:
  Exception: Any exception encountered during the retrieval process will be caught,
             logged, and result in returning "Unknown Title".
  """
  try:
    # Get the window title
    window_title = ctypes.create_string_buffer(512)
    ctypes.windll.user32.GetWindowTextA(hwnd, window_title, len(window_title))
    
    title_string = window_title.value.decode()
    return title_string
  except Exception as e:
    print(f"Error getting window title for HWND {hwnd}: {e}")
    return "Unknown Title"

def center_window(window):
  """
  Centers a given window on the screen if it's not maximized.
  
  Parameters:
  - window: The window object to be centered. This should be an instance of a class that has attributes like `size` and methods like `moveTo`.
  
  This function calculates the new position for the window so that it is centered on the screen,
  taking into account both the screen dimensions and the window's own dimensions.
  """
  # Check if the window is maximized
  if window.isMaximized:
      return  # Do not center the window if it's maximized

  window_width = 0
  window_height = 0
  start_time = time.time()

  while time.time() - start_time < 0.5:
      try:
          for w in gw.getAllWindows():
              if w._hWnd == window._hWnd:
                  window = w
                  break
          window_width, window_height = window.size
          if window_width > 0 and window_height > 0:
              break
      except Exception:
          break
      time.sleep(0.05)

  if window_width <= 0 or window_height <= 0:
      return

  if window.isMaximized:
      return

  monitor_left, monitor_top, monitor_width, monitor_height = get_monitor_work_area(window._hWnd)

  # Calculate the new x and y coordinates for the top-left corner of the window
  new_x = monitor_left + (monitor_width - window_width) // 2
  new_y = monitor_top + (monitor_height - window_height) // 2

  # Move the window to the calculated position
  window.moveTo(new_x, new_y)

def on_quit_callback(sysTrayIcon):
  """
  Stops the application by setting the global running flag to False and signaling the main thread to exit.

  This function is typically called when the user interacts with the system tray icon to close the application.

  Parameters:
  sysTrayIcon: The system tray icon object associated with the application. This parameter might be used
                in future implementations to perform cleanup actions related to the system tray icon.

  Side Effects:
  - Sets the global variable `running` to False, indicating that the application's main loop should terminate.
  - Calls `set()` on the `quit_event` threading event, signaling any waiting threads (likely including the main thread)
    that they should proceed with termination.
  """
  global running
  running = False  # Stop the loop
  quit_event.set()  # Signal the main thread to exit

def open_github(sysTrayIcon=None):
    """
    Opens the Github repository URL.
    """
    webbrowser.open("https://github.com/Basiiii/Center-Windows")

def open_donation(sysTrayIcon=None):
    """
    Opens the PayPal donation URL.
    """
    webbrowser.open("https://www.paypal.com/paypalme/basigraphics")

def enable_respect_taskbar(sysTrayIcon=None):
  global respect_taskbar
  respect_taskbar = True
  save_config()
  if sysTrayIcon is not None:
    sysTrayIcon.hover_text = "Center-Windows (work area)"
    try:
      sysTrayIcon._refresh_icon()
    except Exception:
      pass

def disable_respect_taskbar(sysTrayIcon=None):
  global respect_taskbar
  respect_taskbar = False
  save_config()
  if sysTrayIcon is not None:
    sysTrayIcon.hover_text = "Center-Windows (full monitor)"
    try:
      sysTrayIcon._refresh_icon()
    except Exception:
      pass

def initialize_sys_tray_and_monitoring():
  """
  Initializes the system tray icon and starts the window monitoring loop in a separate thread.
  
  Waits for the application to be signaled to quit via the quit_event.
  """
  global existing_hwnds, quit_event
  
  load_config()

  # Initialize a set to keep track of existing window handles (HWNDs)
  existing_hwnds = set([w._hWnd for w in gw.getAllWindows()])
  
  # Create and configure the system tray icon
  if respect_taskbar:
    current_hover = "Center-Windows (work area)"
  else:
    current_hover = "Center-Windows (full monitor)"

  centering_menu = (
                    ('Center within work area (respect taskbar)', None, enable_respect_taskbar),
                    ('Center on full monitor (ignore taskbar)', None, disable_respect_taskbar))

  menu_options = (
                  ('Centering mode', None, centering_menu),
                  ('Github Repo', None, open_github),
                  ('Donate', None, open_donation))
  sysTrayIcon = SysTrayIcon("icon.ico", current_hover, menu_options=menu_options, on_quit=on_quit_callback, default_menu_index=1)
  
  # Start the event-driven window monitoring loop in a separate thread
  loop_thread = threading.Thread(target=window_event_loop)
  loop_thread.daemon = True
  loop_thread.start()
  
  # Start the system tray icon
  tray_thread = threading.Thread(target=sysTrayIcon.start)
  tray_thread.daemon = True
  tray_thread.start()
  

if __name__ == "__main__":
  try:
    initialize_sys_tray_and_monitoring()
    while not quit_event.is_set():
      time.sleep(0.1)
  except KeyboardInterrupt:
    running = False
    quit_event.set()
