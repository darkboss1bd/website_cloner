import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from urllib.parse import urljoin
import threading
import random

# Main Application Class
class WebsiteClonerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("darkboss1bd - Website Cloner")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="black")

        # Canvas for animation
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)

        # Banner Label
        self.banner_label = tk.Label(
            root,
            text="darkboss1bd",
            font=("Courier", 32, "bold"),
            fg="#00ff00",
            bg="black"
        )
        self.banner_label.place(relx=0.5, rely=0.1, anchor="center")

        # URL Entry
        self.url_label = tk.Label(
            root,
            text="Enter Website URL:",
            font=("Courier", 14),
            fg="white",
            bg="black"
        )
        self.url_label.place(relx=0.5, rely=0.3, anchor="center")

        self.url_entry = ttk.Entry(root, width=50, font=("Courier", 12))
        self.url_entry.place(relx=0.5, rely=0.4, anchor="center")

        # Clone Button
        self.clone_button = ttk.Button(
            root,
            text="Clone Website",
            command=self.start_cloning
        )
        self.clone_button.place(relx=0.5, rely=0.5, anchor="center")

        # Progress Bar
        self.progress = ttk.Progressbar(
            root,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.place(relx=0.5, rely=0.6, anchor="center")

        # Status Label
        self.status_label = tk.Label(
            root,
            text="Ready to clone...",
            font=("Courier", 10),
            fg="lightgreen",
            bg="black"
        )
        self.status_label.place(relx=0.5, rely=0.7, anchor="center")

        # Start animation
        self.animation_running = True
        self.animate_falling_code()

    def animate_falling_code(self):
        """Hacker-style falling code animation"""
        if not self.animation_running:
            return

        chars = "01 "  # Binary style
        x = random.randint(0, 800)
        y = 0
        speed = random.randint(5, 15)
        length = random.randint(10, 30)

        def fall():
            nonlocal y
            if y < 600:
                char = random.choice(chars)
                color = "green" if char == "1" else "#003300"
                self.canvas.create_text(x, y, text=char, fill=color, font=("Courier", 12))
                y += speed
                self.root.after(100, fall)
            else:
                self.canvas.delete("all")
                self.banner_label.lift()

        fall()
        self.root.after(100, self.animate_falling_code)

    def start_cloning(self):
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            url = "https://" + url

        if not url:
            messagebox.showerror("Error", "Please enter a valid URL!")
            return

        # Disable button
        self.clone_button.config(state="disabled")
        self.progress["value"] = 0
        self.status_label.config(text="Starting clone...")

        # Run in thread
        threading.Thread(target=self.clone_website, args=(url,), daemon=True).start()

    def clone_website(self, url):
        try:
            # Create folder
            parsed_url = urllib.parse.urlparse(url)
            folder_name = f"{parsed_url.netloc}_clone"
            os.makedirs(folder_name, exist_ok=True)

            # Download main page
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Save index.html
            with open(os.path.join(folder_name, "index.html"), "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            self.progress["value"] = 30
            self.status_label.config(text="Main page saved...")

            # Extract and download assets
            asset_tags = {
                "img": {"src": "jpg,jpeg,png,gif,webp"},
                "link": {"href": "css,ico"},
                "script": {"src": "js"}
            }

            downloaded = 0
            total_assets = 0

            # Count assets
            for tag, attrs in asset_tags.items():
                for attr, exts in attrs.items():
                    total_assets += len(soup.find_all(tag, {attr: True}))

            for tag, attrs in asset_tags.items():
                for attr, exts in attrs.items():
                    for element in soup.find_all(tag, {attr: True}):
                        asset_url = element[attr]
                        if not asset_url.startswith("http"):
                            asset_url = urljoin(url, asset_url)

                        try:
                            asset_response = requests.get(asset_url, headers=headers, timeout=10)
                            asset_response.raise_for_status()

                            # Extract filename
                            filename = os.path.basename(urllib.parse.urlparse(asset_url).path)
                            if not filename or "." not in filename:
                                continue

                            ext = filename.split(".")[-1].lower()
                            if ext not in exts.split(","):
                                continue

                            # Create subfolder
                            dir_name = tag if tag == "img" else "assets"
                            asset_folder = os.path.join(folder_name, dir_name)
                            os.makedirs(asset_folder, exist_ok=True)

                            # Save file
                            with open(os.path.join(asset_folder, filename), "wb") as af:
                                af.write(asset_response.content)

                            downloaded += 1
                            self.progress["value"] = 30 + int((downloaded / total_assets) * 70)
                            self.root.after(1, lambda: self.status_label.config(text=f"Downloaded: {filename}"))

                        except Exception as e:
                            print(f"Failed to download {asset_url}: {e}")
                            continue

            self.status_label.config(text="Website cloned successfully!")
            messagebox.showinfo("Success", f"Website cloned to folder: {folder_name}")

        except Exception as e:
            self.status_label.config(text="Error occurred!")
            messagebox.showerror("Error", str(e))

        finally:
            self.clone_button.config(state="normal")

    def on_closing(self):
        self.animation_running = False
        self.root.destroy()


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = WebsiteClonerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()