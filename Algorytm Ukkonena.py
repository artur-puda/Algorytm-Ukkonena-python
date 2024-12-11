import sys
import time
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    def __init__(self, start=-1, end=None, suffix_link=-1):
        self.start = start
        self.end = end  # None dla liści; będzie aktualizowane dynamicznie
        self.children = {}
        self.suffix_link = suffix_link

class SuffixTree:
    def __init__(self, s):
        self.nodes = [Node()]  # Korzeń drzewa
        self.num_nodes = 1
        self.active_node = 0
        self.active_edge = -1
        self.active_length = 0
        self.remaining_suffix_count = 0
        self.text = s + "$"  # Dodajemy unikalny znak końcowy, aby uniknąć nakładających się sufiksów
        self.size = len(self.text)  # Długość tekstu, łącznie z końcowym symbolem

        if s is not None:
            for i in range(self.size):
                self.add_char(i)

    def edge_length(self, node):
        return (node.end if node.end is not None else self.size - 1) - node.start + 1

    def add_char(self, pos):
        self.remaining_suffix_count += 1
        last_new_node = -1
        current_char = self.text[pos]

        while self.remaining_suffix_count > 0:
            if self.active_length == 0:
                self.active_edge = pos

            active_edge_char = self.text[self.active_edge]
            active_node = self.active_node

            if active_edge_char not in self.nodes[active_node].children:
                # Tworzenie nowego liścia
                leaf_node_index = self.num_nodes
                self.num_nodes += 1
                leaf_node = Node(start=pos, end=self.size - 1)  # Zapisujemy indeks końca
                self.nodes.append(leaf_node)
                self.nodes[active_node].children[active_edge_char] = leaf_node_index

                if last_new_node != -1:
                    self.nodes[last_new_node].suffix_link = active_node
                    last_new_node = -1
            else:
                next_node_index = self.nodes[active_node].children[active_edge_char]
                next_node = self.nodes[next_node_index]

                if self.walk_down(next_node_index):
                    continue

                if self.text[next_node.start + self.active_length] == current_char:
                    if last_new_node != -1 and active_node != 0:
                        self.nodes[last_new_node].suffix_link = active_node
                        last_new_node = -1
                    self.active_length += 1
                    break

                # Podział krawędzi
                split_node_index = self.num_nodes
                self.num_nodes += 1
                split_node = Node(start=next_node.start, end=next_node.start + self.active_length - 1)
                self.nodes.append(split_node)

                self.nodes[active_node].children[active_edge_char] = split_node_index

                # Nowy liść
                leaf_node_index = self.num_nodes
                self.num_nodes += 1
                leaf_node = Node(start=pos, end=self.size - 1)
                self.nodes.append(leaf_node)
                self.nodes[split_node_index].children[current_char] = leaf_node_index

                next_node.start += self.active_length
                self.nodes[split_node_index].children[self.text[next_node.start]] = next_node_index

                if last_new_node != -1:
                    self.nodes[last_new_node].suffix_link = split_node_index

                last_new_node = split_node_index

            self.remaining_suffix_count -= 1

            if self.active_node == 0 and self.active_length > 0:
                self.active_length -= 1
                self.active_edge = pos - self.remaining_suffix_count + 1
            elif self.active_node != 0:
                self.active_node = self.nodes[self.active_node].suffix_link if self.nodes[self.active_node].suffix_link > -1 else 0

    def walk_down(self, next_node_index):
        next_node = self.nodes[next_node_index]
        length = self.edge_length(next_node)
        if self.active_length >= length:
            self.active_edge += length
            self.active_length -= length
            self.active_node = next_node_index
            return True
        return False

    def build_graph(self):
        G = nx.DiGraph()
        def add_edges(node_index):
            node = self.nodes[node_index]
            for child_char, child_index in node.children.items():
                child_node = self.nodes[child_index]
                label = f"[{child_node.start}, {child_node.end if child_node.end is not None else self.size - 1}]"
                G.add_edge(node_index, child_index, label=label)
                add_edges(child_index)
        add_edges(0)
        return G

    def visualize_graphical(self, liczba_wezlow, liczba_krawedzi, execution_time):
        # Budowanie grafu
        G = self.build_graph()

        # Tworzenie wykresu
        fig, ax = plt.subplots(figsize=(12, 8))

        # Tworzenie layoutu i etykiet
        pos = nx.spring_layout(G, seed=42)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw(G, pos, with_labels=True, arrows=True, node_size=500, node_color='lightblue', ax=ax)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

        # Wyświetlanie informacji o węzłach, krawędziach i czasie wykonania
        ax.text(
            0.05, 0.95,
            f"Liczba wierzchołków: {liczba_wezlow}\nLiczba krawędzi: {liczba_krawedzi}\nCzas wykonywania: {execution_time:.2f} s",
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.5)
        )

        plt.show()

    def visualize_console(self, rozmiar_grafu, dlugosc_tekstu, liczba_wezlow, liczba_krawedzi, build_time):
        def print_tree(node_index, prefix=""):
            node = self.nodes[node_index]
            children = node.children
            if node.start != -1:
                node_label = f"{node_index}: [{node.start}, {node.end if node.end is not None else self.size - 1}]"
            else:
                node_label = f"{node_index}: 'Root'"
            if not children:
                print(prefix + "-- " + node_label)
                return
            print(prefix + "+- " + node_label)
            for i, (child_char, child_index) in enumerate(children.items(), 1):
                new_prefix = prefix + ("   " if i == len(children) else "|  ")
                print_tree(child_index, new_prefix)

        print("\nStruktura drzewa sufiksowego:")
        print_tree(0)

        print(f"\nRozmiar drzewa sufiksowego: {rozmiar_grafu} bajtów")
        print(f"Długość tekstu w bajtach: {dlugosc_tekstu} bajtów")
        print(f"Liczba wierzchołków: {liczba_wezlow}")
        print(f"Liczba krawędzi: {liczba_krawedzi}")
        print(f"Czas budowy drzewa sufiksowego: {build_time:.6f} sekund")

    def visualize(self, display_mode, rozmiar_grafu=0, dlugosc_tekstu=0, liczba_wezlow=0, liczba_krawedzi=0, build_time=0.0):
        if display_mode.lower() == 'g':
            self.visualize_graphical(liczba_wezlow, liczba_krawedzi, build_time)
        elif display_mode.lower() == 'c':
            self.visualize_console(rozmiar_grafu, dlugosc_tekstu, liczba_wezlow, liczba_krawedzi, build_time)
        else:
            print("Nieznana opcja wyświetlania. Proszę wybrać 'g' lub 'c'.")

def get_size(obj, seen=None):
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum(get_size(v, seen) for v in obj.values())
        size += sum(get_size(k, seen) for k in obj.keys())
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_size(i, seen) for i in obj)
    return size

def main():
    choice = ''
    while choice.lower() not in ['g', 'c']:
        choice = input("Czy chcesz wyświetlić drzewo graficznie (g) czy w konsoli (c)? [g/c]: ")

    text = input("Wprowadź tekst dla drzewa sufiksowego: ")
    if text is None:
        text = ''

    start_time = time.time()

    suffix_tree = SuffixTree(text)

    rozmiar_grafu = get_size(suffix_tree.nodes)
    dlugosc_tekstu = len(text.encode('utf-8'))

    G = suffix_tree.build_graph()
    liczba_wezlow = G.number_of_nodes()
    liczba_krawedzi = G.number_of_edges()

    end_time = time.time()
    build_time = end_time - start_time

    suffix_tree.visualize(choice, rozmiar_grafu, dlugosc_tekstu, liczba_wezlow, liczba_krawedzi, build_time)

if __name__ == "__main__":
    main()
