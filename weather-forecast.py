import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
import io

API_KEY = "8d8c010549c801d683242d32f22f1447"
CITY_LIST = ["Delhi", "Mumbai", "New York", "London", "Tokyo", "Sydney", "Paris", "Beijing", "Berlin", "Moscow"]
search_history = []

def launch_weather_app():
    weather_app = tk.Toplevel()
    weather_app.title("🌦 Full-Featured Weather App")
    weather_app.geometry("500x700")
    weather_app.configure(bg="#d0e7f9")

    def update_autocomplete(*args):
        typed = city_var.get()
        suggestions = [city for city in CITY_LIST if city.lower().startswith(typed.lower())]
        autocomplete_menu['menu'].delete(0, 'end')
        if suggestions:
            for city in suggestions:
                autocomplete_menu['menu'].add_command(label=city, command=tk._setit(city_var, city))
            autocomplete_menu.pack()
        else:
            autocomplete_menu.pack_forget()

    def get_weather():
        city = city_var.get()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") != 200:
                error_message = data.get("message", "Unknown error occurred.")
                messagebox.showerror("API Error", f"Error: {error_message.capitalize()}")
                return

            city_name = data["name"]
            country = data["sys"]["country"]
            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            icon_code = data["weather"][0]["icon"]

            result = f"""
📍 {city_name}, {country}
🌡 Temperature: {temp} °C
☁ Weather: {weather_desc.capitalize()}
💧 Humidity: {humidity}%
🌬 Wind Speed: {wind} m/s
            """.strip()
            result_label.config(text=result)

            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            icon_img_data = requests.get(icon_url).content
            img = Image.open(io.BytesIO(icon_img_data))
            img = ImageTk.PhotoImage(img)
            icon_label.config(image=img)
            icon_label.image = img

            if city not in search_history:
                search_history.append(city)
                history_listbox.insert(tk.END, city)

            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            forecast_output = ""
            for i in range(0, 40, 8):
                item = forecast_data["list"][i]
                date = item["dt_txt"].split(" ")[0]
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"]
                forecast_output += f"{date} ➤ {temp}°C, {desc.capitalize()}\n"

            forecast_label.config(text=forecast_output.strip())

        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("HTTP Error", f"HTTP error: {http_err}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to connect to server.")
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout", "Request timed out.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def on_history_select(event):
        selection = history_listbox.curselection()
        if selection:
            city = history_listbox.get(selection)
            city_var.set(city)
            get_weather()

    def clear_history():
        search_history.clear()
        history_listbox.delete(0, tk.END)

    heading = tk.Label(weather_app, text="Weather Forecast", font=("Helvetica", 20, "bold"), bg="#d0e7f9")
    heading.pack(pady=10)

    city_var = tk.StringVar()
    city_var.trace("w", update_autocomplete)

    city_entry = tk.Entry(weather_app, textvariable=city_var, font=("Helvetica", 14), justify="center", width=30)
    city_entry.pack(pady=5)

    autocomplete_menu = ttk.OptionMenu(weather_app, city_var, "")
    autocomplete_menu.pack_forget()

    search_btn = tk.Button(weather_app, text="Get Weather", font=("Helvetica", 14), bg="#4fa3f7", fg="white", command=get_weather)
    search_btn.pack(pady=10)

    icon_label = tk.Label(weather_app, bg="#d0e7f9")
    icon_label.pack()

    result_label = tk.Label(weather_app, text="", font=("Helvetica", 12), bg="#d0e7f9", justify="left")
    result_label.pack(padx=20, pady=10, fill="both")

    forecast_title = tk.Label(weather_app, text="5-Day Forecast", font=("Helvetica", 14, "bold"), bg="#d0e7f9")
    forecast_title.pack(pady=5)

    forecast_label = tk.Label(weather_app, text="", font=("Helvetica", 11), bg="#d0e7f9", justify="left")
    forecast_label.pack(padx=20, fill="both")

    history_label = tk.Label(weather_app, text="Search History", font=("Helvetica", 14, "bold"), bg="#d0e7f9")
    history_label.pack(pady=10)

    history_frame = tk.Frame(weather_app, bg="#d0e7f9")
    history_frame.pack()

    history_listbox = tk.Listbox(history_frame, font=("Helvetica", 12), height=6, width=30)
    history_listbox.pack(side=tk.LEFT, padx=5)
    history_listbox.bind("<<ListboxSelect>>", on_history_select)

    clear_btn = tk.Button(history_frame, text="Clear History", bg="red", fg="white", command=clear_history)
    clear_btn.pack(side=tk.RIGHT, padx=5)

# --- HOME PAGE ---
home = tk.Tk()
home.title("Welcome Page")
home.geometry("400x400")
home.configure(bg="#40aff0")

welcome_label = tk.Label(home, text="Welcome to the Weather Forecast App ☀🌧", font=("Helvetica",20, "bold"), bg="#a2d5f2", wraplength=600, justify="center")
welcome_label.pack(pady=60)

launch_button = tk.Button(home, text="OPEN APP", font=("Helvetica",19), bg="#007acc", fg="white", command=launch_weather_app)
launch_button.pack(pady=20)

home.mainloop()
