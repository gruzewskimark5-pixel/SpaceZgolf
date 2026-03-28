import random
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# To avoid circular imports, we will pass the run_simulation function into the optimizer
class GeneticOptimizer:
    def __init__(self, run_sim_func, population_size=20, generations=10, mutation_rate=0.1):
        self.run_sim = run_sim_func
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

        # Define the parameter space bounds
        self.bounds = {
            "heat_threshold_anchor": (1.0, 5.0),
            "heat_threshold_camera": (1.0, 5.0),
            "chaos_velocity_threshold": (-1.0, 0.0),
            "ces_threshold": (0.1, 2.0),
            "chaos_probability": (0.0, 1.0)
        }

    def generate_random_policy(self) -> Dict:
        return {
            "heat_threshold_anchor": round(random.uniform(*self.bounds["heat_threshold_anchor"]), 2),
            "heat_threshold_camera": round(random.uniform(*self.bounds["heat_threshold_camera"]), 2),
            "chaos_velocity_threshold": round(random.uniform(*self.bounds["chaos_velocity_threshold"]), 2),
            "ces_threshold": round(random.uniform(*self.bounds["ces_threshold"]), 2),
            "chaos_probability": round(random.uniform(*self.bounds["chaos_probability"]), 2)
        }

    def evaluate_fitness(self, policy: Dict) -> float:
        # Run a short simulation to evaluate this policy
        events = self.run_sim(policy, steps=30)

        if not events:
            return 0.0

        avg_heat = sum(e["heat"] for e in events) / len(events)
        avg_ces = sum(e["ces"] for e in events) / len(events)
        chaos_count = sum(1 for e in events if "CHAOS_INJECTION" in e["actions"])

        # Fitness Function: Maximize Heat and CES, but penalize excessive chaos
        # (Too much chaos burns out the audience)
        chaos_penalty = max(0, (chaos_count - 5) * 0.2)

        fitness = (avg_heat * 0.6) + (avg_ces * 0.4) - chaos_penalty
        return max(0.0, round(fitness, 3))

    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        child = {}
        for key in self.bounds.keys():
            # 50/50 chance to take gene from parent 1 or 2
            child[key] = parent1[key] if random.random() > 0.5 else parent2[key]
        return child

    def mutate(self, policy: Dict) -> Dict:
        mutated = policy.copy()
        for key, (min_val, max_val) in self.bounds.items():
            if random.random() < self.mutation_rate:
                # Nudge the value slightly
                nudge = random.uniform(-0.5, 0.5)
                # For probabilities and small ranges, scale the nudge
                if key in ["chaos_velocity_threshold", "chaos_probability", "ces_threshold"]:
                    nudge *= 0.2

                new_val = mutated[key] + nudge
                mutated[key] = round(max(min_val, min(max_val, new_val)), 2)
        return mutated

    async def optimize(self, websocket_callback=None) -> List[Dict]:
        population = [self.generate_random_policy() for _ in range(self.population_size)]
        history = []

        for gen in range(self.generations):
            # Evaluate fitness for all individuals
            scored_population = []
            for ind in population:
                fitness = self.evaluate_fitness(ind)
                scored_population.append({"policy": ind, "fitness": fitness})

            # Sort by fitness descending
            scored_population.sort(key=lambda x: x["fitness"], reverse=True)

            best_individual = scored_population[0]
            avg_fitness = sum(x["fitness"] for x in scored_population) / self.population_size

            gen_data = {
                "generation": gen + 1,
                "best_fitness": best_individual["fitness"],
                "avg_fitness": round(avg_fitness, 3),
                "best_policy": best_individual["policy"]
            }
            history.append(gen_data)

            # Stream progress if callback provided
            if websocket_callback:
                await websocket_callback(gen_data)

            # Selection (Elitism: keep top 20%)
            elite_count = max(2, int(self.population_size * 0.2))
            next_generation = [x["policy"] for x in scored_population[:elite_count]]

            # Fill the rest with crossover and mutation
            while len(next_generation) < self.population_size:
                # Tournament selection
                tournament = random.sample(scored_population, 3)
                tournament.sort(key=lambda x: x["fitness"], reverse=True)
                parent1 = tournament[0]["policy"]

                tournament = random.sample(scored_population, 3)
                tournament.sort(key=lambda x: x["fitness"], reverse=True)
                parent2 = tournament[0]["policy"]

                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                next_generation.append(child)

            population = next_generation

        return history
