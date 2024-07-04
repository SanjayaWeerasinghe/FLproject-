
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Define a function to generate random data for plotting
def generate_random_data(iterations, num_labels):
    data = np.random.rand(iterations, num_labels)
    return data

# Create a Tkinter window
root = tk.Tk()
root.title("Random Data Plot")

# Create a frame for the plot
plot_frame = ttk.Frame(root)
plot_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Generate random data for demonstration
iterations = 100
num_labels = 10
random_data = generate_random_data(iterations, num_labels)

# Create a Matplotlib figure and plot the data
fig = Figure(figsize=(10, 6))
ax = fig.add_subplot(111)

for j in range(num_labels):
    ax.plot(range(iterations), random_data[:, j], label='Label {}'.format(j))

ax.set_xlabel('Iteration count')
ax.set_ylabel('Random Data')
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
canvas.draw()

# Start the Tkinter main loop
root.mainloop()
