from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineAvatarIconListItem, MDList
from kivymd.app import MDApp
from datetime import datetime
from kivymd.uix.dialog import MDDialog
import json
from kivymd.toast import toast
from kivy.utils import get_color_from_hex

DATA_FILE = "blog.json"

class BlogPostItem(OneLineAvatarIconListItem):
    def __init__(self, title, author, date_published, blog_content, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.author = author
        self.date_published = date_published
        self.blog_content = blog_content
        self.text = f"{self.title} - {self.author} ({self.date_published})"
        self.on_release = self.show_full_post

       
        self.bg_color = get_color_from_hex("#FFFFFF")  # White

    def show_full_post(self, *args):
        dialog = MDDialog(
            title=self.title,
            text=self.blog_content,
            size_hint=(0.8, 0.8),
            auto_dismiss=True,
        )

        
        dialog.background_color = self.bg_color

        dialog.open()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            
            self.bg_color = get_color_from_hex("#CCCCCC")  # Light gray
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            
            self.bg_color = get_color_from_hex("#FFFFFF")  # White
        return super().on_touch_up(touch)

class NutritionBlogScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blog_posts = []
        self.load_blog_posts()
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical")
        
        
        background = Image(source="greenimage.jpg", allow_stretch=True, keep_ratio=False)
        self.add_widget(background)

        label = MDLabel(
            text="Nutrition Support Blog",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),  # White color
            bold=True,
            font_size="150sp",  # Larger font size
        )

        
        additional_text = MDLabel(
            text=("Here you can write blogs and stories that may be helpful to others on this page. "
                  "They may also provide further insights on your text."),
            halign="center",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),  # White color
            bold=True,
            size_hint_y=None,
            height="150dp"  # Fixed height for additional text
        )

        new_post_button = MDRaisedButton(
            text="Write New Blog Post"
        )
        new_post_button.bind(on_release=self.show_post_input)
        
        
        button_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", padding="10dp")
        button_layout.add_widget(new_post_button)

        self.posts_list = MDList()
        for post in self.blog_posts:
            self.posts_list.add_widget(BlogPostItem(**post))
        
        
        layout.add_widget(label)
        layout.add_widget(additional_text)
        layout.add_widget(self.posts_list)
        layout.add_widget(button_layout)  # Add the button layout

        self.add_widget(layout)

    def show_post_input(self, *args):
        title_input = MDTextField(hint_text="Enter post title", required=True, height="80dp")
        author_input = MDTextField(hint_text="Enter your name", required=True, height="80dp")
        content_input = MDTextField(hint_text="Write your blog post here...", multiline=True, height="400dp")

        dialog = MDDialog(
            title="Write New Blog Post",
            type="custom",
            content_cls=BoxLayout(orientation="vertical", spacing="12dp", padding="12dp", size_hint_y=None, height="600dp"),
            size_hint=(None, None),
            size=("400dp", "1000dp"),  # Set the size of the dialog
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(
                    text="Upload Post",
                    on_release=lambda x: self.upload_post(title_input.text, author_input.text, content_input.text, dialog),
                ),
            ],
        )

        dialog.content_cls.add_widget(title_input)
        dialog.content_cls.add_widget(author_input)
        dialog.content_cls.add_widget(content_input)

        dialog.open()

    def save_blog_posts(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.blog_posts, f)

    def load_blog_posts(self):
        try:
            with open(DATA_FILE, "r") as f:
                self.blog_posts = json.load(f)
        except FileNotFoundError:
            self.blog_posts = []
    
    def upload_post(self, title, author, content, dialog):
        if title.strip() and author.strip() and content.strip():
            date_published = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            blog_post = {"title": title, "author": author, "date_published": date_published, "blog_content": content}
            self.blog_posts.append(blog_post)
            self.posts_list.add_widget(BlogPostItem(**blog_post))
            self.save_blog_posts()
            dialog.dismiss()
        else:
            toast("Please fill in all fields before uploading the post.")

class CommunityApp(MDApp):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(NutritionBlogScreen(name="nutrition_blog_screen"))
        return self.screen_manager

if __name__ == '__main__':
    CommunityApp().run()
