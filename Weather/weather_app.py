import os
import requests
import tkinter as tk
from tkinter import messagebox, font
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast")
        self.root.geometry("800x900")  # Increased size for additional graphs
        self.root.configure(bg="#ADD8E6")

        self.city_data = self.load_city_data()
        self.search_var = tk.StringVar()
        self.create_widgets()

    def get_weather_data(self, city_name, api_key):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return {}

    def load_city_data(self):
        try:
            df = pd.read_csv("cities.csv")
            print("City data loaded successfully:")
            print(df.head())  # Debugging line to check the loaded data
            return df
        except FileNotFoundError:
            print("Error: cities.csv file not found.")
            return pd.DataFrame(columns=["city", "country"])
        except pd.errors.EmptyDataError:
            print("Error: cities.csv is empty.")
            return pd.DataFrame(columns=["city", "country"])
        except Exception as e:
            print(f"Unexpected error: {e}")
            return pd.DataFrame(columns=["city", "country"])

    def search_city(self, *args):
        search_term = self.search_var.get().lower()
        if search_term:
            filtered_cities = [
                f"{row['city']}, {row['country']}"
                for _, row in self.city_data.iterrows()
                if search_term in row["city"].lower()
            ]
            self.city_combobox["values"] = filtered_cities
            if filtered_cities:
                self.city_combobox.set(filtered_cities[0])
        else:
            self.city_combobox["values"] = []

    def load_image(self, icon_name):
        icon_path = f"icons/{icon_name}.png"
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
            return ImageTk.PhotoImage(image)
        return None

    def plot_weather_data(self, temp, humidity, wind_speed_kmh):
        fig, axs = plt.subplots(1, 3, figsize=(5.5, 5))  # Adjusted to 3 subplots
        plt.subplots_adjust(wspace=0.3)  # Adjust space between plots

        # Pie Chart for Temperature
        axs[0].pie(
            [temp, 100 - temp],
            labels=["Temperature", "Rest"],
            autopct="%1.1f%%",
            colors=["#FF6347", "#D3D3D3"],
        )
        axs[0].set_title("Temperature")

        # Pie Chart for Humidity
        axs[1].pie(
            [humidity, 100 - humidity],
            labels=["Humidity", "Rest"],
            autopct="%1.1f%%",
            colors=["#4682B4", "#D3D3D3"],
        )
        axs[1].set_title("Humidity")

        # Pie Chart for Wind Speed
        axs[2].pie(
            [wind_speed_kmh, 100 - wind_speed_kmh],
            labels=["Wind Speed", "Rest"],
            autopct="%1.1f%%",
            colors=["#32CD32", "#D3D3D3"],
        )
        axs[2].set_title("Wind Speed")

        plt.tight_layout()
        return fig

    def create_widgets(self):
        title_font = font.Font(family="Helvetica", size=18, weight="bold")
        label_font = font.Font(family="Helvetica", size=12)
        button_font = font.Font(family="Helvetica", size=12, weight="bold")

        title_label = tk.Label(
            self.root,
            text="Weather Forecast",
            font=title_font,
            bg="#ADD8E6",
            fg="#00008B",
        )
        title_label.pack(pady=10)

        search_entry = tk.Entry(
            self.root,
            textvariable=self.search_var,
            font=label_font,
            justify="center",
            bg="#F0FFFF",
            fg="#00008B",
        )
        search_entry.pack(pady=5, ipady=3)

        self.city_combobox = ttk.Combobox(self.root, font=label_font)
        self.city_combobox.pack(pady=5, fill=tk.X, padx=10)
        self.city_combobox.set("Select a city")

        # Bind the search_var to the search_city method
        self.search_var.trace("w", self.search_city)

        get_weather_button = tk.Button(
            self.root,
            text="Get Weather",
            command=self.show_weather,
            font=button_font,
            bg="#4682B4",
            fg="white",
        )
        get_weather_button.pack(pady=15)

        self.icon_label = tk.Label(self.root, bg="#ADD8E6")
        self.icon_label.pack(pady=10)

        self.result_label = tk.Label(
            self.root, text="", font=label_font, bg="#ADD8E6", fg="#00008B"
        )
        self.result_label.pack(pady=10)

        self.graph_frame = tk.Frame(self.root, bg="#ADD8E6")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def show_weather(self):
        city_name = self.city_combobox.get()
        if not city_name or city_name == "Select a city":
            messagebox.showwarning("Input Error", "Please select a city")
            return

        city_name = city_name.split(",")[0]
        weather_data = self.get_weather_data(
            city_name, "799ef3bbc65b17ce86943cf9d4f8e491"
        )

        if not weather_data or weather_data.get("cod") != 200:
            messagebox.showerror("Error", "City not found or API request failed")
            return

        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        wind_speed_kmh = wind_speed * 3.6  # Convert wind speed from m/s to km/h
        self.weather_description = weather_data["weather"][0]["description"]
        icon_name = weather_data["weather"][0]["icon"]
        weather_icon = self.load_image(icon_name)

        # Additional Information
        sunrise_utc = datetime.utcfromtimestamp(
            weather_data["sys"]["sunrise"]
        ).strftime("%H:%M:%S")
        sunset_utc = datetime.utcfromtimestamp(weather_data["sys"]["sunset"]).strftime(
            "%H:%M:%S"
        )

        timezone_offset = weather_data["timezone"]
        sunrise_local = (
            datetime.utcfromtimestamp(weather_data["sys"]["sunrise"])
            + timedelta(seconds=timezone_offset)
        ).strftime("%H:%M:%S")
        sunset_local = (
            datetime.utcfromtimestamp(weather_data["sys"]["sunset"])
            + timedelta(seconds=timezone_offset)
        ).strftime("%H:%M:%S")

        rain = weather_data.get("rain", {}).get("1h", 0)
        thunderstorm = "thunderstorm" in self.weather_description.lower()

        weather_result = (
            f"Temperature: {temp}°C\nHumidity: {humidity}%\nWind Speed: {wind_speed_kmh:.2f} km/h\n"
            f"Description: {self.weather_description.capitalize()}\n"
            f"Sunrise (UTC): {sunrise_utc}\nSunset (UTC): {sunset_utc}\n"
            f"Sunrise (Local): {sunrise_local}\nSunset (Local): {sunset_local}\n"
            f"Rain: {rain} mm\nThunderstorm: {'Yes' if thunderstorm else 'No'}"
        )

        self.result_label.config(text=weather_result)
        if weather_icon:
            self.icon_label.config(image=weather_icon)
            self.icon_label.image = weather_icon

        fig = self.plot_weather_data(temp, humidity, wind_speed_kmh)
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
