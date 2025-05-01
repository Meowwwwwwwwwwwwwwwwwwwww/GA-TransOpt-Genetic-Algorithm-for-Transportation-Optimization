import random
import copy

SAMPLE_INPUT = {
    "buses": [
        {"id": "bus1", "capacity": 50, "depotCoordinates": [37.7749, -122.4194]},  # San Francisco (West Coast)
        {"id": "bus2", "capacity": 50, "depotCoordinates": [40.7128, -74.0060]}   # New York (East Coast)
    ],
    "stops": [
        {"id": "stopA", "coordinates": [34.0522, -118.2437], "studentCount": 70},  # Los Angeles
        {"id": "stopB", "coordinates": [39.7392, -104.9903], "studentCount": 30},  # Denver
        {"id": "stopC", "coordinates": [41.8781, -87.6298], "studentCount": 40},  # Chicago
        {"id": "stopD", "coordinates": [32.7157, -117.1611], "studentCount": 50},  # San Diego
        {"id": "stopE", "coordinates": [38.9072, -77.0369], "studentCount": 60},  # Washington DC
        {"id": "college", "coordinates": [37.7749, -122.4194], "studentCount": 0}  # College, same as SF depot for simplicity
    ],
    "constraints": {
        "hard": {
            "maxStudentsPerBus": 50,
            "collegeLast": True,
            "latestArrivalTime": "09:00"
        },
        "soft": {
            "fuelWeight": 0.7,
            "balanceWeight": 0.3
        }
    }
}

class BusGA:
    def __init__(self, input_data):
        self.input_data = input_data
        self.buses = input_data["buses"]
        self.stops = [s for s in input_data["stops"] if s["id"] != "college"]
        self.college = next(s for s in input_data["stops"] if s["id"] == "college")
        self.constraints = input_data["constraints"]
        
        self.pop_size = 50
        self.max_generations = 100
        self.mutation_rate = 0.2
        self.elitism = 0.1

    def initialize_population(self):
        population = []
        for _ in range(self.pop_size):
            chromosome = {
                "busroutes": {},
                "studentgroups": {},
                "departuretime": {}
            }

            # For each stop, we distribute the students across buses
            for stop in self.stops:
                chromosome["studentgroups"][stop["id"]] = {bus["id"]: 0 for bus in self.buses}
                remaining = stop["studentCount"]
                shuffled_buses = copy.deepcopy(self.buses)
                random.shuffle(shuffled_buses)  # Shuffle buses for diversity

                # Assign students to buses
                for bus in shuffled_buses:
                    if remaining <= 0:
                        break
                    assign = random.randint(0, min(remaining, bus["capacity"]))
                    chromosome["studentgroups"][stop["id"]][bus["id"]] += assign
                    remaining -= assign

            # Assign stops to buses and create routes
            for bus in self.buses:
                stops_for_bus = [stop["id"] for stop in self.stops if chromosome["studentgroups"][stop["id"]][bus["id"]] > 0]
                # Ensure that each bus has a unique route by adding randomness
                if len(stops_for_bus) > 1:
                    random.shuffle(stops_for_bus)  # Shuffle stops for diversity
                stops_for_bus.append("college")
                chromosome["busroutes"][bus["id"]] = stops_for_bus
                # Random departure times
                hour = random.randint(6, 8)
                minute = random.randint(0, 59)
                chromosome["departuretime"][bus["id"]] = f"{hour}:{minute:02d} AM"
            
            population.append(chromosome)
        return population

    def calculate_distance(self, coord1, coord2):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5

    def evaluate_fitness(self, chromosome):
        fitness = 0
        bus_loads = []
        total_distance = 0
        buses_used = 0

        for bus in self.buses:
            route = chromosome["busroutes"][bus["id"]]
            if route[-1] != "college":
                return 0
            load = 0
            for stop in self.stops:
                load += chromosome["studentgroups"][stop["id"]][bus["id"]]
            
            # Check if bus is used (i.e., it has students assigned)
            if load > 0:
                buses_used += 1
            
            if load > bus["capacity"]:
                return 0
            
            bus_loads.append(load)
            prev_coords = bus["depotCoordinates"]
            for stop_id in route:
                stop = next((s for s in self.input_data["stops"] if s["id"] == stop_id), None)
                if stop:
                    total_distance += self.calculate_distance(prev_coords, stop["coordinates"])
                    prev_coords = stop["coordinates"]

        # Fuel cost (minimize distance)
        fitness += (1 / (total_distance + 1)) * self.constraints["soft"]["fuelWeight"]
        
        # Load balancing (try to balance the load across buses)
        if len(bus_loads) > 1:
            diff = max(bus_loads) - min(bus_loads)
            fitness += (1 - (diff / sum(bus_loads))) * self.constraints["soft"]["balanceWeight"]
        
        # Reward for fewer buses being used (lower penalty for using fewer buses)
        buses_used_penalty = max(0, buses_used - 1)  # Reward fewer buses used
        fitness -= buses_used_penalty * 0.1  # Adjust this penalty as needed

        return fitness

    def selection(self, population):
        selected = []
        for _ in range(self.pop_size):
            candidates = random.sample(population, 3)
            best = max(candidates, key=lambda x: x["fitness"])
            selected.append(copy.deepcopy(best))
        return selected

    def crossover(self, p1, p2):
        child = {
            "busroutes": {},
            "studentgroups": copy.deepcopy(p1["studentgroups"]),
            "departuretime": copy.deepcopy(p1["departuretime"])
        }
        crossover_stop = random.choice(self.stops)["id"]
        for bus in self.buses:
            if random.random() > 0.5:
                child["studentgroups"][crossover_stop][bus["id"]] = p2["studentgroups"][crossover_stop][bus["id"]]
        for bus in self.buses:
            stops_for_bus = [stop["id"] for stop in self.stops if child["studentgroups"][stop["id"]][bus["id"]] > 0]
            random.shuffle(stops_for_bus)
            stops_for_bus.append("college")
            child["busroutes"][bus["id"]] = stops_for_bus
        return child

    def mutate(self, chromo):
        chromo = copy.deepcopy(chromo)
        if random.random() < self.mutation_rate:
            stop_id = random.choice(self.stops)["id"]
            bus1, bus2 = random.sample(self.buses, 2)
            move = random.randint(1, 5)
            available = chromo["studentgroups"][stop_id][bus1["id"]]
            move = min(move, available)
            bus2_load = sum(chromo["studentgroups"][s["id"]][bus2["id"]] for s in self.stops)
            if bus2_load + move <= bus2["capacity"]:
                chromo["studentgroups"][stop_id][bus1["id"]] -= move
                chromo["studentgroups"][stop_id][bus2["id"]] += move
        return chromo

    def run(self):
        population = self.initialize_population()

        # Evaluate initial fitness
        for chrom in population:
            chrom["fitness"] = self.evaluate_fitness(chrom)

        all_generations = []

        for generation in range(self.max_generations):
            population.sort(key=lambda x: x["fitness"], reverse=True)

            # Log current generation
            print(f"\n=== Generation {generation + 1} ===")
            for i, chrom in enumerate(population):
                print(f"Chromosome {i + 1}: Fitness = {chrom['fitness']:.4f}")

            all_generations.append(copy.deepcopy(population))

            if population[0]["fitness"] >= 1.9:
                print("\nEarly stopping: Good enough solution found.")
                break

            elites = population[:int(self.elitism * self.pop_size)]
            selected = self.selection(population)

            offspring = []
            for i in range(0, len(selected) - 1, 2):
                child = self.crossover(selected[i], selected[i + 1])
                offspring.append(child)

            mutated = [self.mutate(c) for c in offspring]
            for chrom in mutated:
                chrom["fitness"] = self.evaluate_fitness(chrom)

            population = elites + mutated
            population = population[:self.pop_size]

        # Final best solution
        best = max(population, key=lambda x: x["fitness"])
        print(f"\n=== Best Final Solution (Fitness: {best['fitness']:.4f}) ===")
        return self.format_solution(best)

    def format_solution(self, chromo):
        formatted_solution = {
            "busroutes": {},
            "studentgroups": chromo["studentgroups"],
            "departuretime": chromo["departuretime"]
        }

        for bus, stops in chromo["busroutes"].items():
            formatted_solution["busroutes"][bus] = []

            for stop_id in stops:
                # Find the stop's coordinates
                stop = next((s for s in self.input_data["stops"] if s["id"] == stop_id), None)
                if stop:
                    # Ensure the stop is in self.stops list
                    stop_number = None
                    for i, s in enumerate(self.stops):
                        if s["id"] == stop_id:
                            stop_number = i + 1
                            break
                    
                    if stop_number is None:
                        print(f"Warning: Stop {stop_id} not found in self.stops")
                        continue
                    
                    coordinates = stop["coordinates"]
                    formatted_solution["busroutes"][bus].append({
                        "stop_number": stop_number,
                        "coordinates": coordinates
                    })
                else:
                    print(f"Warning: Stop {stop_id} not found in input_data['stops']")

        return formatted_solution


if __name__ == "__main__":
    ga = BusGA(SAMPLE_INPUT)
    solution = ga.run()
    print("\n=== FINAL SOLUTION ===")
    print("Bus Routes:")
    for bus, stops in solution["busroutes"].items():
        print(f"{bus}: {stops}")
    print("\nStudent Groups:")
    for stop, group in solution["studentgroups"].items():
        print(f"{stop}: {group}")
    print("\nDeparture Times:")
    for bus, time in solution["departuretime"].items():
        print(f"{bus}: {time}")
