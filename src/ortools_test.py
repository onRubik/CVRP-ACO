from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from tqdm import tqdm

def create_data_model():
    """Create data for the problem."""
    data = {}
    data['distance_matrix'] = [
        [0, 10, 15, 20, 25, 30, 35, 40],
        [10, 0, 35, 25, 20, 40, 45, 50],
        [15, 35, 0, 30, 50, 10, 45, 55],
        [20, 25, 30, 0, 10, 15, 20, 25],
        [25, 20, 50, 10, 0, 30, 35, 40],
        [30, 40, 10, 15, 30, 0, 40, 45],
        [35, 45, 45, 20, 35, 40, 0, 55],
        [40, 50, 55, 25, 40, 45, 55, 0]
    ]
    data['num_vehicles'] = 3
    data['vehicle_capacities'] = [30, 40, 50]
    data['depot'] = 0
    return data

def print_solution(data, manager, routing, solution):
    """Prints the solution on the console."""
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f'Route for Vehicle {vehicle_id}:\n'
        route_distance = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            plan_output += f' {node_index} ->'
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        plan_output += f' {manager.IndexToNode(index)}\n'
        plan_output += f'Route distance for Vehicle {vehicle_id}: {route_distance} units\n'
        print(plan_output)

def main():
    data = create_data_model()

    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    # Create your own distance and demand callback functions

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )

    solution = None
    with tqdm(total=100) as pbar:
        def update_progress(percent):
            nonlocal pbar
            pbar.n = percent
            pbar.refresh()

        def progress_tracker():
            nonlocal solution
            solution = routing.SolveWithParameters(search_parameters)
            update_progress(100)

        progress_tracker()

    if solution:
        print_solution(data, manager, routing, solution)

if __name__ == '__main__':
    main()
