"""
Author      : Rasha Boura
PI          : Dr. Sampson Akwafuo
File Name   : Lassa_model.py
Date        : August 1st, 2022
"""



from mesa import Agent, Model
from mesa.time import RandomActivation 
from mesa.space import MultiGrid 
from mesa.datacollection import DataCollector


import random
import math
import sys

class superAgent(Agent):

    def __init__(self, unique_id, model, init_infection, transmissibility, level_of_movement, 
    contagious_period, accessible_treatment, ribavirin_availability, socioeconomic_level_of_human, is_human):
        # Takes cares of the background stuff needed to create a Mesa 'Agent'
        super().__init__(unique_id, model)


        # Theses parameters define the attributes that make up a human agent
        if is_human:
            self.hum_init_infection         = init_infection
            self.h2h_transmissibility       = transmissibility
            self.level_of_hum_movement      = level_of_movement
            self.contagious_period_hum      = contagious_period
            self.accessible_treatment       = accessible_treatment
            self.ribavirin_availability     = ribavirin_availability
            self.socioeconomic_level_of_human = socioeconomic_level_of_human
            self.is_human                   = True
            self.treated                    = False
            self.secondary_transmission_h2h = 0
            self.test_group                 = False
            self.isolate_group              = False
        # Theses parameters define the attributes that make up a rat agent
        else:
            self.rat_init_infection         = init_infection
            self.r2h_transmissibility       = transmissibility
            self.contagious_period_rat      = contagious_period
            self.level_of_rat_movement      = level_of_movement
            self.is_human                   = False
            self.secondary_transmission_r2h = 0            
            self.accessible_treatment       = 0
            self.ribavirin_availability     = 0
            self.socioeconomic_level_of_human = 0


        # I HAVE NO IDEA WHY THIS DOESN'T WORK UNDER THE ELSE BLOCK; TECHINCALLY ONLY BELONGS TO RAT AGENTS 
        self.r2r_transmissibility           = 40


        # Determine if an agent (rat or human) starts off infected at the beginning of the model
        if random.uniform(0, 100) < init_infection:
            self.infected = True
            if self.is_human:
                self.model.infected_group.append(self)
        else:
            self.infected = False


    def step(self):
        # Determines if an agent (human or rat) moves at the beginning of a step
        if self.is_human:
            if random.uniform(0, 100) < self.level_of_hum_movement:
                self.move()
        else:
            if random.uniform(0, 100) < self.level_of_rat_movement:
                self.move()

        # Once an agents moves (or stays), we should check if the agent (rat or human) is infected and is able to infect others
        
        # Infected Human Host (only H2H possible)
        if self.is_human and self.infected:
            self.infect()
            self.contagious_period_hum -= 1

            if self.contagious_period_hum <= 0:
                self.infected = False

        # Infected Rat Host (both R2H and R2R possible)
        if not self.is_human and self.infected:
            self.infect()
            self.contagious_period_rat -= 1

            if self.contagious_period_rat <= 0:
                self.infected = False

        if self.is_human and self.infected and self.treated == False:
            if random.randint(0,100) < self.socioeconomic_level_of_human:
                self.treated = True
                self.infected = False
        
        if self.is_human and self.infected and self.treated == False:
            if self.ribavirin_availability != 0:
                self.treated = True
                self.infected = False
                self.ribavirin_availability -=1



    def move(self):
        # Creates a list of possible cells our agent (either rat/human) can move into (not including the cell its already on)
        neighbor_cells = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        # Choose a random cell from the list 
        new_position = random.choice(neighbor_cells)
        # Move the agent
        self.model.grid.move_agent(self, new_position)
    

    def infect(self):
        # Get a list of agents in this cell
        cellmates = self.model.grid.get_cell_list_contents([self.pos])

        # Check if there are more agents in that cell
        if len(cellmates) > 1:
            for resident in cellmates:
                if resident.is_human and not resident.infected:
                    # H2H Transmission
                    if self.is_human:
                        if random.uniform(0, 100) < self.h2h_transmissibility:
                            resident.infected = True
                            resident.model.infected_group.append(resident)
                            self.secondary_transmission_h2h += 1

                    # R2H Transmission
                    elif not self.is_human:
                        if random.uniform(0, 100) < self.r2h_transmissibility:
                            resident.infected = True
                            resident.model.infected_group.append(resident)
                            self.secondary_transmission_r2h += 1

                    # R2R Transmission
                    elif not resident.is_human and not resident.infected:
                        if random.uniform(0, 100) < self.r2r_transmissibility:
                            resident.infected = True

                    
                    
class lassaModel(Model):

    def __init__(self, N_humans, N_rats, test_population, isolation_population, width, height, hum_init_infection, rat_init_infection, hum_transmissibility, rat_transmissibility, hum_level_of_movement, rat_level_of_movement, 
    contagious_period_hum, contagious_period_rat, accessible_treatment, ribavirin_availability, socioeconomic_level_of_human):
        self.running                = True
        self.num_humans             = N_humans
        self.num_rats               = N_rats
        self.grid                   = MultiGrid(width, height, True)
        self.schedule               = RandomActivation(self)
        self.hum_transmissibility   = hum_transmissibility
        self.rat_transmissibility   = rat_transmissibility
        self.contagious_period_hum  = contagious_period_hum
        self.contagious_period_rat  = contagious_period_rat
        self.test_population        = test_population
        self.isolation_population   = isolation_population
        self.accessible_treatment   = accessible_treatment

        self.infected_group = []


        # Creates human agents
        for i in range(self.num_humans):
            human = superAgent(2*i, self, hum_init_infection, hum_transmissibility, hum_level_of_movement, contagious_period_hum, accessible_treatment,ribavirin_availability, socioeconomic_level_of_human, is_human=True)
            self.schedule.add(human)

            try:
                start_cell = self.grid.find_empty()
                self.grid.place_agent(human, start_cell)
            except:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
                self.grid.place_agent(human, (x,y))
            

        self.test_group_list    = determineTestGroup(self)
        determineIsolateGroup(self) 


        # Creates rat agents
        for i in range(self.num_rats):
            rat = superAgent((2*i)+1, self, rat_init_infection, rat_transmissibility, rat_level_of_movement, contagious_period_rat, accessible_treatment=0, ribavirin_availability=0, socioeconomic_level_of_human=0, is_human=False)
            self.schedule.add(rat)

            try:
                start_cell = self.grid.find_empty()
                self.grid.place_agent(rat, start_cell)
            except:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)
                self.grid.place_agent(rat,(x,y))



        self.datacollector = DataCollector(
            model_reporters={"Daily Reproduction Number":calculate_total_reproduction_number,
                            },
            agent_reporters={}
        )


    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        resetInfections(self)
        checkInfectionGroup(self)



# Daily Infections Graph Functions

def calculate_human_secondary_infections(model):

    human_secondary_infections = 0
    agent_list = model.schedule.agents

    for x in agent_list:
        if x.is_human:
            human_secondary_infections += x.secondary_transmission_h2h

    return human_secondary_infections


def calculate_rat_secondary_infections(model):

    rat_secondary_infections = 0

    agent_list = model.schedule.agents

    for x in agent_list:
        if not x.is_human:
            rat_secondary_infections += x.secondary_transmission_r2h

    return rat_secondary_infections


# Daily Reproduction Numbers Graph Functions

def calculate_human_reproduction_number(model):
    h2h_trans_rate          = model.hum_transmissibility / 100
    h2h_trans_avg           = calculate_avg_secondary_infection(model, "Human")
    hum_contagious_period   = model.contagious_period_hum

    h2h_r0 = h2h_trans_rate * h2h_trans_avg * hum_contagious_period

    return h2h_r0


def calculate_rat_reproduction_number(model):
    r2h_trans_rate          = model.rat_transmissibility / 100
    r2h_trans_avg           = calculate_avg_secondary_infection(model, "Rat")
    rat_contagious_period   = model.contagious_period_rat

    r2h_r0 = r2h_trans_rate * r2h_trans_avg * rat_contagious_period

    return r2h_r0 


def calculate_total_reproduction_number(model):
    h2h_r0  = calculate_human_reproduction_number(model)
    r2h_r0  = calculate_rat_reproduction_number(model) 
    
    trace       = h2h_r0 + r2h_r0
    determinant = h2h_r0 * r2h_r0

    first_eigenvalue    = (trace/2) + math.sqrt((trace/2)**2 - determinant)
    second_eigenvalue   = (trace/2) - math.sqrt((trace/2)**2 - determinant)
    
    return max(first_eigenvalue, second_eigenvalue)


# Helper Functions Related to Reproduction Numbers

def resetInfections(model):

    agent_list = model.schedule.agents

    for x in agent_list:
        if x.is_human:
            x.secondary_transmission_h2h = 0
        else:
            x.secondary_transmission_r2h = 0


def calculate_avg_secondary_infection(model, agentType):
    num_humans       = 0
    num_rats         = 0
    total_agent_list = model.schedule.agents

    # Counts how many total human/rat agents there are
    for x in total_agent_list:
        if x.is_human:
            num_humans += 1
        else:
            num_rats += 1

    if agentType == "Human":
        avg = calculate_human_secondary_infections(model) / num_humans
    elif agentType == "Rat":
        avg = calculate_rat_secondary_infections(model) / num_rats

    return avg


# Helper function Related to Infected Groups

def checkInfectionGroup(self):
    for x in self.infected_group:
        if not x.infected:
            self.infected_group.remove(x)


def determineTestGroup(self):
    percentage                   = self.test_population/100
    number_of_infected           = len(self.infected_group)
    number_of_test_group         = int(percentage*number_of_infected)
    test_group_list              = random.sample(self.infected_group, number_of_test_group)

    for i in test_group_list:
        i.test_group             = True
    return test_group_list 


def determineIsolateGroup(self):
    percentage                   = self.isolation_population/100
    number_of_isolated_group     = int(percentage*len(self.test_group_list))
    isolated_group_list          = random.sample(self.test_group_list, number_of_isolated_group)

    for i in isolated_group_list:
        i.isolate_group          = True 
