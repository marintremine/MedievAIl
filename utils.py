import html
from datetime import datetime

def render_snapshot(model) -> str:
    """Construit une page HTML lisible séparant Army 1 et Army 2."""

    def render_unit_table(units):
        if not units:
            return "<p>Aucune unité</p>"

        rows = ""
        for u in units:
            hp_display = "Dead" if not u.is_alive() else f"{u.hp}/{u.max_hp}"
            rows += f"""
            <tr>
            <td>{u.name}</td>
            <td>{u.x}</td>
            <td>{u.y}</td>
            <td>{hp_display}</td>
            <td>{u.cooldown_timer:.2f}s/{u.cooldown:.2f}s</td>
            <td>{min(u.move_progress * 100, 100):.1f}%</td>
            </tr>
            """

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>X</th>
                    <th>Y</th>
                    <th>HP</th>
                    <th>Cooldown</th>
                    <th>Move Progress</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Battle Snapshot</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 16px; }}
        h1 {{ margin-bottom: 8px; }}
        section {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 6px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 6px; }}
        th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
        th {{ background: #eee; }}
        .collapsible {{ cursor: pointer; user-select: none; margin-bottom: 5px; }}
    </style>
    <script>
        function toggle(id) {{
            var e = document.getElementById(id);
            e.style.display = (e.style.display === "none") ? "block" : "none";
        }}
    </script>
    </head>
    <body>

        <h1>Battle Snapshot</h1>
        <p>Generated at: {html.escape(datetime.utcnow().isoformat() + "Z")}</p>

        <section>
            <h2 class="collapsible" onclick="toggle('army1')">Army 1</h2>
            <div id="army1">
                {render_unit_table(model.get_army(model.general_1))}
            </div>
        </section>

        <section>
            <h2 class="collapsible" onclick="toggle('army2')">Army 2</h2>
            <div id="army2">
                {render_unit_table(model.get_army(model.general_2))}
            </div>
        </section>
    </body>
    </html>
    """
