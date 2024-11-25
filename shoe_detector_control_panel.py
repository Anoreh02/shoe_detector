import os
import tkinter as tk
import customtkinter as ctk
import pygame
import pymongo 
from tkcalendar import Calendar
import datetime 
from PIL import Image, ImageTk

image_path = "database/images"

class ControlPanel:

    def __init__(self):

        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["shoe_detections"]  # Database name
        self.collection = self.db["detections"]  # Collection name
        
        self.ctk = ctk.CTk()  # Create a custom Tkinter root window
        self.ctk.title("Shoe Detector")
        self.ctk.geometry("900x400")
        self.ctk.minsize(900, 400)
        self.ctk.maxsize(900, 400)
        self.ctk.bind("<Configure>", self.update_dynamic_positions)  # Bind the resize event

        pygame.mixer.init()

        # Create the main menu panel
        self.menu_panel = ctk.CTkFrame(self.ctk, width=900, height=400)
        self.menu_panel.place(relx=0.5, rely=0.5, anchor='center')

        self.title_label = ctk.CTkLabel(self.menu_panel, text="Shoe Detector", font=("Arial", 70, "bold"), text_color="#6495ED")
        self.title_label.place(relx=0.5, rely=0.4, anchor='center')
        self.start_message = ctk.CTkLabel(self.menu_panel, text="Click anywhere to begin", font=("Arial", 15))
        self.start_message.place(relx=0.5, rely=0.550, anchor='center')

        # Bind the click event to start the application
        self.ctk.bind("<Button-1>", self.start_application)

        # Initialization for the control panel buttons and alarm
        self.original_buttons_visible = False
        self.original_buttons = []

        # Alarm duration variable and slider (hidden initially)
        self.alarm_duration = tk.DoubleVar(value=3)  # Default alarm duration (3 seconds)
        self.alarm_duration_label = ctk.CTkLabel(self.ctk, text="Alarm Duration")
        self.alarm_duration_slider = ctk.CTkSlider(self.ctk, from_=1, to=10, variable=self.alarm_duration, number_of_steps=9)
        self.alarm_slider_visible = False


        self.exit_flag = False
        
        # Create the original buttons
        button_params = {
            "width": 200,  # Button width
            "height": 70,  # Button height
            "font": ("Arial", 17, "bold"),  # Button font size
        }

        self.button1 = ctk.CTkButton(self.ctk, text="Notification \nSettings", command=lambda: self.settings_UI(self.button1), **button_params)
        self.button2 = ctk.CTkButton(self.ctk, text="Data Summary", command=lambda: self.summary_ui(self.button2), **button_params)
        self.button3 = ctk.CTkButton(self.ctk, text="End", command=self.exit_program, **button_params)

        # Store the buttons in the original_buttons list
        self.original_buttons = [self.button1, self.button2, self.button3]

        # Slider for popup duration (hidden initially)
        self.popup_duration = tk.DoubleVar(value=3)  # Default duration
        self.duration_label = ctk.CTkLabel(self.ctk, text="Popup Duration")
        self.duration_slider = ctk.CTkSlider(self.ctk, from_=1, to=10, variable=self.popup_duration, number_of_steps=9)
        
        self.volume_level = ctk.DoubleVar(value=0.07)  # Default volume at 100%
        
        # Flags to track slider and popup visibility
        self.slider_visible = False
        self.popup_enabled = True
        self.alarm_enabled = True

    def start_application(self, event=None):
        """Transition from the menu panel to the control panel."""
        self.menu_panel.place_forget()

        # Set the original buttons to visible
        self.original_buttons_visible = True
        self.update_dynamic_positions()  # Place buttons dynamically

        # Remove the click binding once we are in the main screen
        self.ctk.unbind("<Button-1>")

    def update_dynamic_positions(self, event=None):
        """Place buttons dynamically in the control panel."""
        width = self.ctk.winfo_width()
        height = self.ctk.winfo_height()

        # Dynamically place original buttons only if they are visible
        if self.original_buttons_visible:
            button_count = len(self.original_buttons)
            button_width = 0.15  # Button width as a fraction of the window
            spacing = (1 - button_width * button_count) / (button_count + 1)

            for i, button in enumerate(self.original_buttons):
                relx = spacing + i * (button_width + spacing)
                button.place(relx=relx, rely=0.3, relwidth=button_width, relheight=0.1)

         # Alarm duration variable and slider
        self.alarm_duration = tk.DoubleVar(value=3)  # Default alarm duration (3 seconds)
        self.alarm_duration_label = ctk.CTkLabel(self.ctk, text="Alarm Duration")
        self.alarm_duration_slider = ctk.CTkSlider(self.ctk, from_=1, to=10, variable=self.alarm_duration, number_of_steps=9)
        self.alarm_slider_visible = False

        # Original buttons using CTkButton
        self.original_buttons_visible = True

        button_params = {
            "width": 200,  # Button width
            "height": 70,  # Button height
            "font": ("Arial", 17, "bold"),  # Button font size    
        }

        self.button1 = ctk.CTkButton(self.ctk, text="Notification \nSettings", command=lambda: self.settings_UI(self.button1), **button_params)
        self.button2 = ctk.CTkButton(self.ctk, text="Data Summary", command=lambda: self.summary_ui(self.button2), **button_params)
        self.button3 = ctk.CTkButton(self.ctk, text="End", command=self.exit_program, **button_params)

        # Store original buttons in a list
        self.original_buttons = [self.button1, self.button2, self.button3]

        # Initialize slider and label (hidden initially)
        self.popup_duration = tk.DoubleVar(value=2)  # Default duration
        self.duration_label = ctk.CTkLabel(self.ctk, text="Popup Duration")
        self.duration_slider = ctk.CTkSlider(self.ctk, from_=1, to=10, variable=self.popup_duration, number_of_steps=9)

        # Flag to track slider visibility
        self.slider_visible = False
        self.popup_enabled = True
        self.alarm_enabled = True

        # Handle window close event
        self.ctk.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Place buttons dynamically
        self.update_dynamic_positions()

    def settings_UI(self, active_button):
        
        self.original_buttons_visible = False
        for button in self.original_buttons:
            button.place_forget()

        button_size = {
            "width": 100,  # Button width
            "height": 40,  # Button height
            "font": ("Arial", 20, "bold"),  # Button font size    
        }

        self.buttonAlarm = ctk.CTkButton(self.ctk, text="Alarm", command=lambda: self.toggle_alarm_slider(self.buttonAlarm), **button_size)
        self.buttonPopup = ctk.CTkButton(self.ctk, text="Popup", command=lambda: self.toggle_duration_slider(self.buttonPopup), **button_size)
        self.buttonHome = ctk.CTkLabel(self.ctk, text="← Back", font=("Arial", 17, "bold"), text_color="white", cursor="hand2")

        self.buttonHome.place(relx=0.01, rely=0.05, anchor='w')
        self.buttonAlarm.place(relx=0.3, rely=0.3, anchor='center')
        self.buttonPopup.place(relx=0.7, rely=0.3, anchor='center')

        self.buttonHome.bind("<Button-1>", lambda event: self.back_to_main())

        self.round_button2 = ctk.CTkCheckBox(self.ctk, 
                                            text="", 
                                            command=self.toggle_enable_alarm,
                                            onvalue=True, 
                                            offvalue=False, 
                                            width=25, 
                                            height=25,
                                            fg_color="#454545",
                                            hover_color="#999999")
        self.round_button2.select() if self.alarm_enabled else self.round_button2.deselect()
        self.round_button2.place(relx=0.437 - 0.34, rely=0.5, anchor='center') # Centered dynamically
        

        # Add a smaller round button for enabling/disabling the popup
        self.round_button = ctk.CTkCheckBox(self.ctk, 
                                            text="", 
                                            command=self.toggle_enable_popup, 
                                            onvalue=True, 
                                            offvalue=False, 
                                            width=25, 
                                            height=25,
                                            fg_color="#454545",
                                            hover_color="#999999")
        self.round_button.select() if self.popup_enabled else self.round_button.deselect()
        self.round_button.place(relx=0.437 - 0.04, rely=0.5, anchor='center')  # Centered dynamically

    def back_to_main(self):

        # Remove all the settings UI components
        if hasattr(self, 'buttonHome'):
            self.buttonHome.place_forget()
        if hasattr(self, 'buttonAlarm'):
            self.buttonAlarm.place_forget()
        if hasattr(self, 'buttonPopup'):
            self.buttonPopup.place_forget()
        if hasattr(self, 'round_button'):
            self.round_button.place_forget()
        if hasattr(self, 'round_button2'):
            self.round_button2.place_forget()
        if hasattr(self, 'calendar'):
            self.calendar.place_forget()
            self.select_button_calendar.place_forget() 
        if hasattr(self, 'no_data_label'):
                self.no_data_label.place_forget()

        self.original_buttons_visible = True

        # Hide the duration slider and label
        if self.slider_visible == True:
            self.duration_label.place_forget()
            self.duration_slider.place_forget()
            self.popup_duration_display.place_forget()
            self.slider_visible = False

        # Hide the alarm duration slider and label
        if self.alarm_slider_visible == True:
            self.alarm_duration_label.place_forget()
            self.alarm_duration_slider.place_forget()
            self.alarm_duration_display.place_forget()
            self.alarm_slider_visible = False
            self.volume_slider.place_forget()
            self.volume_label.place_forget()

        # Re-add the original buttons
        for button in self.original_buttons:
            button.place_forget()  # Ensure they are reset
        self.update_dynamic_positions()

    def toggle_enable_alarm(self, event=None):
        self.alarm_enabled = not self.alarm_enabled

        # Update checkbox state
        if self.alarm_enabled:
            self.round_button2.select()  # Check the box
            self.popup_duration.set(3)  # Reset to a default value if needed
            # Restore the slider if it was previously visible
            if self.alarm_slider_visible:
                self.update_dynamic_positions()
        else:
            self.round_button2.deselect()  # Uncheck the box
            self.alarm_duration.set(0)  # Set duration to 0 when popup is disabled
            # Hide the slider and label when popup is disabled
            if hasattr(self, 'alarm_duration_display'):
                self.alarm_duration_display.place_forget()
            self.alarm_duration_label.place_forget()
            self.alarm_duration_slider.place_forget()
            self.alarm_slider_visible = False  # Ensure the slider is not visible

    def update_alarm_duration_display(self, event=None):
        if self.alarm_enabled:
            milliseconds = self.alarm_duration.get()
            seconds = milliseconds / 10  # Convert milliseconds to seconds
            if hasattr(self, 'alarm_duration_display'):
                self.alarm_duration_display.configure(text=f"Duration: {seconds:.2f} s")
        else:
            # Hide the alarm duration display if the alarm is disabled
            if hasattr(self, 'alarm_duration_display'):
                self.alarm_duration_display.place_forget()

    def toggle_alarm_slider(self, *args):
        """Toggle the alarm duration slider visibility."""
        if self.alarm_enabled:
            if self.alarm_slider_visible:
                # Hide the slider and the display label
                self.alarm_duration_label.place_forget()
                self.alarm_duration_slider.place_forget()

                self.alarm_duration_display.place_forget()  # Hide the display label as well
                self.volume_slider.place_forget()
                self.volume_label.place_forget()
                self.alarm_slider_visible = False
            else:
                # Show the slider
                width = self.ctk.winfo_width()
                height = self.ctk.winfo_height()

                alarm_duration_width = 0.18
                alarm_duration_height = 0.56

                self.alarm_duration_label.place(x=width * alarm_duration_width - 50, y=height * alarm_duration_height)
                self.alarm_duration_slider.place(x=width * alarm_duration_width - 50, y=height * alarm_duration_height + 30)

                # Update the alarm duration display (ms and seconds)
                
                self.alarm_duration_display = ctk.CTkLabel(self.ctk, text=f"Duration: {(self.alarm_duration.get()/10):.2f} s")
                self.alarm_duration_display.place(x=width * alarm_duration_width - 50, y=height * alarm_duration_height + 60)

                # Bind the slider movement to update the label in real-time
                self.alarm_duration_slider.bind("<Motion>", self.update_alarm_duration_display)


            

                self.volume_slider = ctk.CTkSlider(
                    self.ctk,
                    from_=0,  # Mute
                    to=1,  # Maximum volume
                    variable=self.volume_level,
                )
                self.volume_slider.place(x=width * alarm_duration_width - 8, y=height * alarm_duration_height + 50)

                # Label to show volume slider value
                self.volume_label = ctk.CTkLabel(self.ctk, text=f"Volume: {self.volume_level.get() * 100:.0f}%")
                self.volume_label.place(x=width * alarm_duration_width - 4, y=height * alarm_duration_height + 80)
                self.volume_slider.bind("<Motion>", self.update_volume_label)

                self.alarm_slider_visible = True
        else:
            # Do not show the alarm slider if the alarm is disabled
            self.alarm_duration_label.place_forget()
            self.alarm_duration_slider.place_forget()
            if hasattr(self, 'alarm_duration_display'):
                self.alarm_duration_display.place_forget()
            self.alarm_slider_visible = False  # Ensure the slider is not visible

    def update_volume_label(self, event=None):
        """Update the volume label when the slider value changes."""
        current_volume = self.volume_level.get()
        self.volume_label.configure(text=f"Volume: {current_volume * 100:.0f}%")
    
    def play_alarm_sound(self, duration):
        """Play the alarm sound for the specified duration."""
        try:

            volume = self.volume_level.get()

            milliseconds = self.alarm_duration.get()
            seconds = milliseconds / 10
            
            pygame.mixer.music.load("buzz.mp3")  # Path to the MP3 file
            pygame.mixer.music.set_volume(volume)

            pygame.mixer.music.play()
            duration = seconds  # Get the duration from the slider
            self.ctk.after(int(duration * 1000), pygame.mixer.music.stop)  # Stop after the duration
        except Exception as e:
            print(f"Error playing alarm: {e}")


    def toggle_duration_slider(self, active_button):
        if not self.popup_enabled:
            return  # Do nothing if popup is disabled

        if self.slider_visible:
            self.duration_label.place_forget()
            self.duration_slider.place_forget()
            self.popup_duration_display.place_forget()
            self.slider_visible = False
        else:
            duration_label_x = self.ctk.winfo_width() * 0.488 - 50
            duration_label_y = self.ctk.winfo_height() * 0.56
            self.duration_label.place(x=duration_label_x, y=duration_label_y)

            duration_slider_x = self.ctk.winfo_width() *  0.488 - 50
            duration_slider_y = duration_label_y * 0.56 + 30
            self.duration_slider.place(x=duration_slider_x, y=duration_slider_y)

            self.popup_duration_display = ctk.CTkLabel(self.ctk, text=f"Duration: {(self.popup_duration.get()/2):.2f} s")
            self.popup_duration_display.place(x=self.ctk.winfo_width() *  0.488 + 85, y= duration_slider_y + 60)

            # Bind the slider movement to update the label in real-time
            self.duration_slider.bind("<Motion>", self.update_popup_duration_display)


            self.slider_visible = True
    
    def toggle_enable_popup(self, event=None):
        self.popup_enabled = not self.popup_enabled

        # Update checkbox state based on popup_enabled
        if self.popup_enabled:
            self.round_button.select()  # Check the box
            self.popup_duration.set(3.0)  # Reset to a default value if needed
            # Restore the slider if it was previously visible
            if self.slider_visible:
                self.update_dynamic_positions()
        else:
            self.round_button.deselect()  # Uncheck the box
            self.popup_duration.set(0)  # Set duration to 0 when popup is disabled
            # Hide the slider and label when popup is disabled
            self.duration_label.place_forget()
            self.duration_slider.place_forget()
            self.popup_duration_display.place_forget()
            self.slider_visible = False  # Ensure the slider is not visible

    def update_popup_duration_display(self, event=None):
        if self.popup_enabled:
            milliseconds = self.popup_duration.get()
            seconds = milliseconds / 2  # Convert milliseconds to seconds
            if hasattr(self, 'popup_duration_display'):
                self.popup_duration_display.configure(text=f"Duration: {seconds:.2f} s")
        else:
            # Hide the alarm duration display if the alarm is disabled
            if hasattr(self, 'popup_duration_display'):
                self.popup_duration_display.place_forget()

    def on_closing(self):
        self.ctk.destroy()

    def update_dynamic_positions(self, event=None):
    # Dynamic placement for the original buttons
        width = self.ctk.winfo_width()
        height = self.ctk.winfo_height()

        
        # Dynamically place original buttons only if they are visible
        if self.original_buttons_visible:
            button_count = len(self.original_buttons)
            button_width = 0.15  # Button width as a fraction of the window
            spacing = (1 - button_width * button_count) / (button_count + 1)

            for i, button in enumerate(self.original_buttons):
                relx = spacing + i * (button_width + spacing)
                button.place(relx=relx, rely=0.3, relwidth=button_width, relheight=0.1)
        
        # Dynamically position the alarm slider if it's visible
        if self.alarm_slider_visible:
            alarm_duration_width = 0.23
            alarm_duration_height = 0.40
            self.alarm_duration_label.place(x=width * alarm_duration_width - 50, y=height * alarm_duration_height)
            self.alarm_duration_slider.place(x=width * alarm_duration_width - 50, y=height * alarm_duration_height + 30)
            
            
            self.alarm_duration_display.place(x=width * alarm_duration_width - 50, y=height * alarm_duration_height + 60)

        
        if hasattr(self, 'round_button2') and self.round_button2.winfo_ismapped():
            self.round_button2.place(relx=0.537 - 0.34, rely=0.3, anchor='center')

        # Dynamically place round_button
        if hasattr(self, 'round_button') and self.round_button.winfo_ismapped():
            self.round_button.place(relx=0.637 - 0.04, rely=0.3, anchor='center')
        

        # Dynamically position the popup slider if it's visible
        if self.slider_visible:
            duration_label_x = width * 0.600 - 13
            duration_label_y = height * 0.40
            self.duration_label.place(x=duration_label_x, y=duration_label_y)

            duration_slider_x = width * 0.600 - 13
            duration_slider_y = duration_label_y + 30
            self.duration_slider.place(x=duration_slider_x, y=duration_slider_y)

    def summary_ui(self, active_button):
        
        if hasattr(self, 'scrollable_frame') and self.scrollable_frame:
            # Destroy the scrollable_frame and its contents
            self.scrollable_frame.pack_forget()

        if hasattr(self, 'buttonback'):
            self.buttonback.place_forget()

        self.original_buttons_visible = False
        for button in self.original_buttons:
            button.place_forget()

        self.buttonHome = ctk.CTkLabel(self.ctk, text="← Back", font=("Arial", 17, "bold"), text_color="white", cursor="hand2")
        self.buttonHome.place(relx=0.01, rely=0.05, anchor='w')
        self.buttonHome.bind("<Button-1>", lambda event: self.back_to_main())

        calendar_pos_x = 325
        calendar_pos_y = 100

        self.calendar = Calendar(self.ctk, selectmode='day',
                        font=("Arial", 12), background="lightblue", foreground="black",  
                        width=300, height=300)
        
        self.calendar.place(x= calendar_pos_x, y = calendar_pos_y)

        self.select_button_calendar = ctk.CTkButton(self.ctk, text="Select Date", command= lambda: self.on_date_selected(self.calendar.get_date()))
        self.select_button_calendar.place(x= calendar_pos_x + 85, y = calendar_pos_y - 50)

    def initialize_calendar(self):
        """Initialize and populate the calendar, highlighting dates with data."""
        today = datetime.date.today()
        current_year = today.year
        current_month = today.month
        self.calendar = Calendar(self.ctk, selectmode='day')
        # Loop through the days of the current month and check for data for each date
        for day in range(1, 32):  # Loop through all the days of the month
            try:
                selected_date = datetime.date(current_year, current_month, day)  # Create a date object for the current month
                self.highlight_date(selected_date)  # Highlight the date
            except ValueError:
                # If the date is invalid (like Feb 30th), skip it
                continue
        self.calendar.pack(pady=20)

    def on_date_selected(self, selected_date):
        
        """This method will be called when a date is selected."""
        print(f"Selected date: {selected_date}")
        
        try:
            # Handle "MM/DD/YY" format from the calendar
            if "/" in selected_date:
                selected_date = datetime.datetime.strptime(selected_date, "%m/%d/%y").date()
            else:
                # Assume "YYYY-MM-DD" format
                selected_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Error: Invalid date format {selected_date} - {e}")
            return
        
        if hasattr(self, 'calendar'):
            self.calendar.place_forget()
            self.select_button_calendar.place_forget()

        if hasattr(self, 'buttonHome'):
            self.buttonHome.place_forget()
        

        data_exists = self.fetch_data_from_db(selected_date)

        if data_exists:

            if hasattr(self, 'no_data_label'):
                self.no_data_label.place_forget()
            
            self.show_data_summary(selected_date)  # Show data summary in a new tab/frame
        else:

            if hasattr(self, 'calendar'):
                self.calendar.place_forget()
                self.select_button_calendar.place_forget()

            self.no_data_label = ctk.CTkLabel(self.ctk, text=f"no detections occurred on the selected date", font=("Arial", 15), text_color="white")
            self.no_data_label.place(x= 340, y=330)
            self.summary_ui(selected_date)

        # formatted_date = selected_date.strftime("%Y-%m-%d")

        # if self.fetch_data_from_db(formatted_date):
        #     print(f"Data exists for {formatted_date}")
        # else:
        #     print(f"No data found for {formatted_date}")

    def show_data_summary(self, selected_date):
        
        """Show the data summary retrieved from the database."""
        
        # Fetch the data from the database
        data = self.fetch_data_from_db(selected_date)
        
        if data:
            self.scrollable_frame = ctk.CTkScrollableFrame(self.ctk)
            self.scrollable_frame.pack(padx=20, pady=20, fill="both", expand=True)
            # Create a frame for the data display
            data_frame = ctk.CTkFrame(self.scrollable_frame)
            data_frame.pack(padx=20, pady=20, fill="both", expand=True)
            
            # Add the title label
            label = ctk.CTkLabel(data_frame, text=f"Data for {selected_date}", font=("Arial", 15))
            label.grid(row=0, column=0, padx=10, pady=10)

            # Assuming data has fields like "timestamp" and "image_path"
            for i, entry in enumerate(data):
                shoe_id = entry['shoe_id']
                timestamp = entry['timestamp']
                formatted_date = selected_date.strftime("%Y-%m-%d")
                
                # Extract the time portion from the timestamp
                time_part = timestamp.split("_")[1].replace("-", ":")  # Extract the "HH-MM-SS" part from timestamp
                
                # Display the timestamp and time under the label
                data_label = ctk.CTkLabel(data_frame, text=f"Date: {formatted_date}\nTime: {time_part}")
                data_label.grid(row=i + 1, column=0, padx=10, pady=5)

                # Assuming image is named with timestamp and shoe_id
                image_filename = f"shoe_{shoe_id}_{timestamp}.jpg"

                
                # Full path to the image
                full_image_path = os.path.join(image_path, image_filename)

                if os.path.exists(full_image_path):
                    self.display_image(data_frame, full_image_path, i + 1)
                else:
                    print(f"Image not found for {timestamp}.jpg")
                self.buttonback = ctk.CTkLabel(self.ctk, text="← Back", font=("Arial", 17, "bold"), text_color="white", cursor="hand2")
                self.buttonback.place(relx=0.01, rely=0.05, anchor='w')
                self.buttonback.bind("<Button-1>", lambda event: self.summary_ui(self.buttonback))
        
                self.data_summary_buttons = [self.scrollable_frame, data_frame, data_label]
        
        else:

            print("No data available for this date.")
        
       

            
    def toggle_data_summary(self, active_button):

        """Toggle the display of data summary."""
        if hasattr(self, 'data_summary_label'):
            self.data_summary_label.place_forget()  # Hide it if already shown
        else:
            self.show_data_summary()  # Show the data summary

    def display_image(self, data_frame, image_path, row):
        """Display an image in the data frame."""
        try:
            # Open the image file
            image = Image.open(image_path)
            image = image.resize((476, 289))  # Resize to fit in the UI
            photo = ImageTk.PhotoImage(image)

            # Create a label for the image and add it to the data frame
            image_label = ctk.CTkLabel(data_frame, image=photo, text="")
            image_label.image = photo  # Keep reference to avoid garbage collection
            image_label.grid(row=row, column=1, padx=100, pady=3)  # Adjust position as needed
        except Exception as e:
            print(f"Error loading image: {e}")


    def fetch_data_from_db(self, selected_date):
        """Fetch data from the database for a specific date."""
        # Format the selected date as YYYY-MM-DD (e.g., 2024-11-17)
        formatted_date = selected_date.strftime("%Y-%m-%d")
        print(f"Formatted date for query: {formatted_date}")  # Debugging line
        
        # Query the database for entries where the timestamp starts with the formatted date
        # Use $regex to match the date portion in "YYYY-MM-DD_HH-MM-SS" format
        data = self.collection.find({"timestamp": {"$regex": f"^{formatted_date}"}})
        
        # Convert the cursor to a list
        data_list = list(data)
        print(f"Data fetched: {data_list}")  # Debugging: check if data is fetched correctly
        
        # If data exists for that date, return it
        if data_list:
            return data_list  # Return the list of data for this date
        else:
            return []  # No data found for the selected date
        
    def exit_program(self):
        """Exit the program."""
        self.exit_flag = True
        self.ctk.destroy()
        exit()

if __name__ == "__main__":
    control_panel = ControlPanel()
    control_panel.ctk.mainloop()