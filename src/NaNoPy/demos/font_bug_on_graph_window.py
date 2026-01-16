# source: https://gitlab.tudelft.nl/nb1420_2025/individual/jelle-jpheij/-/blob/main/Final_project/Testing.py?ref_type=heads
from NaNoPy import *
import random as rnd

# Set up the screen, a title and the size
xsize_screen, ysize_screen = 800, 600
height_legend = ysize_screen/12

xsize_graphs = 250
ysize_graphs = 400
xstart_graph = 50
ystart_graph = 250

graph_screen = Canvas("Graphs", xsize_graphs, ysize_graphs, xpos=xstart_graph, ypos=ystart_graph)
graph_pen = Writer(graph_screen)

screen = Canvas("Quorum sensing in a biofilm", xsize_screen, ysize_screen)
pen = Writer(screen)

number_rows, number_columns = 8, 8
number_nutrients = 300

# Constants for the simulated biofilm
xfilm, yfilm = xsize_screen/8, (ysize_screen-height_legend)/8 + 0.5*height_legend
width_film, height_film = 3*xsize_screen/4, 3*ysize_screen/4
color_film = color().white

healthy_color = color().white
starving_color = color().red
dead_color = color().cyan
repolarization_color = color().blue

free_nutrient_color = color().green
taken_up_nutrient_color = color().gray

calcium_color_trapped = color().custom(r=255, g=165, b=0) # orange
calcium_color_free = color().magenta

width_cells = width_film / number_columns
height_cells = height_film / number_rows

cells = []
nutrients = []
amount_calcium_per_cell = 15

nutrient_radius = 3
nutrient_speed = 2
nutrient_flow = 2

speed_calcium_trapped = 1
speed_calcium_free = 2
radius_calcium = 1
depolarization_time = 250
dead_time = 750

total_amount_dead = 0
total_amount_starving = 0
total_amount_healthy = 0

degrade_chance = 0.0005
depolarization_chance = 0.005
dead_chance = 0.0005
take_up_chance = 0.01
lose_nutrient_chance = 0.5
take_up_chance_calc = 0.025
release_calcium_chance = 0.10

percentage_quorum_sensing = 100

class Cell:
    def __init__(self, row, column, quorum):
        self.color_states = {"healthy": healthy_color, "starving": starving_color, 
                        "dead": dead_color, "repolarization":repolarization_color}
        xmin = row*width_cells + xfilm
        xmax = xmin + width_cells - 0.2*(xfilm/width_cells)
        ymin = column*height_cells + yfilm
        ymax = ymin + height_cells - 0.2*(yfilm/height_cells)
        self.area = (xmin, ymin, xmax, ymax)
        self.nutrients_taken_up = set()
        self.quorum = quorum

        self.calcium_ions = []
        self.depolarization_timer = 0
        self.dead_timer = 0
        self.dead = False

    def draw(self):
        (xmin, ymin, xmax, ymax) = self.area
        color_cell = self.color_states[self.state]

        if self.polarization == "repolarization":
            color_cell = self.color_states["repolarization"]

        pen.draw_rectangle(xmin, ymin, (xmax-xmin), (ymax-ymin), color_cell, False)


    def update(self):
        self.degrade_nutrient()
        self.update_timer()

    @property
    def state(self):
        if self.dead:
            #total_amount_dead += 1
            return "dead"
        if len(self.nutrients_taken_up) > 0:
            #total_amount_healthy += 1
            return "healthy"
            
        else:
            #total_amount_starving += 1
            return "starving"

        
    @property
    def polarization(self):
        for calc_ion in self.calcium_ions:
            if calc_ion.state != "trapped":
                return "repolarization"
        
        return "polarized"

    def degrade_nutrient(self):
        for nutrient in list(self.nutrients_taken_up):
            nutrient_chance = rnd.random()
            if nutrient_chance < degrade_chance:
                nutrient.xpos = 0
                nutrient.ypos = rnd.uniform(0, ysize_screen)
                nutrient.release()
                self.nutrients_taken_up.remove(nutrient)

    def update_timer(self):
        if self.polarization != "repolarization" and self.state != "dead":
            self.depolarization_timer += 1
        if len(self.nutrients_taken_up) == 0:
            self.dead_timer += 1

    def take_up_nutrient(self, nutrient):
        self.nutrients_taken_up.add(nutrient)

    def depolarize(self):
        if self.state == "starving" and self.quorum is True:
            depolarization_cell = rnd.random()
            if depolarization_cell < depolarization_chance and self.depolarization_timer > depolarization_time:
                for calcium_ion in self.calcium_ions:
                    calcium_ion.release()

    def calcium_induced_release(self, calc_ion):
        (xmincell, ymincell, xmaxcell, ymaxcell) = self.area
        if xmincell<=calc_ion.xpos<=xmaxcell and ymincell<=calc_ion.ypos<=ymaxcell and calc_ion not in self.calcium_ions:
            if self.state != "dead" and self.polarization != "repolarization":
                if self.depolarization_timer > depolarization_time and self.quorum is True:
                    for calcium_ion in self.calcium_ions:
                        calcium_ion.release()
    
                    self.nutrient_induced_release()
                    self.depolarization_timer = 0

    def nutrient_induced_release(self):
        lose_nutrient_cell = rnd.random()
        if lose_nutrient_cell < lose_nutrient_chance:
            for nutrient in self.nutrients_taken_up:
                nutrient.release()
            self.nutrients_taken_up = set()

    def die(self):
        if len(self.nutrients_taken_up) == 0 and self.dead_timer > dead_time:
            dead_cell_chance = rnd.random()
            if dead_cell_chance < dead_chance:
                self.dead = True
                for calcium_ion in self.calcium_ions:
                    del calcium_ion
                
                self.calcium_ions.clear()

class Nutrient:
    def __init__(self, radius, speed, flow):
        self.speed = speed
        self.flow = flow
        self.radius = radius

        self.xpos = rnd.uniform(0, 0)
        self.ypos = rnd.uniform(0, ysize_screen)
        self.area = (0, 0, xsize_screen, ysize_screen) # (xmin, ymin, xmax, ymax)
        self.state = "free"

        self.color_states = {"free": free_nutrient_color, "trapped":taken_up_nutrient_color}

    def move(self):
        (xmin, ymin, xmax, ymax) = self.area
        dx = rnd.randint(-self.speed, self.speed)
        dy = rnd.randint(-self.speed, self.speed)

        if self.state == "free":
            if self.xpos+dx+self.flow >= xmax:
                self.xpos = 0
                self.ypos = rnd.uniform(0, ysize_screen)
            if self.xpos+dx+self.flow > xmin:
                self.xpos += (dx + self.flow)
            if ymax > self.ypos+dy > ymin:
                self.ypos += dy
            
        elif self.state == "trapped":
            if xmax > self.xpos+dx > xmin:
                self.xpos += dx
            if ymax > self.ypos+dy > ymin:
                self.ypos += dy

    def draw(self):
        color_nutrient = self.color_states[self.state]
        pen.draw_circle(self.xpos, self.ypos, self.radius, color_nutrient, True)

    def take_up(self, cells):
        for cell in cells:
            (xmincell, ymincell, xmaxcell, ymaxcell) = cell.area
            if xmincell <= self.xpos <= xmaxcell and ymincell <= self.ypos <= ymaxcell and cell.dead != True:
                take_up_nutrient = rnd.random()
                if take_up_nutrient < take_up_chance:
                    self.state = "trapped"
                    self.area = cell.area
                    cell.take_up_nutrient(self)

    def release(self):
        self.state = "free"
        self.area = (0, 0, xsize_screen, ysize_screen)
        
class Calcium:
    def __init__(self, xmincell, ymincell, xmaxcell, ymaxcell, speed_trapped, speed_free, radius):
        self.xpos = rnd.uniform(xmincell, xmaxcell)
        self.ypos = rnd.uniform(ymincell, ymaxcell)

        self.area_cell = (xmincell, ymincell, xmaxcell, ymaxcell)

        self.radius = radius
        self.speed_trapped = speed_trapped
        self.speed_free = speed_free
        self.state = "trapped"
        self.color_states = {"free": calcium_color_free, "trapped":calcium_color_trapped}
    
    def move(self):
        if self.state == "free":
            dx = rnd.randint(-self.speed_free, self.speed_free)
            dy = rnd.randint(-self.speed_free, self.speed_free)
            if xfilm < self.xpos+dx < xfilm+width_film:
                self.xpos += dx
            if yfilm < self.ypos+dy < yfilm+height_film:
                self.ypos += dy    
            self.take_up()

        elif self.state == "trapped":
            dx = rnd.randint(-self.speed_trapped, self.speed_trapped)
            dy = rnd.randint(-self.speed_trapped, self.speed_trapped)
            (xmin, ymin, xmax, ymax) = self.area_cell
            if xmin < self.xpos+dx < xmax:
                self.xpos += dx
            if ymin < self.ypos+dy < ymax:
                self.ypos += dy

    def draw(self):
        color_particle = self.color_states[self.state]
        pen.draw_circle(self.xpos, self.ypos, self.radius, color_particle, True)

    def take_up(self):
        taking_up_calcium = rnd.random()
        if self.state == "free" and taking_up_calcium <= take_up_chance_calc:
            self.state = "trapped"
            (xmincell, ymincell, xmaxcell, ymaxcell) = self.area_cell
            self.xpos = rnd.uniform(xmincell, xmaxcell)
            self.ypos = rnd.uniform(ymincell, ymaxcell)

    def release(self):
        if self.state == "trapped":
            self.state = "free"

def create_cells(rows, columns, percentage_quorum_sensing):
    for column in range(columns):
        for row in range(rows):
            cell = Cell(row, column, False)
            cells.append(cell)

    amount_quorum_cells = percentage_quorum_sensing/100 * (rows*columns)
    current_amount = 0

    while current_amount < amount_quorum_cells:
        n = rnd.randint(0, len(cells) - 1)
        if cells[n].quorum != True:
            cells[n].quorum = True
            current_amount += 1

def fill_cells_calcium():
    for cell in cells:
        (xmincell, ymincell, xmaxcell, ymaxcell) = cell.area
        for _ in range(amount_calcium_per_cell):
            calcium_ion = Calcium(xmincell, ymincell, xmaxcell, ymaxcell, speed_calcium_trapped, speed_calcium_free, radius_calcium)
            cell.calcium_ions.append(calcium_ion)

def initialize(rows, columns, number_nutrients):
    create_cells(rows, columns, percentage_quorum_sensing)
    fill_cells_calcium()

    for _ in range(number_nutrients):
        nutrient = Nutrient(nutrient_radius, nutrient_speed, nutrient_flow)
        nutrients.append(nutrient)

def draw_everything():
    for cell in cells:
        cell.draw()
        for calcium_ion in cell.calcium_ions:
            calcium_ion.draw()

    for nutrient in nutrients:
        nutrient.draw()
    
    # Now also draw a legend
    create_legend()
    
def create_legend():
    # Start with a black box
    pen.draw_rectangle(0, 0, xsize_screen, height_legend, color().custom(r=0, g=0, b=0), True)
    pen.draw_rectangle(0, 0, xsize_screen, height_legend, color().white, False)

    # free nutrient
    pen.draw_circle(10, 3*height_legend/4, nutrient_radius, free_nutrient_color, True)
    pen.draw_string(25, 3*height_legend/4 + 3, color().white, "Free nutrient")

    # trapped nutrient
    pen.draw_circle(10, height_legend/3, nutrient_radius, taken_up_nutrient_color, True)
    pen.draw_string(25, height_legend/3 + 3, color().white, "Taken up nutrient")

    # free calcium
    pen.draw_circle(10 + xsize_screen/4, 3*height_legend/4, nutrient_radius, calcium_color_free, True)
    pen.draw_string(25 + xsize_screen/4, 3*height_legend/4 + 3, color().white, "Free calcium")

    # trapped calcium
    pen.draw_circle(10 + xsize_screen/4, height_legend/3, nutrient_radius, calcium_color_trapped, True)
    pen.draw_string(25 + xsize_screen/4, height_legend/3 + 3, color().white, "Trapped calcium")

    # Healthy cell
    pen.draw_rectangle(2*xsize_screen/4 - 10, 3*height_legend/4-10, 2*width_cells/7, 2*height_cells/7, healthy_color, False)
    pen.draw_string(25 + 2*xsize_screen/4, 3*height_legend/4 + 3, color().white, "Healthy cell")

    # Starving cell 
    pen.draw_rectangle(2*xsize_screen/4 - 10, height_legend/4-8, 2*width_cells/7, 2*height_cells/7, starving_color, False)
    pen.draw_string(25 + 2*xsize_screen/4, height_legend/4 + 5, color().white, "Starving cell")

    # Repolarization cell
    pen.draw_rectangle(3*xsize_screen/4 - 10, 3*height_legend/4-10, 2*width_cells/7, 2*height_cells/7, repolarization_color, False)
    pen.draw_string(25 + 3*xsize_screen/4, 3*height_legend/4 + 3, color().white, "Repolarization cell")

    # Dead cell
    pen.draw_rectangle(3*xsize_screen/4 - 10, height_legend/4-8, 2*width_cells/7, 2*height_cells/7, dead_color, False)
    pen.draw_string(25 + 3*xsize_screen/4, height_legend/4 + 5, color().white, "Dead cell")

def create_graphs(height_graph, origin_x, origin_y, width_bar):
    height_dead = total_amount_dead/(number_rows*number_columns)*height_graph
    height_starving = total_amount_starving/(number_rows*number_columns)*height_graph
    height_healthy = total_amount_healthy/(number_rows*number_columns)*height_graph
    graph_pen.draw_string(10, 10, color().white, "Dead")
    graph_pen.draw_string(origin_x+width_bar, 100, color().white, "Starving")
    graph_pen.draw_string(origin_x+2*width_bar, 100, color().white, "Healthy")

    graph_pen.draw_rectangle(origin_x, origin_y, width_bar, height_dead, dead_color, True)
    graph_pen.draw_rectangle(origin_x+width_bar, origin_y, width_bar, height_starving, starving_color, True)
    graph_pen.draw_rectangle(origin_x+2*width_bar, origin_y, width_bar, height_healthy, healthy_color, True)


initialize(number_rows, number_columns, number_nutrients)

while screen.running():

    total_amount_dead = 0
    total_amount_starving = 0
    total_amount_healthy = 0

    # move all the particles
    for nutrient in nutrients:
        nutrient.move()
        nutrient.take_up(cells)

    for cell in cells:
        for calc_ion in cell.calcium_ions:
            calc_ion.move()
            for cell in cells:
                cell.calcium_induced_release(calc_ion)


    for cell in cells:
        cell.depolarize()
        cell.die()
        cell.update()

        if cell.dead:
            total_amount_dead += 1
        if len(cell.nutrients_taken_up) > 0:
            total_amount_healthy += 1
        if len(cell.nutrients_taken_up) == 0:
            total_amount_starving += 1

    # Draw everything
    draw_everything()
    create_graphs(3*ysize_graphs/4, xsize_graphs/6, ysize_graphs/12, xsize_graphs/4)

    screen.update()
    screen.clear()
    screen.pause(5)

    graph_screen.update()
    graph_screen.pause(5)
    graph_screen.clear()


### TODO: graphs for the simulation