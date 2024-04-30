import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.multioutput import MultiOutputClassifier
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

Window.clearcolor = (0.2, 0.2, 0.2, 1)  # Set a dark background color

class PredictionPopup(Popup):
     def __init__(self, prediction, message, **kwargs):
        super().__init__(**kwargs)
        content = BoxLayout(orientation='vertical', padding=20)
        result_label = Label(text=f"Predicted Obesity Category: {prediction}", font_size=18, color=(1, 1, 1, 1), halign='center')
        content.add_widget(result_label)

        scroll_view = ScrollView(size_hint=(1,2))
        message_label = Label(text=message, font_size=18, color=(1, 1, 1, 1), halign='center', text_size=(2000, None), size_hint_y=None)
        scroll_view.add_widget(message_label)
        content.add_widget(scroll_view)

        self.content = content
        self.size_hint = (None, None)
        self.size = (1000,1000)

class MLApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feature_columns = ['Age', 'Gender', 'Height (cm)', 'Weight  (kg)', 'BMI ', 'PhysicalActivityLevel']
        self.label_encoders = {}
        self.string_encoder = OneHotEncoder(handle_unknown='ignore')
        self.clf = MultiOutputClassifier(RandomForestClassifier())

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        with self.layout.canvas:
            Color(0.3, 0.3, 0.3, 1)  # Set a dark gray background color
            self.rect = RoundedRectangle(pos=self.layout.pos, size=self.layout.size, radius=[20])
            self.layout.bind(pos=self.update_rect, size=self.update_rect)

        header_label = Label(text='Obesity Prediction', font_size=30, bold=True, color=(1, 1, 1, 1))
        self.layout.add_widget(header_label)

        self.inputs = {}
        for feature in self.feature_columns:
            if feature == 'Gender':
                gender_spinner = Spinner(text='Select Gender', values=['Male', 'Female'], background_color=(0.4, 0.4, 0.4, 1), font_size=18, color=(1, 1, 1, 1))
                gender_spinner.bind(text=self.on_spinner_select)
                self.inputs[feature] = gender_spinner
                self.layout.add_widget(gender_spinner)
            else:
                input_label = Label(text=feature, font_size=18, color=(1, 1, 1, 1))
                input_text = TextInput(background_color=(0.4, 0.4, 0.4, 1), foreground_color=(1, 1, 1, 1), font_size=18, halign='center')
                self.inputs[feature] = input_text
                self.layout.add_widget(input_label)
                self.layout.add_widget(input_text)

        predict_button = Button(text='Predict', size_hint_y=None, height=50, background_color=(0.6, 0.8, 0.4, 1), bold=True, font_size=18)
        predict_button.bind(on_press=self.predict)
        self.layout.add_widget(predict_button)

        return self.layout

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def preprocess_data(self):
        obesity_data = pd.read_csv('obesity_data.csv', encoding='ISO-8859-1')
        target_columns = ['ObesityCategory']
        X = obesity_data[self.feature_columns]
        y = obesity_data[target_columns]

        for column in y.columns:
            self.label_encoders[column] = LabelEncoder()
            y[column] = self.label_encoders[column].fit_transform(y[column])

        X['Gender'] = LabelEncoder().fit_transform(X['Gender'])
        return X, y

    def train_model(self, X, y):
        self.clf.fit(X, y)

    def predict(self, instance):
        user_input = []
        for feature in self.feature_columns:
            if feature == 'Gender':
                user_input.append(self.inputs[feature].text)
            else:
                user_input.append(float(self.inputs[feature].text))

        user_input_df = pd.DataFrame([user_input], columns=self.feature_columns)

        user_input_df['Gender'] = LabelEncoder().fit_transform(user_input_df['Gender'])

        result = self.clf.predict(user_input_df)[0]

        result_decoded = {column: self.label_encoders[column].inverse_transform([result[i]])[0]
                          for i, column in enumerate(y.columns)}
        obesity_category = result_decoded['ObesityCategory']
        if obesity_category == 'Normal weight':
            message = "Well done! Keep it up!"
        elif obesity_category == 'Obese' or obesity_category == 'Overweight':
            message = "Here are some workouts to do and what to eat to live healthily:\n\nWorkouts:\nCardiovascular Exercises: Engage in activities like brisk walking, jogging, cycling, swimming, or using cardio machines like treadmills or ellipticals. Aim for at least 150 minutes of moderate-intensity aerobic activity per week.\nStrength Training: Include exercises that target major muscle groups such as squats, lunges, push-ups, and weightlifting. Strength training helps build lean muscle mass, which can increase metabolism and aid in weight management.\nHigh-Intensity Interval Training (HIIT): Incorporate short bursts of intense exercise followed by brief recovery periods. HIIT workouts can be effective for burning calories and improving cardiovascular health in a shorter amount of time.\nFlexibility and Balance Exercises: Practice yoga, Pilates, or tai chi to improve flexibility, balance, and overall mobility. These exercises can also help reduce stress and promote relaxation.\n\nDietary Recommendations:\nBalanced Diet: Focus on consuming a variety of nutrient-dense foods from all food groups, including fruits, vegetables, whole grains, lean proteins, and healthy fats. Limit the intake of processed foods, sugary snacks, and high-calorie beverages.\nPortion Control: Be mindful of portion sizes and avoid overeating. Use smaller plates and bowls, and listen to your body's hunger and fullness cues.\nHydration: Drink plenty of water throughout the day to stay hydrated and support bodily functions. Limit sugary drinks and alcohol, which can contribute to excess calorie intake.\nMeal Planning: Plan and prepare meals in advance to avoid relying on convenience foods or fast food options. Incorporate plenty of fruits and vegetables into meals and snacks for added fiber and nutrients.\nMindful Eating: Practice mindful eating by paying attention to hunger and satiety cues, eating slowly, and savoring each bite. Avoid distractions like television or smartphones while eating to prevent overeating."
        elif obesity_category == 'Underweight':
            message = "Here's a diet plan for gaining weight and living healthily:\n\nIncrease Caloric Intake:\nConsume more calories than your body burns to promote weight gain. Aim for a surplus of 500 to 1000 calories per day to gain weight at a gradual and healthy pace.\nInclude calorie-dense foods such as nuts, seeds, nut butters, avocados, dried fruits, whole milk, cheese, yogurt, and healthy oils like olive oil and coconut oil.\n\nNutrient-Rich Foods:\nOpt for nutrient-dense foods that provide essential vitamins, minerals, protein, and healthy fats to support overall health and weight gain.\nIncorporate a variety of fruits, vegetables, whole grains, lean proteins, and dairy or dairy alternatives into your meals and snacks.\n\nFrequent Meals and Snacks:\nAim to eat smaller, frequent meals and snacks throughout the day to increase overall calorie intake. Include snacks between meals and before bedtime to provide continuous fuel for your body. Choose nutrient-dense snacks such as Greek yogurt with fruit, trail mix, cheese and whole grain crackers, smoothies with protein powder, or peanut butter and banana sandwiches.\n\nProtein-Rich Foods:\nConsume protein-rich foods to support muscle growth and repair. Include sources of lean protein such as poultry, fish, eggs, tofu, legumes, nuts, and seeds in your diet.\nConsider adding protein supplements like whey protein powder to smoothies or shakes to boost protein intake.\n\nHealthy Fats:\nIncorporate healthy fats into your diet to increase calorie density and provide essential fatty acids. Include sources like avocados, nuts, seeds, olive oil, fatty fish (salmon, mackerel, sardines), and coconut oil.\n\nHydration:\nStay hydrated by drinking plenty of water throughout the day. Avoid excessive consumption of sugary drinks and focus on hydrating beverages like water, herbal teas, and homemade fruit-infused water.\n\nMeal Planning and Preparation:\nPlan and prepare meals and snacks in advance to ensure you have calorie-dense options readily available. Cook extra portions of meals to have leftovers for quick and convenient meals throughout the week.\n\nRegular Exercise:\nIncorporate strength training exercises into your fitness routine to build muscle mass and promote healthy weight gain. Focus on compound exercises like squats, lunges, deadlifts, and bench presses."

        prediction_popup = PredictionPopup(obesity_category, message)
        prediction_popup.open()

    def on_spinner_select(self, instance, value):
        self.inputs['Gender'].text = value

if __name__ == '__main__':
    app = MLApp()
    X, y = app.preprocess_data()
    app.train_model(X, y)
    app.run()