from Circle import Circle
import random
import time
class Game_sequence:
    def __init__(self, game):
        self.game = game
        self.canvas = self.game.canvas
        self.games = ['single circle', 'multiple circles', 'moving circles']
        self.sequence = []
        self.ch_game_sequence()
        self.current_pointer = 0
        self.game_sequence_duration = 15  # 5 seconds for each game
        self.moving_circles = []

    def ch_game_sequence(self):
        random.shuffle(self.games)

    def run_game_sequence(self):
        if self.current_pointer < len(self.games):
            game_name = self.games[self.current_pointer]
            self.start_game_sequence(game_name)
        else:
            # Schedule showing the end game screen with a delay
            game_result = {
    "Successful Clicks": self.game.successful_clicks,
    "Total Clicks": self.game.total_clicks,
    "Accuracy": self.game.calculate_accuracy(),
    "Region Accuracies": {}  # You can fill this in with region-specific data
        }

# Append the game result to self.results
            self.game.results.append(game_result)
            self.game.canvas.after(self.game_sequence_duration * 1000, self.game.end_game)

    def start_game_sequence(self, game_name):
        # Remove old circles and path lines
        for circle in self.game.circles:
            self.game.canvas.delete(circle.circle_id)

        self.game.circles = []

        # Start the specified game sequence
        if game_name == 'single circle':
            self.single_circle()
        elif game_name == 'multiple circles':
            self.multiple_circle()
        elif game_name == 'moving circles':
            self.moving_circle()
#         

        # Set the game start time
        self.game_start_time = time.time()

        # Schedule the next game sequence or end the game
        self.current_pointer += 1
        if self.current_pointer < len(self.games):
            self.game.canvas.after(self.game_sequence_duration * 1000, self.run_game_sequence)

    def single_circle(self):
        self.spawn_circle()

    def multiple_circle(self):
        self.spawn_multiple_circle()

    def moving_circle(self):
        self.start_moving_circles()
        
    def spawn_circle(self, circle_type=None):
        if self.game.game_started and self.game.remaining_time > 0:
            canvas_width = self.game.canvas.winfo_width()
            canvas_height = self.game.canvas.winfo_height()

            if circle_type == "moving":
                # Create a regular moving circle
                circle = Circle(self.game.canvas, moving=True) # Call the method to create a path circle
            else:
                circle = Circle(self.game.canvas, moving=False)
                  # Call the method to create a path circle

            circle.canvas.tag_bind(circle.circle_id, "<Button-1>", lambda event, circle=circle: self.click_circle(event, circle))
            self.game.circles.append(circle)

    def click_circle(self, event, circle):
        if self.game.game_started and self.game.remaining_time > 0:
            if circle.clicked:
                return  # Ignore additional clicks while the circle is already clicked

            circle.clicked = True
            self.game.total_clicks += 1

            for region, region_coords in self.game.regions.items():
                if region_coords[0] <= event.x <= region_coords[2] and region_coords[1] <= event.y <= region_coords[3]:
                    self.game.region_accuracies[region] += 1 if circle.is_clicked(event.x, event.y) else 0

            if circle.is_clicked(event.x, event.y):
                self.game.successful_clicks += 1

            self.game.canvas.delete(circle.circle_id)
            self.game.circles.remove(circle)
            self.spawn_circle()


    def spawn_multiple_circle(self):
        if self.game.game_started and self.game.remaining_time > 0:
            for _ in range(3):
                canvas_width = self.game.canvas.winfo_width()
                canvas_height = self.game.canvas.winfo_height()
                circle = Circle(self.game.canvas)
                circle.canvas.tag_bind(circle.circle_id, "<Button-1>", lambda event, circle=circle: self.click_circle(event, circle))
                self.game.circles.append(circle)

    def start_moving_circles(self):
        # Create and start moving circles
        for _ in range(3):  # You can adjust the number of moving circles
            circle = Circle(self.game.canvas, moving=True)
            circle.canvas.tag_bind(circle.circle_id, "<Button-1>", lambda event, circle=circle: self.click_circle(event, circle))
            self.game.circles.append(circle)

        # Schedule the position update function
        self.update_moving_circle_positions()

    def update_moving_circle_positions(self):
        if self.game.game_started and self.game.remaining_time > 0:
            for circle in self.game.circles:
                # Generate random motion direction
                dx, dy = random.choice([(0, -7), (0, 7), (-7, 0), (7, 0)])  # Up, down, left, right

                # Check if the circle is about to move outside the canvas boundaries
                new_x = circle.x + dx
                new_y = circle.y + dy
                if 0 <= new_x - 2 * circle.radius <= self.game.canvas.winfo_reqwidth() and 0 <= new_y - 2 * circle.radius <= self.game.canvas.winfo_reqheight():
                    # Update circle position
                    circle.update_position(dx, dy)
                else:
                    # If hitting the canvas boundary, bounce back in the opposite direction
                    circle.update_position(-dx, -dy)

            # Schedule the next position update
            self.game.canvas.after(500, self.update_moving_circle_positions)

