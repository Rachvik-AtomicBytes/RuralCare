import random
import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy_garden.mapview import MapView, MapMarker
from kivy_garden.mapview import MapMarkerPopup
from geopy.geocoders import Nominatim

class MyMapView(MapView):
    def on_map_marker_select(self, marker):
        print("Map marker selected:", marker)
       
        if isinstance(marker, MapMarkerPopup):
            return
        if marker.specialist_type:
            popup = CustomMapMarkerPopup(marker=marker)
            popup.open()

class CustomMapMarkerPopup(MapMarkerPopup):
    def __init__(self, marker, **kwargs):
        super(CustomMapMarkerPopup, self).__init__(**kwargs)
        self.marker = marker
        self.update_content()

    def update_content(self):
        print("Updating popup content for marker:", self.marker)
        
        self.content = Label(text=self.marker.name)

class MapScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MapScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.load_map()
        self.add_specialist_button()
        self.valid_cities = self.load_city_data()

    def load_map(self):
      
        self.latitude = 12.9716
        self.longitude = 77.5946

        
        self.mapview = MyMapView(lat=self.latitude, lon=self.longitude, zoom=10)

        
        self.marker = MapMarker(lat=self.latitude, lon=self.longitude)
        self.mapview.add_marker(self.marker)

       
        self.add_widget(self.mapview)
    
    def add_specialist_button(self):
        button = Button(text="Search Nearby Specialist", size_hint=(None, None), size=(250, 50), pos=(self.mapview.width + 450, 10))
        button.size_hint = (None, None)
        button.bind(on_press=self.ask_city)
        self.mapview.add_widget(button)

    def ask_city(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=10)
        popup = Popup(title='Enter Your City', content=popup_content, size_hint=(None, None), size=(400, 200))

        city_input = TextInput(text='', multiline=False)
        submit_button = Button(text="Submit")

        def submit_city():
            if city_input.text.strip(): 
                self.validate_city(city_input.text.strip(), popup)

        def capitalize_first_letter(instance, value):
            if city_input.text.strip():  
                city_input.text = ' '.join(word.capitalize() for word in city_input.text.split(' '))

        city_input.bind(text=capitalize_first_letter)
        city_input.bind(on_text_validate=lambda x: submit_city())

        popup_content.add_widget(Label(text="Enter your city:"))
        popup_content.add_widget(city_input)
        popup_content.add_widget(submit_button)

        submit_button.bind(on_press=lambda x: submit_city())

        popup.open()

    def load_city_data(self):
        try:
            city_data = pd.read_csv('worldcities.csv')  
            valid_cities = city_data['city'].str.strip().str.lower().tolist()
            return valid_cities
        except FileNotFoundError:
            return []

    def validate_city(self, city, popup):
        if city.lower() in self.valid_cities:
            self.show_specialist_options(city, popup)
        else:
            popup.dismiss()
            self.ask_city_again()

    def ask_city_again(self):
        def try_again(popup):
            popup.dismiss()
            self.ask_city(None)  

        popup_content = BoxLayout(orientation='vertical', padding=10)
        popup = Popup(title='City Not Found', content=popup_content, size_hint=(None, None), size=(400, 200))

        message_label = Label(text="City not found. Please enter a valid city.")
        try_again_button = Button(text="PLEASE TRY AGAIN")

        popup_content.add_widget(message_label)
        popup_content.add_widget(try_again_button)

        try_again_button.bind(on_press=lambda x: try_again(popup))
        popup.open()

    def show_specialist_options(self, city, previous_popup):
        def close_popup_and_select_specialist(instance):
            specialist_type = instance.text
            
            specialist_popup.dismiss()  
            if specialist_type != "Cardiologist":
                previous_popup.dismiss() 

        
        previous_popup.dismiss()

       
        city_info = self.get_city_coordinates(city)
        if city_info:
            self.latitude = float(city_info['latitude'])
            self.longitude = float(city_info['longitude'])
            self.update_map_center(self.latitude, self.longitude)

        popup_content = BoxLayout(orientation='vertical', padding=10)
        specialist_popup = Popup(title='Choose Specialist', content=popup_content, size_hint=(None, None), size=(400, 200))

        option1 = Button(text="General Practitioner", on_press=close_popup_and_select_specialist)
        option2 = Button(text="Psychiatrist", on_press=close_popup_and_select_specialist)
        option3 = Button(text="Cardiologist", on_press=close_popup_and_select_specialist)

        popup_content.add_widget(option1)
        popup_content.add_widget(option2)
        popup_content.add_widget(option3)

        specialist_popup.open()
        
        
        specialists_locations = self.generate_random_locations(self.latitude, self.longitude)

        
        for location, specialist_type in specialists_locations:
            marker = MapMarker(lat=location[0], lon=location[1])
            marker.specialist_type = specialist_type
            self.mapview.add_marker(marker)

    def generate_random_locations(self, latitude, longitude):
        

        specialists_locations = []
        for _ in range(5):  
            
            offset_latitude = random.uniform(-0.05, 0.05)
            offset_longitude = random.uniform(-0.05, 0.05)

           
            specialist_latitude = latitude + offset_latitude
            specialist_longitude = longitude + offset_longitude

            specialists_locations.append(((specialist_latitude, specialist_longitude), random.choice(["General Practitioner", "Psychiatrist", "Cardiologist"])))

        return specialists_locations

    def get_city_coordinates(self, city):
        try:
            city_data = pd.read_csv('worldcities.csv')  
            city_info = city_data.loc[city_data['city'].str.lower() == city.lower()]
            if not city_info.empty:
                return {'latitude': city_info.iloc[0]['latitude'], 'longitude': city_info.iloc[0]['longitude']}
            else:
                return None
        except FileNotFoundError:
            return None
        
    def update_map_center(self, latitude, longitude):
        self.mapview.center_on(latitude, longitude)
       
        self.marker.lat = latitude
        self.marker.lon = longitude


class MyApp(App):
    def build(self):
        return MapScreen()

if __name__ == '__main__':
    MyApp().run()
