from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import AsyncImage, Image
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.textinput import TextInput
from kivy.uix.relativelayout import RelativeLayout
import sqlite3
from kivy.uix.popup import Popup
import os

# Create a connection and cursor
conn = sqlite3.connect('login_A.db')
c = conn.cursor()

# Create a table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT)''')
conn.commit()

class LoginPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = RelativeLayout()

        # Background Image
        background = AsyncImage(source="greenimage.jpg",
                                allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        box_layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        # Login Title
        label1 = Label(text="Login", font_size=50, bold=True, color=(0, 0, 0, 1))
        box_layout.add_widget(label1)

        # Welcome label
        self.welcome_label = Label(text="", font_size=18, color=(1, 1, 1, 1), size_hint_y=None, height=50)
        box_layout.add_widget(self.welcome_label)

        # Name input
        self.name_input = TextInput(hint_text="Enter your name", size_hint_y=None, height=50,
                                     background_color=(1, 1, 1, 0.5), foreground_color=(0, 0, 0, 1),
                                     hint_text_color=(0.5, 0.5, 0.5, 1))
        box_layout.add_widget(self.name_input)

        # Email input
        self.email_input = TextInput(hint_text="Enter your email", size_hint_y=None, height=50,
                                      background_color=(1, 1, 1, 0.5), foreground_color=(0, 0, 0, 1),
                                      hint_text_color=(0.5, 0.5, 0.5, 1))
        box_layout.add_widget(self.email_input)

        # Password input
        self.password_input = TextInput(hint_text="Enter Password", size_hint_y=None, height=50,
                                         background_color=(1, 1, 1, 0.5), foreground_color=(0, 0, 0, 1),
                                         hint_text_color=(0.5, 0.5, 0.5, 1), password=True)
        box_layout.add_widget(self.password_input)
        self.begin_button = Button(text="Begin", size_hint_y=None, height=50, background_color=(0.6, 0.8, 0.4, 1), bold=True)
        self.begin_button.bind(on_press=self.login)
        self.begin_button.height = 0
        self.begin_button.bind(on_press=self.show_popup)
        box_layout.add_widget(self.begin_button)
        self.hide_welcome()


        login_button = Button(text="Login", size_hint_y=None, height=50, background_color=(0, 0.5, 0, 1), bold=True)
        login_button.bind(on_press=self.login)
        box_layout.add_widget(login_button)

        signup_button = Button(text="Sign Up", size_hint_y=None, height=50, background_color=(0, 0.5, 0, 1), bold=True)
        signup_button.bind(on_press=self.signup)
        box_layout.add_widget(signup_button)

        layout.add_widget(box_layout)
        self.add_widget(layout)

        self.hide_welcome()

    def hide_welcome(self):
        self.welcome_label.text = ""
        self.welcome_label.height = 0
        self.welcome_label.color = (0,0,0,1)

    def show_welcome(self, message):
        self.welcome_label.text = message
        self.welcome_label.height = 50

    def login(self, instance):
        name = self.name_input.text
        email = self.email_input.text
        password = self.password_input.text

        # Check if the email and password match any record in the database
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()

        if user:
            self.welcome_label.text = f"Welcome {name} to RuralCare"
            self.welcome_label.visible = True
            self.begin_button.visible = True
            print("Login successful!")
            self.begin_button.height = 50
        else:
            self.welcome_label.text = "Invalid email or password."
            self.welcome_label.visible = True
            self.begin_button.visible = False
        

    def signup(self, instance):
        name = self.name_input.text
        email = self.email_input.text
        password = self.password_input.text

        # Check if the email already exists in the database
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = c.fetchone()

        if existing_user:
            self.show_welcome("Email already registered.")
        else:
            # Insert the new user into the database
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            self.show_welcome(f"Welcome {name} to RuralCare")
            print("Sign up successful!")
            self.begin_button.height = 50

    def show_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        popup = Popup(title='Choose an option:', content=content, size_hint=(None, None), size=(400, 300))

        option1_button = Button(text='Find Nearby Specialists', size_hint_y=None, height=40)
        option1_button.bind(on_press=self.redirect_to_map)
        content.add_widget(option1_button)

        option2_button = Button(text='Health Prediction', size_hint_y=None, height=40)
        option2_button.bind(on_press=self.redirect_to_prediction)
        content.add_widget(option2_button)

        option3_button = Button(text='Learn More about Healthcare', size_hint_y=None, height=40)
        option3_button.bind(on_press=self.redirect_to_community)
        content.add_widget(option3_button)

        popup.open()

    def redirect_to_prediction(self, instance):
        os.system("python obesity1.pyt")

    def redirect_to_map(self, instance):
        os.system("python map.py")

    def redirect_to_community(self, instance):
        os.system("python Nutrition.pyt")

    

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = RelativeLayout()
        background = AsyncImage(source="greenimage.jpg",
                                allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        box_layout = BoxLayout(orientation='vertical', padding=50)
        ruralcare_logo = Image(source="ruralcarelogo.jpg", size_hint=(None, None), size=(300, 300))
        ruralcare_logo.pos_hint = {'center_x': 0.5}
        box_layout.add_widget(ruralcare_logo)
        
        label1 = Label(text="Villages to the World: Your Health, Our Priority", font_size=50, color=(1, 1, 1, 1),
                       bold=True, halign='center')
        box_layout.add_widget(label1)

        label2 = Label(text="Connecting Hearts, Healing Lives: Your Health, Our Mission", font_size=35,
                       color=(1, 1, 1, 1), bold=True, halign='center')
        box_layout.add_widget(label2)

        # Adjusting spacing between labels
        box_layout.spacing = 10  # Set the spacing to 10 pixels

        button = Button(text="Get Started", size_hint=(None, None), size=(250, 50),
                        background_color=(0.2, 0.6, 0.2, 1), bold=True, color=(1, 1, 1, 1),
                        font_size=20, on_press=self.go_to_login_page)
        button.pos_hint = {'center_x': 0.5}
        box_layout.add_widget(button)
        layout.add_widget(box_layout)
        self.add_widget(layout)

    def go_to_login_page(self, instance):
        self.manager.current = 'login'

    
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(LoginPage(name='login'))
        return sm

if __name__ == '__main__':
    MyApp().run()
conn.close()
