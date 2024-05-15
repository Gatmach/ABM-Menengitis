import numpy as np
import starsim as ss

class Vaccine(ss.Intervention):
    def __init__(self, timestep=100, prob=0.5, imm_boost=2.0):
        super().__init__()
        self.timestep = timestep
        self.prob = prob
        self.imm_boost = imm_boost

    def apply(self, sim):
        if sim.ti == self.timestep:
            meningitis = sim.diseases.meningitis
            eligible_ids = sim.people.uid[meningitis.susceptible]
            n_eligible = len(eligible_ids)
            to_vaccinate = self.prob > np.random.rand(n_eligible)
            vaccine_ids = eligible_ids[to_vaccinate]
            meningitis.immunity[vaccine_ids] += self.imm_boost
            
# Define people with the right age structure
class VaccineAge(ss.Intervention):
    def __init__(self, age_range=None, timestep=10, prob=0.5, imm_boost=2.0):
        super().__init__() # Initialize the intervention
        self.timestep = timestep # Store the timestep the vaccine is applied on
        self.prob = prob # Store the probability of vaccination
        self.imm_boost = imm_boost # Store the amount by which immunity is boosted
        self.age_range = age_range

    def apply(self, sim): # Apply the vaccine
        if sim.ti == self.timestep: # Only apply on the matching timestep
            meningitis = sim.diseases.meningitis # Shorten the name of the disease module
            eligibility_conditions = meningitis.susceptible
            
            if self.age_range is not None: 
                lower_age = self.age_range[0]
                upper_age = self.age_range[1]
                age_conditions = (sim.people.age >= lower_age) & (sim.people.age < upper_age)
                eligibility_conditions = eligibility_conditions & age_conditions
                
            eligible_ids = sim.people.uid[eligibility_conditions] # Only susceptible people are eligible
                
            n_eligible = len(eligible_ids)  # Number of people who are eligible
            to_vaccinate = self.prob > np.random.rand(n_eligible) # Define which of the n_eligible people get vaccinated
            vaccine_ids = eligible_ids[to_vaccinate]
            meningitis.immunity[vaccine_ids] += self.imm_boost
            
class Treatment(ss.Intervention):
    def __init__(self, timestep=10, prob=0.5, mean_dur_infection=5):
        super().__init__()
        self.timestep = timestep
        self.prob = prob
        self.dur_infection = ss.normal(mean_dur_infection, 1)

    def apply(self, sim):
        if sim.ti == self.timestep:
            meningitis = sim.diseases.meningitis
            eligible_ids = sim.people.uid[meningitis.ti_infected == sim.ti]
            n_eligible = len(eligible_ids)
            is_treated = np.random.rand(n_eligible) < self.prob
            treat_ids = eligible_ids[is_treated]
            dur_inf = self.dur_infection.rvs(treat_ids)
            will_die = meningitis.pars.p_death.rvs(treat_ids)
            dead_uids = treat_ids[will_die]
            recover_uids = treat_ids[~will_die]
            meningitis.ti_dead[dead_uids] = meningitis.ti_infected[dead_uids] + dur_inf[will_die] / sim.dt
            meningitis.ti_recovered[recover_uids] = meningitis.ti_infected[recover_uids] + dur_inf[~will_die] / sim.dt
