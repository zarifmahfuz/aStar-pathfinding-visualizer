# Author: Zarif Mahfuz

import pygame
import tkinter as tk
from tkinter import font

width = 800
height = 800
pygame.init()
win = pygame.display.set_mode((width, height))

# want a 2-dimensional array that can store information for every spot on the grid
cols = 50
rows = 50
w = 15 # width of each square
h = 15 # height of each square
margin = 1

def heuristic(a, b):
	# MANHATTAN DISTANCE
	d = abs(a.x-b.x) + abs(a.y-b.y)
	return d

class Spot:
	def __init__(self, i, j):
		self.x = i
		self.y = j
		self.f = 0
		self.g = 0
		self.h = 0
		self.neighbours = [] # each spot keeps track of its neighbours
		self.previous = None
		# By default, every spot is not an obstacle
		self.obstacle = False

	
	def show(self, color):
		if self.obstacle:
			color = (0,0,0)
			
		pygame.draw.rect(win, color, (self.y*(w+margin), self.x*(h+margin), w, h))
		pygame.display.update()

	
	def addNeighbours(self, grid): 
		i = self.x
		j = self.y
		if i<(rows-1): # bottom neighbour
			self.neighbours.append(grid[i+1][j])
		
		if i>0: # top neighbour
			self.neighbours.append(grid[i-1][j])
		
		if j<(cols-1): # right neighbour
			self.neighbours.append(grid[i][j+1])
		
		if j>0: # left neighbour
			self.neighbours.append(grid[i][j-1])
		
		if i>0 and j>0: # top-left neighbour
			self.neighbours.append(grid[i-1][j-1])
		
		if i>0 and j<(cols-1): # top-right neighbour
			self.neighbours.append(grid[i-1][j+1])
		
		if i<(rows-1) and j>0: # bottom-left neighbour
			self.neighbours.append(grid[i+1][j-1])
		
		if i<(rows-1) and j<(cols-1): # bottom-right neighbour
			self.neighbours.append(grid[i+1][j+1])


# BUILDING GRID
grid = []
for i in range(rows):
	# For each row create a list that will represent an entire row
	grid.append([])
	for j in range(cols):
		# Instantiate an object of the class Spot for each spot in the grid
		grid[i].append(Spot(i, j))

# add neighbours for each spot 
for i in range(rows):
	for j in range(cols):
		grid[i][j].addNeighbours(grid)
		
# DRAW THE GRID 
for column in range(cols):
		for row in range(rows):
			grid[row][column].show((255,255,255))

	
# GUI
start_coords = []
end_coords = []

# get_coords function obtains the starting and ending coordinates entered by the user
def get_coords(start_entry, end_entry, master):
	str1 = start_entry.get()
	str2 = end_entry.get()
	
	global start_coords
	start_coords.extend(list(map(int, str1.split(","))))
	global end_coords
	end_coords.extend(list(map(int, str2.split(","))))

	# exit out of the GUI window
	master.quit()
	master.destroy()

root = tk.Tk()
HEIGHT = 200
WIDTH = 300

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

start_label = tk.Label(root, text="Start (x, y):", font=("Mordern", 10), anchor='nw', justify='left')
start_label.place(relx=0.1, rely=0.1, relwidth=0.3, relheight=0.2)

start_entry = tk.Entry(root, font=("Mordern", 10))
start_entry.place(relx=0.4, rely=0.1, relwidth=0.4, relheight=0.15)

end_label = tk.Label(root, text="End (x, y): ", font=("Mordern", 10), anchor='nw', justify='left')
end_label.place(relx=0.1, rely=0.4, relwidth=0.3, relheight=0.2)

end_entry = tk.Entry(root, font=("Mordern",10))
end_entry.place(relx=0.4, rely=0.4, relwidth=0.4, relheight=0.15)

state = tk.IntVar()
tickbox = tk.Checkbutton(root, text="Show steps", font=("Mordern", 10), onvalue=1, offvalue=0, variable=state)
tickbox.place(relx=0.1, rely=0.75)

button = tk.Button(root, text="Submit", command=lambda: get_coords(start_entry, end_entry, root))
button.place(relx=0.7, rely=0.75, relwidth=0.25, relheight=0.15, anchor='n')

root.mainloop() 

tick = state.get() # state of the tickbox

# mark the starting and the ending coordinates with light blue 
start = grid[start_coords[0]][start_coords[1]]
end = grid[end_coords[0]][end_coords[1]]
start.show((0,255,255)) 
end.show((0,255,255))

# obstacles set by the user by clicking and dragging the mouse
def mouse_pressed(coords): 
	x = coords[0]
	y = coords[1]
	anchorX = y // (800//rows)
	anchorY = x // (800//cols)
	
	global grid
	grid[anchorX][anchorY].obstacle = True
	grid[anchorX][anchorY].show((0,0,0))
	


run1 = True
while run1:
	pygame.time.delay(1)

	for event in pygame.event.get():
		if pygame.mouse.get_pressed()[0]:
			coords = pygame.mouse.get_pos()
			mouse_pressed(coords)

		# after the user sets obstacles, the program proceeds when the user presses the spacebar
		elif pygame.key.get_pressed()[pygame.K_SPACE]:
			run1 = False


# implementation of the A* pathfinding algorithm begins here
openSet = [start]
closedSet = []
optimal_path = []

def aStar():
	
	if len(openSet)>0:
		incomplete = True
		winner = 0 # assume the element with lowest f is the first element in the openSet(i.e. winner)
		for i in range(len(openSet)):
			if (openSet[i].f<openSet[winner].f):
				winner = i

		# current is the node in the openSet that has the lowest f
		current = openSet[winner]
		if current==end:
			# find the optimal path; traceback
			temp = current
			optimal_path.append(temp)
			while (temp.previous!=None):
				optimal_path.append(temp.previous)
				temp = temp.previous
			incomplete = False
			print("Shortest path has been found!")
		

		if incomplete:
			# current is the node we're moving into next; so we have to mark it off the openSet and add it to closedSet
			closedSet.append(current)
			del openSet[winner]

			neighbours = current.neighbours
			# now analyze every neighbour
			for i in range(len(neighbours)):
				
				every_neighbour = neighbours[i]
				updatePath = False
				
				# if the neighbour has not been evaluated and put in the closedSet AND it is not an obstacle
				if not(closedSet.count(every_neighbour)>0) and not(every_neighbour.obstacle): 
					tempG = current.g + 1
					# we need to check if we had evaluated that node before but not put in the closedSet
					# if this is the case we might've gotten to that node with a lower g; check for that
					if openSet.count(every_neighbour)>0:
						if tempG<every_neighbour.g:
							every_neighbour.g = tempG
							updatePath = True
					else:
						every_neighbour.g = tempG
						# it's not yet in the openSet because it was not evaluated before; need to put it there
						openSet.append(every_neighbour)
						updatePath = True
					# only need to update the information of neighbours if we have a better g or evaluated first time
					if updatePath:
						every_neighbour.h = heuristic(every_neighbour, end)
						every_neighbour.f = every_neighbour.g + every_neighbour.h
						every_neighbour.previous = current 


	if tick==1:
		# closedSet is RED
		for i in range(len(closedSet)):
			closedSet[i].show((255,0,0))

		# openSet is GREEN
		for i in range(len(openSet)):
			openSet[i].show((0,255,0))

	# optimal_path is BLUE
	for i in range(len(optimal_path)):
		optimal_path[i].show((0,0,255))

	if len(openSet)==0 and current!=end:
		return 2
	elif incomplete:
		return 0
	else: return 1

notDone = aStar()
while notDone==0:
	notDone = aStar()
if notDone==2: print("No path can be found!")


# pygame 'main loop'
run2 = True
while run2:
	pygame.time.delay(10)

	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			run2 = False
	
pygame.quit()
