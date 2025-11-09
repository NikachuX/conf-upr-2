from graphviz import Digraph

def export_to_graphviz(graph, root, filename="graph.dot"):
    dot = Digraph(comment=f"Dependency graph for {root}", format="png")
    dot.attr('node', shape='box', style='rounded,filled', color='lightblue2')

    visited = set()
    stack = [root]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)

        for dep in graph.get(node, []):
            dot.edge(node, dep)
            if dep not in visited:
                stack.append(dep)

    dot.save(filename)
    print(f"Graphviz файл сохранён: {filename}")
    return dot

def render_graph(dot):
    """
    Рендерит граф и открывает его изображение (если поддерживается системой).
    """
    output_path = dot.render(filename='dependency_graph', cleanup=True)
    print(f"Граф сохранён как {output_path}")

def visualize_dependencies(graph, root):
    dot = export_to_graphviz(graph, root)
    render_graph(dot)
