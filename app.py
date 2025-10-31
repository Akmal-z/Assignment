import streamlit as st
import pandas as pd
import random

# --- 1. GENETIC ALGORITHM LOGIC ---
# This is a complete GA built to satisfy the [cite: 5, 6] instruction.
# It is designed to schedule 8 programs to maximize total rating.

# --- GA Constants ---
POPULATION_SIZE = 50
NUM_GENERATIONS = 100
NUM_TIME_SLOTS = 8  # The number of programs to schedule

# --- GA Function: Create a single schedule (Chromosome) ---
def create_individual(program_list):
    """ Creates a random schedule (an 'individual') """
    schedule = random.sample(program_list, NUM_TIME_SLOTS)
    return schedule

# --- GA Function: Create the first population ---
def initialize_population(program_list):
    """ Creates the initial population of random schedules """
    population = []
    for _ in range(POPULATION_SIZE):
        population.append(create_individual(program_list))
    return population

# --- GA Function: Score a schedule (Fitness Function) ---
def calculate_fitness(schedule, ratings_dict):
    """ Calculates the total rating (fitness) for a given schedule """
    fitness = 0
    for program_id in schedule:
        fitness += ratings_dict.get(program_id, 0)
    return fitness

# --- GA Function: Select parents for breeding (Tournament Selection) ---
def selection(population, ratings_dict):
    """ Selects a good parent using tournament selection """
    tournament = random.sample(population, 5)
    best_individual = max(tournament, key=lambda ind: calculate_fitness(ind, ratings_dict))
    return best_individual

# --- GA Function: Create children (Crossover) ---
def crossover(parent1, parent2, crossover_rate):
    """ 
    Performs single-point crossover with a given rate (co_r).
    Uses the 'crossover_rate' variable from the Streamlit slider.
    """
    if random.random() < crossover_rate:
        point = random.randint(1, NUM_TIME_SLOTS - 1)
        
        # Create children by combining parents
        child1 = parent1[:point] + [gene for gene in parent2 if gene not in parent1[:point]]
        child2 = parent2[:point] + [gene for gene in parent1 if gene not in parent2[:point]]
        
        # Ensure children are the correct length
        child1 = (child1 + [gene for gene in parent2 if gene not in child1])[:NUM_TIME_SLOTS]
        child2 = (child2 + [gene for gene in parent1 if gene not in child2])[:NUM_TIME_SLOTS]
        return child1, child2
    else:
        # No crossover, parents pass on
        return parent1, parent2

# --- GA Function: Randomly change a schedule (Mutation) ---
def mutation(individual, mutation_rate):
    """ 
    Performs swap mutation with a given rate (mut_r).
    Uses the 'mutation_rate' variable from the Streamlit slider.
    """
    if random.random() < mutation_rate:
        # Pick two random positions (indices) to swap
        idx1, idx2 = random.sample(range(NUM_TIME_SLOTS), 2)
        # Perform the swap
        individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
    return individual

# --- Main GA Function: This runs the whole process ---
def run_ga(csv_data, co_r, mut_r):
    """
    This is the main function that runs the entire GA process
    and returns the best schedule as a pandas DataFrame.
    """
    
    # Prepare data
    available_programs = csv_data['ProgramID'].tolist()
    ratings_dict = pd.Series(csv_data.Rating.values, index=csv_data.ProgramID).to_dict()

    # Initialize population
    population = initialize_population(available_programs)
    
    # Evolve for a number of generations
    for _ in range(NUM_GENERATIONS):
        new_population = []
        
        # Elitism: Keep the best individual from the current generation
        best_of_gen = max(population, key=lambda ind: calculate_fitness(ind, ratings_dict))
        new_population.append(best_of_gen)
        
        # Fill the rest of the new population
        while len(new_population) < POPULATION_SIZE:
            parent1 = selection(population, ratings_dict)
            parent2 = selection(population, ratings_dict)
            
            # Pass the user-defined rates to the functions
            child1, child2 = crossover(parent1, parent2, co_r) # [cite: 13]
            child1 = mutation(child1, mut_r) # [cite: 14]
            child2 = mutation(child2, mut_r) # [cite: 14]
            
            new_population.extend([child1, child2])
        
        population = new_population[:POPULATION_SIZE]

    # Get the best schedule from the final population
    best_schedule_ids = max(population, key=lambda ind: calculate_fitness(ind, ratings_dict))
    
    # Format the final schedule into a nice DataFrame
    schedule_details = csv_data[csv_data['ProgramID'].isin(best_schedule_ids)]
    final_schedule_df = pd.DataFrame({'ProgramID': best_schedule_ids})
    final_schedule_df = final_schedule_df.merge(schedule_details, on='ProgramID', how='left')
    
    # Add a Time Slot column
    final_schedule_df['Time Slot'] = [f"Slot {i+1}" for i in range(NUM_TIME_SLOTS)]
    
    # Reorder columns for the final table
    final_schedule_df = final_schedule_df[['Time Slot', 'ProgramID', 'ProgramName', 'Genre', 'Rating']]
    
    # Calculate the total fitness (rating) of the best schedule
    total_fitness = final_schedule_df['Rating'].sum()

    return final_schedule_df, total_fitness

# -----------------------------------------------------------------
# --- 2. STREAMLIT INTERFACE ---
# [cite: 11]
# -----------------------------------------------------------------

st.title('JIE42903 - Evolutionary Computing Assignment')
st.header('Genetic Algorithm for TV Scheduling')

# --- 3. PARAMETER INPUTS (IN SIDEBAR) ---
st.sidebar.header('GA Parameters Input')

# Crossover Rate (CO_R) slider [cite: 13, 15]
co_r = st.sidebar.slider(
    'Crossover Rate (CO_R)', 
    min_value=0.0, 
    max_value=0.95, 
    value=0.8,  # Default value [cite: 13]
    step=0.05
)

# Mutation Rate (MUT_R) slider [cite: 14, 15]
# Note: The required range [0.01, 0.05] [cite: 15] conflicts with the default (0.2)[cite: 14].
# I am using a logical default (0.02) that is *within* the required range.
mut_r = st.sidebar.slider(
    'Mutation Rate (MUT_R)', 
    min_value=0.01, 
    max_value=0.05, 
    value=0.02, # Using 0.02 as a logical default *within* the range [cite: 15]
    step=0.01
)

st.sidebar.write('---')

# --- 4. RUN ALGORITHM AND DISPLAY RESULTS ---

# Button to run the algorithm
if st.sidebar.button('Run Genetic Algorithm'):
    
    # --- Load your modified CSV data ---
    # 
    try:
        # This file MUST be in your GitHub repository
        CSV_FILE_NAME = 'program_ratings.csv'
        ratings_data = pd.read_csv(CSV_FILE_NAME)
        
        # Check if the CSV has the required columns
        if 'ProgramID' not in ratings_data.columns or 'Rating' not in ratings_data.columns:
            st.error(f"Error: Your CSV file ('{CSV_FILE_NAME}') must contain 'ProgramID' and 'Rating' columns.")
        else:
            with st.spinner('Evolving schedules... Please wait.'):
                # --- Run your GA logic ---
                final_schedule, total_fitness = run_ga(ratings_data, co_r, mut_r)
            
            st.success('Algorithm run complete!')

            # --- Display parameters used [cite: 24] ---
            st.subheader('Parameters Used for This Trial')
            st.code(f"Crossover Rate: {co_r}\nMutation Rate: {mut_r}")
            
            # --- Display the schedule in a table [cite: 17, 18, 19, 25] ---
            st.subheader('Resulting Schedule')
            st.write(f"**Total Schedule Rating (Fitness): {total_fitness:.2f}**")
            st.dataframe(final_schedule)

    except FileNotFoundError:
        st.error(f"Error: The CSV file ('{CSV_FILE_NAME}') was not found. Please make sure it's in your repository and named correctly.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    st.info('Set your parameters in the sidebar and click "Run Genetic Algorithm" to start.')
