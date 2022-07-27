from Lassa_model import lassaModel
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

def agent_portrayal(agent):
    # Susceptible human
    portrayal = {"Shape":"hum-sc.png", "Filled":"true", "Layer":1}

    # Infected human
    if agent.is_human == True and agent.infected:
        portrayal["Shape"] = "hum-if.png"
        portrayal["Layer"] = 0
    # Susceptible rat
    elif agent.is_human == False and not agent.infected:
        portrayal["Shape"] = "rat-sc.png"
        portrayal["Layer"] = 2
    # Infeceted rat
    elif agent.is_human == False and agent.infected:
        portrayal["Shape"] = "rat-if.png"
        portrayal["Layer"] = 3

    return portrayal



# Setups how the grid is going to be displayed on the webpage
grid = CanvasGrid(agent_portrayal, 30, 30, 800, 800)




# Creates our charts
total_reproduction_number_graph = ChartModule(
    [{"Label":"Daily Reproduction Number", "Color":"SlateBlue"}],
    data_collector_name='datacollector'
    )



# Set up user sliders
num_human_slider = UserSettableParameter(
        'slider', "Number of Human Agents", 100, 2, 200, 1)

num_rat_slider = UserSettableParameter(
        'slider', "Number of Rat Agents", 150, 2, 200, 1)

test_population_slider = UserSettableParameter(
    'slider', "percentage of infected people who isolate themselves ", 0, 0, 100, 1)
    
isolation_population_slider = UserSettableParameter(
    'slider', "percentage of test population who isolate themselves", 0, 0 , 100, 1)

hum_init_infection_slider = UserSettableParameter(
    'slider', "Probability of Human Initial Infection(%)", 30, 1, 100, 1)

rat_init_infection_slider = UserSettableParameter(
    'slider', "Probability of Rat Initial Infection(%)", 50, 1, 100, 1)

hum_transmissibility_slider = UserSettableParameter(
    'slider', "Transmissibilty between H2H", 20, 1, 100, 1)

hum_level_of_movement_slider = UserSettableParameter(
    'slider', "Level of movement for humans", 45, 1, 100, 1)

rat_level_of_movement_slider = UserSettableParameter(
    'slider', "Level of movement for rats", 65, 1, 100, 1)

hum_contagious_period_slider = UserSettableParameter(
    'slider', "Contagious period for humans(days)", 12, 2, 21, 1)

rat_contagious_period_slider = UserSettableParameter(
    'slider', "Contagious period for rats(days)", 21, 80, 90, 1)





server = ModularServer(lassaModel, [grid, total_reproduction_number_graph], "Intervention Strategies for the Control of Periodic Lassa Fever Outbreaks", 
    {   
        "N_humans": num_human_slider, 
        "N_rats": num_rat_slider,
        "test_population":test_population_slider,
        "isolation_population":isolation_population_slider,
        "width": 30,
        "height":30,
        "hum_init_infection": hum_init_infection_slider,
        "rat_init_infection": rat_init_infection_slider,
        "hum_transmissibility": hum_transmissibility_slider,
        "rat_transmissibility": 60,
        "hum_level_of_movement": hum_level_of_movement_slider,
        "rat_level_of_movement": rat_level_of_movement_slider,
        "contagious_period_hum": hum_contagious_period_slider,
        "contagious_period_rat": rat_contagious_period_slider,    
    }
)