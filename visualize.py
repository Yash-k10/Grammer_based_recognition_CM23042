"""
Parse Tree Visualizer Module for Grammar-Based Pattern Recognition Engine.

Provides multi-format visual tree rendering for formal CFG derivations:
1. Graphviz DOT format export (.dot)
2. Graphviz PNG/PDF rendering (when system dot/graphviz is installed)
3. Pure-Python Standalone SVG rendering (zero external binary dependency)
4. Unicode / ASCII Box-drawing tree representation for terminal output
"""

import os
from typing import Optional, List, Tuple
from parser import ParseTreeNode

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


class ParseTreeVisualizer:
    """
    Renders hierarchical derivation parse trees in multiple visual formats.
    """

    # Color palette for nodes
    COLOR_ROOT = "#1E293B"       # Slate dark
    COLOR_NON_TERMINAL = "#2563EB" # Royal Blue
    COLOR_TERMINAL = "#059669"   # Emerald Green
    COLOR_TEXT = "#FFFFFF"

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_dot(self, root: ParseTreeNode) -> str:
        """
        Generates Graphviz DOT language representation of the parse tree.
        
        Args:
            root: ParseTreeNode root of derivation tree
            
        Returns:
            DOT format string
        """
        lines = [
            'digraph ParseTree {',
            '    rankdir=TB;',
            '    node [shape=box, style="filled,rounded", fontname="Helvetica, Arial, sans-serif", fontsize=11, margin="0.2,0.1"];',
            '    edge [color="#64748B", penwidth=1.5, arrowhead=vee];',
            '    bgcolor="transparent";',
        ]

        node_counter = [0]

        def walk(node: ParseTreeNode) -> int:
            current_id = node_counter[0]
            node_counter[0] += 1

            if node.is_leaf():
                label = f"{node.symbol}\\n'{node.value}'" if node.value is not None else node.symbol
                fillcolor = "#10B981"  # Emerald for terminals
                fontcolor = "#FFFFFF"
                lines.append(f'    node_{current_id} [label="{label}", fillcolor="{fillcolor}", fontcolor="{fontcolor}", shape=ellipse];')
            else:
                label = node.symbol
                fillcolor = "#3B82F6" if current_id > 0 else "#1E293B"  # Blue for non-terminals, dark slate for root
                fontcolor = "#FFFFFF"
                lines.append(f'    node_{current_id} [label="{label}", fillcolor="{fillcolor}", fontcolor="{fontcolor}"];')

            for child in node.children:
                child_id = walk(child)
                lines.append(f'    node_{current_id} -> node_{child_id};')

            return current_id

        if root:
            walk(root)

        lines.append('}')
        return '\n'.join(lines)

    def save_dot(self, root: ParseTreeNode, filename: str = "parse_tree.dot") -> str:
        """Saves DOT graph description to a file."""
        dot_code = self.generate_dot(root)
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(dot_code)
        return filepath

    def render_graphviz(self, root: ParseTreeNode, filename: str = "parse_tree", format: str = "png") -> Optional[str]:
        """
        Renders parse tree using Graphviz library if available and dot executable is on PATH.
        
        Returns:
            Output filepath if successful, None otherwise
        """
        import shutil
        if not GRAPHVIZ_AVAILABLE or not shutil.which("dot"):
            return None

        try:
            dot_code = self.generate_dot(root)
            src = graphviz.Source(dot_code)
            output_base = os.path.join(self.output_dir, filename)
            rendered_path = src.render(output_base, format=format, cleanup=False)
            return rendered_path
        except Exception:
            return None

    def render_ascii(self, root: ParseTreeNode, prefix: str = "", is_last: bool = True, use_unicode: bool = True) -> str:
        """
        Renders a clean tree representation for terminal output.
        Uses Unicode box-drawing by default, with ASCII fallback.
        """
        if not root:
            return ""

        if use_unicode:
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
        else:
            connector = "\\-- " if is_last else "+-- "
            child_prefix = prefix + ("    " if is_last else "|   ")

        node_display = f"{root.symbol}"
        if root.is_leaf() and root.value is not None:
            node_display += f" : \"{root.value}\""

        result = prefix + connector + node_display + "\n"

        child_count = len(root.children)
        for i, child in enumerate(root.children):
            result += self.render_ascii(child, child_prefix, i == (child_count - 1), use_unicode=use_unicode)

        return result

    def render_svg(self, root: ParseTreeNode, filename: str = "parse_tree.svg") -> str:
        """
        Generates a standalone, beautifully styled SVG parse tree diagram.
        Requires zero external binaries or libraries.
        """
        if not root:
            return ""

        # Layout computation using hierarchical layered tree placement
        levels: List[List[Tuple[ParseTreeNode, int, int]]] = []  # [(node, x, y)]
        
        # Calculate tree width and coordinates
        node_positions = {}
        next_x = [50]
        node_id_counter = [0]

        def compute_layout(node: ParseTreeNode, depth: int) -> Tuple[int, int]:
            nid = node_id_counter[0]
            node_id_counter[0] += 1

            if not node.children:
                x = next_x[0]
                next_x[0] += 120
                y = 50 + depth * 80
                node_positions[nid] = (node, x, y, [])
                return x, y, nid
            
            child_nids = []
            child_xs = []
            for child in node.children:
                cx, cy, cnid = compute_layout(child, depth + 1)
                child_xs.append(cx)
                child_nids.append(cnid)

            x = sum(child_xs) // len(child_xs)
            y = 50 + depth * 80
            node_positions[nid] = (node, x, y, child_nids)
            return x, y, nid

        compute_layout(root, 0)

        max_x = max([pos[1] for pos in node_positions.values()]) + 100
        max_y = max([pos[2] for pos in node_positions.values()]) + 80
        width = max(max_x, 600)
        height = max_y

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
            '  <defs>',
            '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
            '      <stop offset="0%" stop-color="#FFFFFF" />',
            '      <stop offset="100%" stop-color="#F8FAFC" />',
            '    </linearGradient>',
            '    <filter id="shadow" x="-10%" y="-10%" width="130%" height="130%">',
            '      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#CBD5E1" flood-opacity="0.6"/>',
            '    </filter>',
            '  </defs>',
            f'  <rect width="{width}" height="{height}" fill="url(#bgGrad)" stroke="#E2E8F0" stroke-width="1.5" rx="12" />',
            '  <!-- Connection Lines -->',
        ]

        # Draw connecting edges
        for nid, (node, x, y, child_nids) in node_positions.items():
            for cnid in child_nids:
                cnode, cx, cy, _ = node_positions[cnid]
                svg_parts.append(
                    f'  <line x1="{x}" y1="{y + 18}" x2="{cx}" y2="{cy - 18}" '
                    f'stroke="#CBD5E1" stroke-width="2.5" stroke-linecap="round" />'
                )

        svg_parts.append('  <!-- Tree Nodes -->')

        # Draw nodes
        for nid, (node, x, y, _) in node_positions.items():
            is_leaf = node.is_leaf()
            if nid == 0:
                fill = "#EA580C"  # Bold Orange for Root
                stroke = "#C2410C"
                label = node.symbol
                sublabel = None
                box_w, box_h = 105, 38
            elif is_leaf:
                fill = "#059669"  # Emerald Green for Terminals
                stroke = "#047857"
                label = node.symbol
                sublabel = f"'{node.value}'" if node.value is not None else ""
                box_w, box_h = 100, 42
            else:
                fill = "#F97316"  # Vibrant Orange for Non-terminals
                stroke = "#EA580C"
                label = node.symbol
                sublabel = None
                box_w, box_h = 90, 34

            rect_x = x - (box_w // 2)
            rect_y = y - (box_h // 2)

            rx = 18 if is_leaf else 8
            svg_parts.append(
                f'  <g filter="url(#shadow)">'
                f'    <rect x="{rect_x}" y="{rect_y}" width="{box_w}" height="{box_h}" '
                f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" />'
            )

            if sublabel:
                svg_parts.append(
                    f'    <text x="{x}" y="{y - 3}" fill="#FFFFFF" font-family="system-ui, -apple-system, sans-serif" '
                    f'font-size="11" font-weight="bold" text-anchor="middle">{label}</text>'
                )
                svg_parts.append(
                    f'    <text x="{x}" y="{y + 13}" fill="#E0E7FF" font-family="monospace" '
                    f'font-size="10" text-anchor="middle">{sublabel}</text>'
                )
            else:
                svg_parts.append(
                    f'    <text x="{x}" y="{y + 4}" fill="#FFFFFF" font-family="system-ui, -apple-system, sans-serif" '
                    f'font-size="12" font-weight="bold" text-anchor="middle">{label}</text>'
                )

            svg_parts.append('  </g>')

        svg_parts.append('</svg>')
        svg_content = '\n'.join(svg_parts)

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

        return filepath


if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser

    lexer = Lexer()
    parser = Parser()
    sample = "dhanshree01@gmail.com"
    tokens = lexer.tokenize(sample)
    res = parser.parse(tokens)

    if res.is_valid and res.parse_tree:
        viz = ParseTreeVisualizer(output_dir="output")
        dot_file = viz.save_dot(res.parse_tree)
        svg_file = viz.render_svg(res.parse_tree)
        png_file = viz.render_graphviz(res.parse_tree)
        print("DOT saved to:", dot_file)
        print("SVG rendered to:", svg_file)
        print("PNG rendered to:", png_file)
        print("\nTerminal Visual Tree:")
        print(viz.render_ascii(res.parse_tree))
