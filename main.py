import pandas as pd
import tkinter as tk
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os
import numpy as np
from Game_sequence import Game_sequence

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Aim labs")
        self.root.geometry("400x400")
        
        self.root.iconbitmap('icon.ico')
        
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.circles = []
        self.path_circles = []
        self.total_clicks = 0
        self.successful_clicks = 0
        self.start_time = 0
        self.end_time = 0
        self.game_started = False
        self.remaining_time = 15
        self.current_game_time = 0  # Track time for each game sequence

        self.results = []
        self.regions = {
                "top_left": (0, 0, 133, 133),
                "top_center": (134, 0, 267, 133),
                "top_right": (268, 0, 400, 133),
                "center_left": (0, 134, 133, 267),
                "center_center": (134, 134, 267, 267),
                "center_right": (268, 134, 400, 267),
                "bottom_left": (0, 268, 133, 400),
                "bottom_center": (134, 268, 267, 400),
                "bottom_right": (268, 268, 400, 400),
            }


        self.region_accuracies = {region: 0 for region in self.regions}

        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        self.start_game_button = tk.Button(frame, text="Start Game", bg="green", command=self.start_game)
        self.start_game_button.pack()

        self.previous_results_button = tk.Button(root, text="Previous Results", bg="green", command=self.show_previous_results)
        self.reset_game_button = tk.Button(root, text="Restart Game", bg="green", command=self.reset_game)
        self.previous_results = []

        root.bind("<Configure>", self.handle_resize)

        self.game_sequence = Game_sequence(self)

    def handle_resize(self, event):
        canvas_width = event.width
        canvas_height = event.height

        if self.canvas:
            try:
                # Update canvas size
                self.canvas.configure(width=canvas_width, height=canvas_height)

                # Calculate region boundaries based on the current canvas dimensions
                region_width = canvas_width // 3
                region_height = canvas_height // 3

                self.regions = {
                    "top_left": (0, 0, region_width, region_height),
                    "top_center": (region_width, 0, 2 * region_width, region_height),
                    "top_right": (2 * region_width, 0, canvas_width, region_height),
                    "center_left": (0, region_height, region_width, 2 * region_height),
                    "center_center": (region_width, region_height, 2 * region_width, 2 * region_height),
                    "center_right": (2 * region_width, region_height, canvas_width, 2 * region_height),
                    "bottom_left": (0, 2 * region_height, region_width, canvas_height),
                    "bottom_center": (region_width, 2 * region_height, 2 * region_width, canvas_height),
                    "bottom_right": (2 * region_width, 2 * region_height, canvas_width, canvas_height),
                }

                # Redraw the circles in their respective regions
                self.redraw_circles_in_regions()

            except:
                pass

    def start_game(self):
        if not self.game_started:
            self.game_started = True
            self.total_clicks = 0
            self.successful_clicks = 0
            self.start_time = time.time()
            self.game_sequence.current_pointer = 0
            self.current_game_time = 0  # Reset current game time

            # Create a new canvas
            if self.canvas:
                self.canvas.destroy()
            self.canvas = tk.Canvas(self.root, width=400, height=400)
            self.canvas.pack()

            self.start_game_button.destroy()
            self.game_sequence.run_game_sequence()

            # Schedule the end_game function to run after the game sequence
            self.root.after(self.game_sequence.game_sequence_duration * 1000 * len(self.game_sequence.games), self.end_game)

    def calculate_accuracy(self):
        if self.total_clicks == 0:
            return 0
        return (self.successful_clicks / self.total_clicks) * 100

    # Modify the show_previous_results method

    def save_results_to_csv(self):
        # Check if the CSV file exists
        file_exists = os.path.isfile('game_result.csv')

        # Open the CSV file in append mode
        with open('game_result.csv', mode="a", newline="") as file:
            fieldnames = ["Successful Clicks", "Total Clicks", "Accuracy"] + list(self.regions.keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # If the file doesn't exist, write headers
            if not file_exists:
                writer.writeheader()

            # Calculate average region accuracies
            region_accuracies = {region: 0 for region in self.regions}
            num_games = len(self.results)

            for result in self.results:
                for region, data in result["Region Accuracies"].items():
                    region_accuracies[region] += data


            # Write data to the CSV file
            writer.writerow({
                "Successful Clicks": self.successful_clicks,
                "Total Clicks": self.total_clicks,
                "Accuracy": self.calculate_accuracy(),
                **region_accuracies
            })


    def end_game(self):
    # At the end of a game sequence, create a dictionary to store results
        game_result = {
            "Successful Clicks": self.successful_clicks,
            "Total Clicks": self.total_clicks,
            "Accuracy": self.calculate_accuracy(),
        }

        # Append the game result to self.results
        self.results.append(game_result)

        self.end_time = time.time()
        self.current_game_time += int(self.end_time - self.start_time)  # Update current game time
        self.game_started = False

        # Check if there are any results in self.results
        if self.results:
            # Calculate region accuracies
            region_accuracies = {}
            for region, data in self.region_accuracies.items():
                    region_accuracies[region] = data

            # Save the updated region accuracies
            self.results[-1]["Region Accuracies"] = region_accuracies
            # Save results to CSV
            self.save_results_to_csv()
        
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()

        labels = ['Successful Clicks', 'Accuracy'] + list(self.region_accuracies.keys())
        values = [self.successful_clicks, self.calculate_accuracy()] +list(i *5 for i in self.region_accuracies.values())
        fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(canvas_width // 120, canvas_height // 120))
        ax.fill_between(range(len(labels)), values)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)

        canvas = FigureCanvasTkAgg(fig, master=self.canvas)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Add buttons for resetting the game and showing previous results
        reset_button = tk.Button(self.canvas, text="Reset Game", bg="green", command=self.reset_game)
        results_button = tk.Button(self.canvas, text="Show Previous Results", bg="green", command=self.show_previous_results)
        reset_button.grid(row=1, column=0, sticky="ew")
        results_button.grid(row=1, column=1, sticky="ew")

        self.previous_results_button.pack_forget()
        self.reset_game_button.pack_forget()
        self.root.update_idletasks()



    def show_previous_results(self):
        self.display_radar_graph("Previous Results")
        reset_button = tk.Button(self.canvas, text="Reset Game", bg="green", command=self.reset_game)

    def reset_game(self):
        self.canvas.destroy()
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.reset_button.pack()
        self.previous_results_button.pack()
        self.root.update_idletasks()

    def display_radar_graph(self, title):
        # Load data from the CSV file into a DataFrame
        df = pd.read_csv('game_result.csv')

        # Calculate the column-wise averages
        column_averages = df.mean()  # This calculates the mean for each column

        # Create a list of labels and values for plotting
        labels = list(column_averages.index)
        values = list(column_averages.values)

        # Check if the number of labels matches the number of values
        if len(labels) != len(values):
            raise ValueError("Number of labels does not match the number of values.")
            
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()

        # Create a radar chart
        fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(canvas_width // 120, canvas_height // 120))
        ax.fill_between(range(len(labels)), values)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)

        canvas = FigureCanvasTkAgg(fig, master=self.canvas)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def reset_game(self):
        self.game_started = False
        self.total_clicks = 0
        self.successful_clicks = 0
        self.results = []
        if self.canvas:
            self.canvas.destroy()
        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        self.start_game_button = tk.Button(frame, text="Start Game", bg="green", command=self.start_game)
        self.start_game_button.pack()



root = tk.Tk()
game = Game(root)
root.mainloop()
