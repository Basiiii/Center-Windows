# Center-Windows

**Center-Windows** is a lightweight background utility for Windows that automatically centers new windows on the screen. This feature is commonly found in Linux environments but is often unavailable or requires paid software on Windows. Center-Windows aims to solve this problem by providing an easy-to-use, free alternative.

Feel free to donate to me [here](https://www.paypal.com/paypalme/basigraphics):

``https://www.paypal.com/paypalme/basigraphics``

## Features

- **Automatic Window Centering**: Centers newly opened windows on the screen.
- **System Tray Icon**: Includes a system tray icon for easy control and status indication.

## Installation

### Option 1: Installer

You can download the precompiled installer from the [Releases](https://github.com/Basiiii/Center-Windows/releases) page.

1. **Download Installer**:

   - Navigate to the [Releases](https://github.com/Basiiii/Center-Windows/releases) page.
   - Download the latest `Center-Windows-Setup.exe` installer.
2. **Install the Application**:

   - Double-click on the installer file (`Center-Windows-Setup.exe`).
   - Follow the on-screen instructions to complete the installation.
3. **Run the Application**:

   - Once installed, you can run the application from the Start menu or desktop shortcut.

### Option 2: Manual Compilation (Advanced)

1. **Clone the Repository**:

```sh
  git clone https://github.com/Basiiii/Center-Windows.git
  cd Center-Windows
```

2. **Create a Virtual Environment** (optional but recommended):

```sh
  python -m venv venv
```

3. **Activate the Virtual Environment**:

```cmd
  venv\Scripts\activate
```

4. **Install Dependencies**:

   ```sh
   pip install -r requirements.txt
   ```
5. **Run the Application**:

   - To run in your terminal:

     ```sh
     python Center-Windows.py
     ```
   - To compile and create an executable (allows running in the background without a terminal):

     ```sh
     python setup.py py2exe
     ```

     This will create an executable in the `dist` directory.

## Usage

Once the application is running, it will automatically monitor for new windows and center them on the screen. The application runs silently in the background and can be controlled via the system tray icon.

### System Tray Icon

- **Hover Text**: Displays "Center-Windows" when you hover over the icon.
- **Quit**: Right-click the system tray icon and select "Quit" to exit the application.

## How It Works

### Main Components

1. **Window Monitoring**: Continuously checks for new windows and centers them if they are not in the ignore list.
2. **System Tray Icon**: Provides an interface for users to interact with the application.

### Key Functions

- `get_process_name_from_hwnd(hwnd)`: Retrieves the name of the process associated with a given window handle.
- `get_window_title_from_hwnd(hwnd)`: Retrieves the title of the window associated with a given window handle.
- `center_window(window)`: Centers a given window on the screen.
- `on_quit_callback(sysTrayIcon)`: Stops the application and exits the monitoring loop.
- `monitor_windows()`: Main loop for monitoring and centering windows.
- `initialize_sys_tray_and_monitoring()`: Initializes the system tray icon and starts the window monitoring loop.

## License

This project is licensed under the GPL-3.0 License. See the `LICENSE` file for more details.

## Acknowledgments

- [pygetwindow](https://pypi.org/project/PyGetWindow/)
- [psutil](https://pypi.org/project/psutil/)
- [pyautogui](https://pypi.org/project/PyAutoGUI/)
- [infi.systray](https://pypi.org/project/infi.systray/)
