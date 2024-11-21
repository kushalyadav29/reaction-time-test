import random

class Circle:
    def __init__(self, canvas, color='blue', moving=False, draggable=False):
        self.canvas = canvas
        self.radius = 20
        self.x = random.randint(self.radius, canvas.winfo_reqwidth() - self.radius)
        self.y = random.randint(self.radius, canvas.winfo_reqheight() - self.radius)
        self.color = color
        self.moving = moving
        self.draggable = draggable
        self.circle_id = canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius, fill=self.color)
        self.clicked = False
        self.path = []  # Initialize an empty path for the circle
        self.path_line = None  # Store the reference to the path line

    def is_clicked(self, event_x, event_y):
        distance = ((event_x - self.x) ** 2 + (event_y - self.y) ** 2) ** 0.5
        return distance <= self.radius

    def update_position(self, dx, dy):
        if self.moving:
            self.x += dx
            self.y += dy
            self.canvas.move(self.circle_id, dx, dy)

    def move_to(self, new_x, new_y):
        if self.draggable:
            dx = new_x - self.x
            dy = new_y - self.y
            self.x = new_x
            self.y = new_y
            self.canvas.move(self.circle_id, dx, dy)