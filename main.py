import math
import matplotlib.pyplot as plt
from collections import defaultdict


def load_data(input_file):
    """Načíta súradnice miest zo súboru."""
    coords = []
    dimension = None
    reading_coords = False

    try:
        with open(input_file, 'r') as f:
            for line in map(str.strip, f):
                if not line:
                    continue

                if line.upper() == "NODE_COORD_SECTION":
                    reading_coords = True
                    continue
                elif line.upper() == "EOF":
                    break

                if not reading_coords:
                    if line.startswith("DIMENSION"):
                        parts = line.split(":")
                        if len(parts) == 2:
                            dimension = int(parts[1])
                    continue

                parts = line.split()
                if len(parts) == 3:
                    _, x, y = parts
                    coords.append((float(x), float(y)))

    except Exception as e:
        print(f"Chyba pri načítaní súboru: {e}")
        return None, None

    if dimension is None or len(coords) != dimension:
        print("Chyba: Nezodpovedajúca DIMENSION a počet načítaných miest.")
        return None, None

    return dimension, coords


def calculate_distance(p1, p2):
    """Vypočíta euklidovskú vzdialenosť medzi dvoma bodmi (x, y)."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def create_distance_matrix(dimension, coords):
    """Vytvorí maticu vzdialeností pre úplný graf."""
    dist_matrix = [[0.0] * dimension for _ in range(dimension)]

    for i in range(dimension):
        for j in range(i + 1, dimension):
            dist = calculate_distance(coords[i], coords[j])
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist

    return dist_matrix

def calculate_graph_MST(distance_matrix):
    """Vypočíta minimálnu kostru grafu pomocou Primovho algoritmu s adjacenčnou maticou."""
    n = len(distance_matrix)
    selected = [False] * n
    min_edge = [float('inf')] * n
    parent = [-1] * n

    min_edge[0] = 0  # Začíname od vrcholu 0

    for _ in range(n):
        # Vyber najbližší nevybraný vrchol
        u = -1
        for i in range(n):
            if not selected[i] and (u == -1 or min_edge[i] < min_edge[u]):
                u = i

        selected[u] = True

        # Aktualizuj vzdialenosti k susedom vrcholu u
        for v in range(n):
            if distance_matrix[u][v] < min_edge[v] and not selected[v]:
                min_edge[v] = distance_matrix[u][v]
                parent[v] = u

    mst_edges = []
    total_weight = 0.0

    for v in range(1, n):
        u = parent[v]
        weight = distance_matrix[u][v]
        mst_edges.append((u, v, weight))
        total_weight += weight

    return mst_edges, total_weight

def find_odd_degree_vertices(mst_edges, n):
    """Nájde všetky vrcholy s nepárnym stupňom v MST."""
    degree = [0] * n
    for u, v, _ in mst_edges:
        degree[u] += 1
        degree[v] += 1

    odd_vertices = [i for i, d in enumerate(degree) if d % 2 == 1]
    return odd_vertices

def greedy_min_weight_matching(odd_vertices, distance_matrix):
    """Greedy párovanie vrcholov s nepárnym stupňom s minimálnou váhou hrán."""
    unmatched = set(odd_vertices)
    matching = []

    while unmatched:
        u = unmatched.pop()
        # Nájdeme najbližšieho partnera
        v = min(unmatched, key=lambda x: distance_matrix[u][x])
        unmatched.remove(v)
        matching.append((u, v, distance_matrix[u][v]))

    return matching



def build_multigraph(mst_edges, matching_edges):
    """Vytvorí multigraf spojením MST a párovania."""
    multigraph = defaultdict(list)
    for u, v, _ in mst_edges + matching_edges:
        multigraph[u].append(v)
        multigraph[v].append(u)
    return multigraph

def find_eulerian_circuit(graph):
    """Nájde Eulerov cyklus v Eulerovskom grafe."""
    graph_copy = {u: list(vs) for u, vs in graph.items()}
    stack = []
    circuit = []
    curr = next(iter(graph_copy))

    while stack or graph_copy[curr]:
        if not graph_copy[curr]:
            circuit.append(curr)
            curr = stack.pop()
        else:
            stack.append(curr)
            neighbor = graph_copy[curr].pop()
            graph_copy[neighbor].remove(curr)
            curr = neighbor

    circuit.append(curr)
    return circuit[::-1]


def make_hamiltonian_cycle(eulerian_circuit):
    """Prevedie Eulerov cyklus na Hamiltonov cyklus odstránením návštev duplicitných vrcholov."""
    visited = set()
    path = []

    for v in eulerian_circuit:
        if v not in visited:
            visited.add(v)
            path.append(v)

    # návrat do východzieho bodu
    path.append(path[0])
    return path


def print_distance_matrix_info(distance_matrix, dimension):
    if dimension >= 2:
        dist_0_1 = distance_matrix[0][1]
        print(f"Vzdialenosť medzi mestom 1 (idx 0) a mestom 2 (idx 1): {dist_0_1:.4f}")


def build_mst_and_report(distance_matrix):
    mst_edges, mst_weight = calculate_graph_MST(distance_matrix)
    print(f"Počet hrán v MST: {len(mst_edges)}")
    print(f"Celková dĺžka MST: {mst_weight:.2f}")
    return mst_edges


def run_christofides_algorithm(dimension, coords, optimal_tour_length=None):
    distance_matrix = create_distance_matrix(dimension, coords)
    print_distance_matrix_info(distance_matrix, dimension)

    mst_edges = build_mst_and_report(distance_matrix)

    odd_vertices = find_odd_degree_vertices(mst_edges, dimension)
    print(f"\nPočet vrcholov s nepárnym stupňom: {len(odd_vertices)}")

    matching_edges = greedy_min_weight_matching(odd_vertices, distance_matrix)
    print(f"Počet hrán v matching-u: {len(matching_edges)}")

    multigraph = build_multigraph(mst_edges, matching_edges)
    print("Multigraf vytvorený.")

    eulerian_circuit = find_eulerian_circuit(multigraph)
    print(f"Dĺžka Eulerovho cyklu (s opakovaniami): {len(eulerian_circuit)}")

    hamilton_cycle = make_hamiltonian_cycle(eulerian_circuit)
    print(f"Dĺžka Hamiltonovho cyklu (optimálnej trasy): {len(hamilton_cycle)}")

    total_length = sum(
        distance_matrix[hamilton_cycle[i]][hamilton_cycle[i + 1]]
        for i in range(len(hamilton_cycle) - 1)
    )
    print(f"Celková dĺžka trasy (Christofides): {total_length:.2f}")

    # ➕ Porovnanie s optimálnym riešením, ak je zadané
    if optimal_tour_length is not None:
        difference = total_length - optimal_tour_length
        percent_over = (difference / optimal_tour_length) * 100
        print(f"Známe optimálne riešenie: {optimal_tour_length:.2f}")
        print(f"Rozdiel: {difference:.2f} ({percent_over:.2f} % nad optimom)")

    return hamilton_cycle, total_length


def save_tour_to_file(tour: list[int], filename: str = "output_tour.txt") -> None:
    """Uloží Hamiltonov cyklus do textového súboru, pričom ID miest začínajú od 1."""
    with open(filename, "w") as f:
        for city_id in tour:
            f.write(f"{city_id + 1}\n")
    print(f"\nVýsledná trasa uložená do súboru '{filename}'.")


def plot_tour(tour: list[int], coords: list[tuple[float, float]], output_image: str = "tour_plot.png") -> None:
    """Vygeneruje a uloží vizualizáciu Hamiltonovho cyklu."""
    x = [coords[i][0] for i in tour]
    y = [coords[i][1] for i in tour]

    plt.figure(figsize=(12, 10))
    plt.plot(x, y, 'b-', linewidth=0.3)  # tenká modrá čiara
    plt.plot(x[0], y[0], 'ro', markersize=3)  # označenie začiatku

    plt.title("Hamiltonov cyklus (zjednodušená vizualizácia)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    plt.close()
    print(f"Trasa uložená ako '{output_image}'")


if __name__ == '__main__':
    input_filename = "eg7146.txt"
    known_optimal_length = 172_386
    dimension, coords = load_data(input_filename)

    if dimension and coords:
        print(f"Načítaných {dimension} miest.")
        print(f"Súradnice mesta s ID 1 (index 0): {coords[0]}")
        hamilton_cycle, total_length = run_christofides_algorithm(dimension, coords, known_optimal_length)
        save_tour_to_file(hamilton_cycle)
        plot_tour(hamilton_cycle, coords)


