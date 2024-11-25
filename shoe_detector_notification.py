import customtkinter as ctk

notification_window = None  # Global reference to the notification window

def show_notification(duration=2.0):
    """
    Display a notification window styled like a Steam notification,
    with an animation coming from just above the taskbar.

    Args:
        duration (float): Duration (in seconds) for which the notification should be visible.
    """
    global notification_window

    # Ensure duration is a valid number
    if not isinstance(duration, (int, float)):
        raise ValueError("Duration must be a number (int or float).")

    # Destroy any existing notification window
    if notification_window is not None and notification_window.winfo_exists():
        notification_window.destroy()

    # Create a new notification window using CTk
    notification_window = ctk.CTkToplevel()
    notification_window.overrideredirect(1)  # Make the window borderless
    notification_window.attributes("-topmost", 1)  # Ensure the window is in front of all others

    # Get screen dimensions
    screen_width = notification_window.winfo_screenwidth()
    screen_height = notification_window.winfo_screenheight()

    # Set window geometry
    window_width = 150
    window_height = 50
    x_position = screen_width - window_width - 10  # Adjust for a 10-pixel margin from the right
    y_position = screen_height  # Start off-screen

    notification_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Add a frame for background color
    frame = ctk.CTkFrame(notification_window,
                         width=window_width,
                         height=window_height,
                         corner_radius=0,  # Rounded corners
                         fg_color="#2a2d36")  # Dark background
    frame.pack(fill="both", expand=True)

    # Add a label for the notification text
    label = ctk.CTkLabel(frame,
                         text="Shoe Detected",  # The message displayed
                         font=("Helvetica", 12, "bold"),  # Font style
                         fg_color="transparent",
                         text_color="#FFFFFF")  # White text
    label.place(relx=0.5, rely=0.5, anchor="center")  # Center the label

    # Animate the window to slide up
    animate_notification_window(y_position - window_height, x_position, window_width, window_height)

    # Schedule the notification window to close after the duration
    notification_window.after(int(duration * 1000), close_notification_window)


def animate_notification_window(target_y, x_position, window_width, window_height):
    """
    Animate the notification window to slide from just above the taskbar.

    Args:
        target_y (int): The target y-coordinate to slide the window to.
    """
    global notification_window
    if notification_window is None or not notification_window.winfo_exists():
        return  # Exit if the window no longer exists

    current_y = notification_window.winfo_y()
    if current_y > target_y:
        # Move the window upwards
        notification_window.geometry(f"{window_width}x{window_height}+{x_position}+{current_y - 5}")
        # Call the animate function again to create a smooth animation
        notification_window.after(10, animate_notification_window, target_y, x_position, window_width, window_height)
    else:
        # Ensure the window reaches the target position
        notification_window.geometry(f"{window_width}x{window_height}+{x_position}+{target_y}")


def close_notification_window():
    """Close the notification window."""
    global notification_window
    if notification_window is not None and notification_window.winfo_exists():
        notification_window.destroy()
        notification_window = None  # Clear the global reference
