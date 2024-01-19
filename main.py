from weather_data import *
import customtkinter as ctk
import tkinter as tk
from io import BytesIO
from PIL import Image, ImageTk
import metpy.calc as mpcalc
import datetime


ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")

class WeatherGUI(ctk.CTk):
    
    def __init__(self,city_names_to_lat_long):
        # need this otherwise git this error: [Previous line repeated 993 more times]
        super().__init__()
        
        # Basic setup
        self.title("Weather Forecast")
        self.geometry("1200x700")
        # Function do not call it yet
        self.city_names_to_lat_long = city_names_to_lat_long
        # Get the data from the Weather API
        self.current_weather_data, self.forecast_weather_data = self.city_names_to_lat_long('Oostende')
        
        ## FRAME 1 >> Current weather data
        self.current_weather_frame = CurrentWeatherFrame(master = self, 
                                                         width = 1200,
                                                         height = 400,
                                                         border_width = 3,
                                                         current_weather_data = self.current_weather_data,
                                                         weather_image = self.weather_image,
                                                         get_location = self.get_location)
        self.current_weather_frame.place(relx = 0, rely = 0)
        
        
        ## Frame 2 >> Weather forecast upcoming 5 days
        self.forecast_weather_frame = ForecastWeatherFrame(master = self,
                                                         #border_color = '#0C3142',
                                                         fg_color = 'white',
                                                         width = 1200,
                                                         height = 300,
                                                         border_width = 3,
                                                         weather_image = self.weather_image,
                                                         forecast_weather_data = self.forecast_weather_data)
        self.forecast_weather_frame.place(x = 0, y = 400)
        
    def weather_image(self, img_id, size):
        #The link to acces the images
        img_url = f'https://openweathermap.org/img/wn/{img_id}@4x.png'
        # Get the response image from the URL
        response = requests.get(img_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Open the image using PIL
            image = Image.open(BytesIO(response.content))
            
            # Convert the image to PhotoImage
            self.image =  ctk.CTkImage(dark_image = image, size = size)
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")

        return self.image
    
    def get_location(self, location):
        
        # Get the data using the entered location
        entered_location = location.get()
        #Update the frames by parsing the new inforamtion the the GUI frames
        self.update_frames(entered_location)
    
    def update_frames(self, entered_location):
        # Get the data using the entered location
        self.current_weather_data, self.forecast_weather_data = self.city_names_to_lat_long(entered_location)

        # Update the frames with the new weather data
        self.current_weather_frame.update_weather_data(self.current_weather_data)
        self.forecast_weather_frame.update_forecast_data(self.forecast_weather_data)
        
        
    
class CurrentWeatherFrame(ctk.CTkFrame):
    
    def __init__(self, master, current_weather_data, weather_image, get_location, **kwargs):
        
        super().__init__(master, **kwargs)        

        # Save the dictionary into a variable 
        self.current_weather_data = current_weather_data
        self.weather_image = weather_image
        self.get_location = get_location
        
        # How to add an image onto the window
        self.canvas_for_image = tk.Canvas(master = self, bg = 'white', width = 1200, height = 400, highlightthickness = 0)
        self.canvas_for_image.pack()
        self.bg_downl = Image.open('graphics/sky_full_stars.jpg')
        self.canvas_for_image.image = ImageTk.PhotoImage(self.bg_downl.resize((1200, 1200), Image.Resampling.LANCZOS))
        self.canvas_for_image.create_image(0, 0, image = self.canvas_for_image.image, anchor='nw')
        
        # Add widgets onto the frame        
        self.current_stats_frame = WeatherStatsCurrent(master = self, 
                                                fg_color = '#66B7DC',
                                                width = 630,
                                                height = 350, 
                                                border_width = 4,
                                                border_color = '#0C3142',
                                                current_weather_data = self.current_weather_data,
                                                weather_image = self.weather_image)  
        self.current_stats_frame.place(x = 50, y = 25)
        
        # Set the border and background color as the same so it doesn have weird corners shown
        self.location_string = tk.StringVar(value = 'Oostende')
        self.location_entry = ctk.CTkEntry(master = self, width = 350, height = 50, text_color = 'white', 
                                           font = (None, 22, 'bold'), border_width = 5, bg_color = '#0C3142', border_color = '#0C3142',
                                           textvariable = self.location_string)
        self.location_entry.place(relx = 0.75, rely = 0.5, anchor = 'center')
        
        # Add a button to search tho location
        # Use a lambda command so can keep calling the function each time when pressing a button
        self.search_button_image = ImageTk.PhotoImage(Image.open('graphics/search.png').resize((50,50), Image.Resampling.LANCZOS))
        self.search_button = tk.Button(master = self, 
                                           text = '', 
                                           image = self.search_button_image, 
                                           height = 50, width = 50, 
                                           borderwidth = 0, highlightthickness = 0,
                                           
                                           command = lambda: self.get_location(self.location_string))
        self.search_button.place(relx = 0.93, rely = 0.5, anchor = 'center')
        
    def update_weather_data(self, current_weather_data):
        #Update the variable information given to current weather data
        self.current_weather_data = current_weather_data
        # Now need to call the function in the WeatherStatsCurrent to update the lables
        self.current_stats_frame.update_stats(self.current_weather_data)
        
class WeatherStatsCurrent(ctk.CTkFrame):
    
    def __init__(self, master, current_weather_data, weather_image, **kwargs):
        
        super().__init__(master, **kwargs)
        
        self.current_weather_data = current_weather_data
        self.weather_image = weather_image
        
        self.current_weather_image = self.weather_image(self.current_weather_data['icon'], size = (300, 300))
        self.weather_icon = ctk.CTkLabel(master = self, image = self.current_weather_image, text = "")
        self.weather_icon.place(relx = 0.25, rely = 0.5, anchor = 'center')
        
        # Get the current time
        current_time = datetime.datetime.now()
        
        self.curr_label = ctk.CTkLabel(master = self, 
                                           text = f"{current_time.strftime('%a - %H:%M')}",
                                           fg_color = '#2B2B2B',
                                           text_color = 'white',
                                           corner_radius = 32,
                                           height = 53,
                                           font = (None, 48, 'bold'))
        self.curr_label.place(relx = 0.25, rely = 0.15, anchor = 'center')
       
        # Label with the temperature
        self.temperature_label = ctk.CTkLabel(master = self, 
                                           text = f'{self.current_weather_data["current_temp"]} °C',
                                           fg_color = 'transparent',
                                           text_color = 'white',
                                           font = (None, 48, 'bold'))
        self.temperature_label.place(relx = 0.7, rely = 0.15, anchor = 'center')
        
        self.description_label = ctk.CTkLabel(master = self,
                                              text = f'{self.current_weather_data["description"].title()}',
                                              fg_color = 'transparent',
                                              text_color = 'white',
                                              font = (None, 36, 'bold'))
        self.description_label.place(relx = 0.7, rely = 0.3, anchor = 'center')
        
        self.temp_min_max_label = ctk.CTkLabel(master = self, 
                                            text = f'Max: {self.current_weather_data["max_temp"]} °C\n Min: {self.current_weather_data["min_temp"]} °C',
                                            fg_color = '#2B2B2B',
                                            text_color = 'white',
                                            corner_radius = 32,
                                            width = 250, 
                                            font = (None, 22, 'bold'),
                                            height = 50)       
        self.temp_min_max_label.place(relx = 0.7, rely = 0.45, anchor = 'center') 
        
        self.wind_direction = mpcalc.angle_to_direction(self.current_weather_data["wind_degree"])
        
        self.wind_direction_label = ctk.CTkLabel(master = self,
                                                text = f'{self.wind_direction} - {self.current_weather_data["wind_speed"]} Km/H',
                                                fg_color = '#2B2B2B',
                                                text_color = 'white',
                                                corner_radius = 32,
                                                width = 250,
                                                font = (None, 22, 'bold'))
        self.wind_direction_label.place(relx = 0.7, rely = 0.6, anchor = 'center')
        
        self.visibility_label = ctk.CTkLabel(master = self,
                                                text = f'Visibility: {self.current_weather_data["visibility"] // 1000} Km',
                                                fg_color = '#2B2B2B',
                                                text_color = 'white',
                                                corner_radius = 32,
                                                width = 250,
                                                font = (None, 22, 'bold'))
        self.visibility_label.place(relx = 0.7, rely = 0.7, anchor = 'center')

        self.rain_label = ctk.CTkLabel(master = self,
                                                text = f'Rain: {self.current_weather_data["rain"]} mm',
                                                fg_color = '#2B2B2B',
                                                text_color = 'white',
                                                corner_radius = 32,
                                                width = 250,
                                                font = (None, 22, 'bold'))
        self.rain_label.place(relx = 0.7, rely = 0.8, anchor = 'center')
        
        
    def update_stats(self, current_weather_data):
        #Load in the new gathered data
        self.current_weather_data = current_weather_data
        
        self.current_weather_image = self.weather_image(self.current_weather_data['icon'], size = (300, 300))
        self.weather_icon.configure(image = self.current_weather_image)
        
        self.temperature_label.configure(text = f"{self.current_weather_data['current_temp']} °C")
        
        self.description_label.configure(text = f'{self.current_weather_data["description"].title()}')
        
        self.temp_min_max_label.configure(text = f'Max: {self.current_weather_data["max_temp"]} °C\n Min: {self.current_weather_data["min_temp"]} °C')
        
        self.wind_direction = mpcalc.angle_to_direction(self.current_weather_data["wind_degree"])
        
        self.wind_direction_label.configure(text = f'{self.wind_direction}\t {self.current_weather_data["wind_speed"]} Km/H')
        
        self.visibility_label.configure(text = f'Visibility: {self.current_weather_data["visibility"] // 1000} Km')
               
class ForecastWeatherFrame(ctk.CTkFrame):
    
    def __init__(self, master, forecast_weather_data, weather_image, **kwargs):
    
        super().__init__(master, **kwargs)

        # Save the dictionary into a variable 
        self.forecast_weather_data = forecast_weather_data
        self.weather_image = weather_image
        self.forecast_weather_data[list(self.forecast_weather_data.keys())[0]]
        
        # Add widgets onto the frame       
        # Will parse the data by calling the key in a variable as the dictionary of that day containg the date 
        self.forecast_day_1 = WeatherStatsForecast(master = self, 
                                                fg_color = '#66B7DC',
                                                width = 200,
                                                height = 250, 
                                                forecast_data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[0]],
                                                date = list(self.forecast_weather_data.keys())[0],  
                                                weather_image = self.weather_image)  
        self.forecast_day_1.place(x = 33, y = 25)
        self.forecast_day_2 = WeatherStatsForecast(master = self, 
                                                fg_color = '#66B7DC',
                                                width = 200,
                                                height = 250, 
                                                forecast_data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[1]],
                                                date = list(self.forecast_weather_data.keys())[1],  
                                                weather_image = self.weather_image)  
        self.forecast_day_2.place(x = 266, y = 25)
        self.forecast_day_3 = WeatherStatsForecast(master = self, 
                                                fg_color = '#66B7DC',
                                                width = 200,
                                                height = 250, 
                                                forecast_data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[2]],
                                                date = list(self.forecast_weather_data.keys())[2],  
                                                weather_image = self.weather_image)  
        self.forecast_day_3.place(x = 499, y = 25)
        self.forecast_day_4 = WeatherStatsForecast(master = self, 
                                                fg_color = '#66B7DC',
                                                width = 200,
                                                height = 250, 
                                                forecast_data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[3]],
                                                date = list(self.forecast_weather_data.keys())[3],  
                                                weather_image = self.weather_image)  
        self.forecast_day_4.place(x = 732, y = 25)
        self.forecast_day_5 = WeatherStatsForecast(master = self, 
                                                fg_color = '#66B7DC',
                                                width = 200,
                                                height = 250, 
                                                forecast_data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[4]],
                                                date = list(self.forecast_weather_data.keys())[4],  
                                                weather_image = self.weather_image)  
        self.forecast_day_5.place(x = 965, y = 25)
    
    def update_forecast_data(self, forecast_weather_data):
        # I parse the new list when called in the previous frame into this function
        self.forecast_weather_data = forecast_weather_data
        #Now can call another function in the frame down below to update the forecast inforamtio on each frame
        self.forecast_day_1.update_stats(data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[0]], date = list(self.forecast_weather_data.keys())[0])
        self.forecast_day_2.update_stats(data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[1]], date = list(self.forecast_weather_data.keys())[1])
        self.forecast_day_3.update_stats(data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[2]], date = list(self.forecast_weather_data.keys())[2])
        self.forecast_day_4.update_stats(data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[3]], date = list(self.forecast_weather_data.keys())[3])
        self.forecast_day_5.update_stats(data_day = self.forecast_weather_data[list(self.forecast_weather_data.keys())[4]], date = list(self.forecast_weather_data.keys())[4])

        
class WeatherStatsForecast(ctk.CTkFrame):
    
    def __init__(self, master, forecast_data_day, date, weather_image, **kwargs):
        
        super().__init__(master, **kwargs)
        
        self.forecast_data_day = forecast_data_day
        self.weather_image = weather_image
        
        # Reformat the date into BE dates
        splitted_date = date.split(' ')
        splitted_date_only = splitted_date[0].split('-')
        self.date = '-'.join(reversed(splitted_date_only))
        
        # Picture >> First place the picture so it wont overlap with any other widgets, thats why set it as first widget and place the others on top of it
        self.forecast_weather_image = self.weather_image(self.forecast_data_day['icon'], size = (100,100))
        self.weather_icon = ctk.CTkLabel(master = self, image = self.forecast_weather_image, text = "")
        self.weather_icon.place(relx = 0.5, rely = 0.4, anchor = 'center')  
        
        # Date
        #self.date_splitted = self.date.split(' ')
        self.date_label = ctk.CTkLabel(master = self, 
                                       text = f'{self.date}',
                                       fg_color = '#2B2B2B',
                                       corner_radius = 32,
                                       text_color = 'white',
                                       font = (None, 22, 'bold'),
                                       padx = 4,
                                       pady = 6)
        self.date_label.place(relx = 0.5, rely = 0.15, anchor = 'center')     
        
        # Descr
        self.descr_label = ctk.CTkLabel(master = self, 
                                       text = f'{self.forecast_data_day["description"].title()}',
                                       fg_color = 'transparent',
                                       text_color = 'white',
                                       font = (None, 18, 'bold'))
        self.descr_label.place(relx = 0.5, rely = 0.6, anchor = 'center')         
        
        # Temp
        self.temp_label = ctk.CTkLabel(master = self, 
                                       text = f'{self.forecast_data_day["current_temp"]} °C',
                                       fg_color = 'transparent',
                                       text_color = 'white',
                                       font = (None, 18, 'bold'))
        self.temp_label.place(relx = 0.5, rely = 0.75, anchor = 'center') 
        
        # Wind
        self.wind_direction = mpcalc.angle_to_direction(self.forecast_data_day["wind_degree"])
        self.wind_label = ctk.CTkLabel(master = self, 
                                       text = f'{self.wind_direction} - {self.forecast_data_day["wind_speed"]} Km/h',
                                       fg_color = 'transparent',
                                       text_color = 'white',
                                       font = (None, 18, 'bold'))
        self.wind_label.place(relx = 0.5, rely = 0.9, anchor = 'center')      
        
    def update_stats(self, data_day, date):
        
        # Picture >> First place the picture so it wont overlap with any other widgets, thats why set it as first widget and place the others on top of it
        self.forecast_weather_image = self.weather_image(data_day['icon'], size = (100,100))
        self.weather_icon.configure(image = self.forecast_weather_image)
        
        # Date
        self.date_splitted = date.split(' ')
        self.date_label.configure(text = f'{self.date_splitted[0]}')   
        
        # Descr
        self.descr_label.configure(text = f'{data_day["description"].title()}')       
        
        # Temp
        self.temp_label.configure(text = f'{data_day["current_temp"]} °C') 
        
        # Wind
        self.wind_direction = mpcalc.angle_to_direction(data_day["wind_degree"])
        self.wind_label.configure(text = f'{self.wind_direction} - {data_day["wind_speed"]} Km/h')
          
        
        

if __name__ == "__main__":
    
    # Parse into the Tkinter class for the GUI >> Give the function needed to get the weather data with it 
    app = WeatherGUI(city_names_to_lat_long)
    app.mainloop()
  