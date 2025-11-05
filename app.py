import streamlit as st
import pandas as pd
import random
 
 
POPULATION_SIZE = 50
NUM_GENERATIONS = 100
NUM_TIME_SLOTS = 8  
 
 
def create_individual(program_list):
    """
Creates a random schedule (an 'individual') """
    schedule =
random.sample(program_list, NUM_TIME_SLOTS)
    return schedule
 
 
def initialize_population(program_list):
    """
Creates the initial population of random schedules """
    population = []
    for _ in
range(POPULATION_SIZE):
       population.append(create_individual(program_list))
    return population
 
 
def calculate_fitness(schedule, ratings_dict):
    """
Calculates the total rating (fitness) for a given schedule """
    fitness = 0
    for program_id in
schedule:
        fitness +=
ratings_dict.get(program_id, 0)
    return fitness
 
 
def selection(population, ratings_dict):
    """
Selects a good parent using tournament selection """
    tournament =
random.sample(population, 5)
    best_individual =
max(tournament, key=lambda ind: calculate_fitness(ind, ratings_dict))
    return
best_individual
 
 
def crossover(parent1, parent2, crossover_rate):
    """
    Performs
single-point crossover with a given rate (co_r).
    Uses the
'crossover_rate' variable from the Streamlit slider.
    """
    if random.random()
< crossover_rate:
        point =
random.randint(1, NUM_TIME_SLOTS - 1)
        
      
        child1 =
parent1[:point] + [gene for gene in parent2 if gene not in parent1[:point]]
        child2 =
parent2[:point] + [gene for gene in parent1 if gene not in parent2[:point]]
        
       
        child1 =
(child1 + [gene for gene in parent2 if gene not in child1])[:NUM_TIME_SLOTS]
        child2 =
(child2 + [gene for gene in parent1 if gene not in child2])[:NUM_TIME_SLOTS]
        return child1,
child2
    else:
       
        return
parent1, parent2
 
 
def mutation(individual, mutation_rate):
    """
    Performs swap
mutation with a given rate (mut_r).
    Uses the
'mutation_rate' variable from the Streamlit slider.
    """
    if random.random()
< mutation_rate:
        
        idx1, idx2 =
random.sample(range(NUM_TIME_SLOTS), 2)
        
       individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
    return individual
 
 
def run_ga(csv_data, co_r, mut_r):
    """
    This is the main
function that runs the entire GA process
    and returns the
best schedule as a pandas DataFrame.
    """
    
    
    available_programs
= csv_data['ProgramID'].unique().tolist() # .tolist() was missing in your code, I fixed it.
    ratings_dict =
pd.Series(csv_data.Rating.values, index=csv_data.ProgramID).to_dict()
 
   
    population =
initialize_population(available_programs)
    
    
    for _ in
range(NUM_GENERATIONS):
        new_population
= []
        
       
        best_of_gen =
max(population, key=lambda ind: calculate_fitness(ind, ratings_dict))
       new_population.append(best_of_gen)
        
        
        while
len(new_population) < POPULATION_SIZE:
            parent1 =
selection(population, ratings_dict)
            parent2 =
selection(population, ratings_dict)
            
           
            child1,
child2 = crossover(parent1, parent2, co_r) 
            child1 =
mutation(child1, mut_r) 
            child2 =
mutation(child2, mut_r) 
            
           new_population.extend([child1, child2])
        
        population =
new_population[:POPULATION_SIZE]
 
    
 s   best_schedule_ids
= max(population, key=lambda ind: calculate_fitness(ind, ratings_dict))
    
    
    # Added .drop_duplicates() for safety
    schedule_details =
csv_data[csv_data['ProgramID'].isin(best_schedule_ids)].drop_duplicates(subset=['ProgramID'])
    final_schedule_df
= pd.DataFrame({'ProgramID': best_schedule_ids})
    final_schedule_df
= final_schedule_df.merge(schedule_details, on='ProgramID', how='left')
    
   
    # --- "Time Slot" section removed as requested ---
    
    
    final_schedule_df
= final_schedule_df[['ProgramID', 'ProgramName', 'Genre',
'Rating']]
    
    
    total_fitness =
final_schedule_df['Rating'].sum()
 
    return
final_schedule_df, total_fitness
 
 
 
st.title('Genetic Algorithm for TV Scheduling')
 
 
st.sidebar.header('GA Parameters Input')
 
 
co_r = st.sidebar.slider(
    'Crossover Rate
(CO_R)', 
    min_value=0.0, 
    max_value=0.95, 
    value=0.8,  
    step=0.05
)
 
 
mut_r = st.sidebar.slider(
    'Mutation Rate
(MUT_R)', 
    min_value=0.01, 
    max_value=0.05, 
    value=0.02, 
    step=0.01
)
 
st.sidebar.write('---')
 
 
if st.sidebar.button('Run Genetic Algorithm'):
    
    
    try:
        
        CSV_FILE_NAME
= 'program_ratings.csv'
        ratings_data =
pd.read_csv(CSV_FILE_NAME)
        
        # --- Check for at least 8 programs ---
        if 'ProgramID'
not in ratings_data.columns or 'Rating' not in ratings_data.columns:
           st.error(f"Error: Your CSV file ('{CSV_FILE_NAME}') must contain
'ProgramID' and 'Rating' columns.")
        elif len(ratings_data['ProgramID'].unique()) < NUM_TIME_SLOTS:
            st.error(f"Error: Your CSV file must contain at least {NUM_TIME_SLOTS} unique programs to fill the schedule.")
        else:
            with
st.spinner('Evolving schedules... Please wait.'):
                
               final_schedule, total_fitness = run_ga(ratings_data, co_r, mut_r)
            
           st.success('Algorithm run complete!')
 
            
           st.subheader('Parameters Used for This Trial')
           st.code(f"Crossover Rate: {co_r}\nMutation Rate: {mut_r}")
            
  s         
           st.subheader('Resulting Schedule')
           st.write(f"**Total Schedule Rating (Fitness):
{total_fitness:.2f}**")
           st.dataframe(final_schedule)
 
  s  except
FileNotFoundError:
       st.error(f"Error: The CSV file ('{CSV_FILE_NAME}') was not found.
Please make sure it's in your repository and named correctly.")
    except Exception
as e:
       st.error(f"An error occurred: {e}")
 
else:
  s  st.info('Set your
parameters in the sidebar and click "Run Genetic Algorithm" to
start.')
