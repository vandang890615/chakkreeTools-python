"""
IngeTrazo Plugin Entry Point for Chakkree Tools
Registers toolbars, menus, and 3D modeling actions within IngeTrazo CAD.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from chakkree_tools.i18n import tr

try:
    from tools.base import Tool  # type: ignore
except ImportError:
    try:
        from ingetrazo.sdk import Tool  # type: ignore
    except ImportError:
        class Tool:
            """Fallback base Tool class when IngeTrazo SDK is not installed."""
            def __init__(self, name: str = "ChakkreeToolsPlugin") -> None:
                self.name = name
                self.active = False

            def activate(self) -> None:
                self.active = True

            def deactivate(self) -> None:
                self.active = False


class ChakkreeToolsPlugin(Tool):
    """
    IngeTrazo plugin providing parametric RC structural tools and .debim export.
    """

    def __init__(self, app: Optional[Any] = None) -> None:
        try:
            super().__init__(name="chakkree_tools")
        except TypeError:
            super().__init__()
            self.name = "chakkree_tools"
        self.app = app
        self.active = False
        self.active_elements: List[Any] = []
        self.show_rebars: bool = False

    def on_activate(self, viewport: Optional[Any] = None) -> None:
        self.active = True

    def on_deactivate(self, viewport: Optional[Any] = None) -> None:
        self.active = False

    def activate(self) -> None:
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def cmd_toggle_rebars(self, parent: Optional[Any] = None) -> bool:
        """Toggles visibility of 3D rebar cages inside the IngeTrazo viewport."""
        self.show_rebars = not self.show_rebars
        msg = tr("Chakkree Tools: Rebar Meshes Shown") if self.show_rebars else tr("Chakkree Tools: Rebar Meshes Hidden")
        if hasattr(self.app, "flash_status"):
            self.app.flash_status(msg)

        # Render rebar cage for active elements to reflect rebar toggle state
        scene, viewport = self._get_scene_and_viewport()
        if scene is not None and hasattr(scene, "mesh"):
            if not self.active_elements:
                if hasattr(self.app, "flash_status"):
                    self.app.flash_status(tr("Chakkree Tools: No active elements. Create a Footing, Column, Beam, or Slab first."))
                return self.show_rebars

            if self.show_rebars:
                # Render rebar cages for elements without duplicating concrete faces
                for el in self.active_elements:
                    self._render_element_rebar_only(el, scene, viewport)

        return self.show_rebars

    def get_menu_registration(self) -> Dict[str, Any]:
        """
        Registers menu items under Extensions > Chakkree Tools.
        """
        return {
            "menu_path": "Extensions > Chakkree Tools",
            "items": [
                {
                    "label": tr("Create Pile Cap (1-9 Piles)..."),
                    "action": self.cmd_create_pile_cap,
                },
                {
                    "label": tr("Create RC Column (4-16 Bars)..."),
                    "action": self.cmd_create_column,
                },
                {
                    "label": tr("Create RC Beam..."),
                    "action": self.cmd_create_beam,
                },
                {
                    "label": tr("Create Slab (PS Plank / RC)..."),
                    "action": self.cmd_create_slab,
                },
                {
                    "label": tr("Toggle Show/Hide 3D Rebar Meshes"),
                    "action": self.cmd_toggle_rebars,
                },
                {
                    "label": tr("Export Model to .debim..."),
                    "action": self.cmd_export_debim,
                    "shortcut": "Ctrl+Shift+E",
                },
            ],
        }

    def get_toolbar_registration(self) -> Dict[str, Any]:
        """
        Registers toolbar actions for IngeTrazo matching the original Chakkree Tools UI.
        """
        icons_dir = Path(__file__).resolve().parent / "resources" / "icons"
        return {
            "toolbar_name": "chakkree_tools",
            "actions": [
                {
                    "name": "RebarTools",
                    "label": tr("Rebar Tools"),
                    "tooltip": tr("Rebar Tools - Bend hooks and generate 3D reinforcement cages"),
                    "icon": str(icons_dir / "RebarTools.svg"),
                    "action": self.cmd_rebar_tools,
                },
                {
                    "name": "ToggleRebars",
                    "label": tr("Show/Hide Rebars"),
                    "tooltip": tr("Toggle Show/Hide 3D Rebar Meshes"),
                    "icon": str(icons_dir / "ToggleRebars.svg"),
                    "action": self.cmd_toggle_rebars,
                },
                {
                    "name": "FootingTools",
                    "label": tr("Footings"),
                    "tooltip": tr("Footing Tools - Parametric 1-9 pile caps and isolated footings"),
                    "icon": str(icons_dir / "FootingTools.svg"),
                    "action": self.cmd_create_pile_cap,
                },
                {
                    "name": "BeamTools",
                    "label": tr("Beams"),
                    "tooltip": tr("Beam Tools - Parametric RC beams with multi-zone stirrup spacing"),
                    "icon": str(icons_dir / "BeamTools.svg"),
                    "action": self.cmd_create_beam,
                },
                {
                    "name": "ColumnTools",
                    "label": tr("Columns"),
                    "tooltip": tr("Column Tools - Rectangular/Circular columns with 4-16 longitudinal bars"),
                    "icon": str(icons_dir / "ColumnTools.svg"),
                    "action": self.cmd_create_column,
                },
                {
                    "name": "SlabTools",
                    "label": tr("Slabs"),
                    "tooltip": tr("Slab Tools - Precast plank and cast-in-place RC slabs"),
                    "icon": str(icons_dir / "SlabTools.svg"),
                    "action": self.cmd_create_slab,
                },
                {"name": "separator_1", "type": "separator"},
                {
                    "name": "GridLine",
                    "label": tr("Grid Lines"),
                    "tooltip": tr("GridLine v2026 - Parametric X/Y grid axes and elevation levels"),
                    "icon": str(icons_dir / "GridLine.svg"),
                    "action": self.cmd_create_grids,
                },
                {"name": "separator_2", "type": "separator"},
                {
                    "name": "TakeOff",
                    "label": tr("QTO Take-off"),
                    "tooltip": tr("Quantity Take-off - Concrete volume, formwork, and Bar Bending Schedule"),
                    "icon": str(icons_dir / "TakeOff.svg"),
                    "action": self.cmd_qto_takeoff,
                },
                {
                    "name": "AnalysisRC",
                    "label": tr("RC Analysis"),
                    "tooltip": tr("RC Analysis - Export model to .debim for OpenBIM / debim CLI"),
                    "icon": str(icons_dir / "AnalysisTool.svg"),
                    "action": self.cmd_export_debim,
                },
                {"name": "separator_3", "type": "separator"},
                {
                    "name": "ConfigColorRebar",
                    "label": tr("Config Colors"),
                    "tooltip": tr("Config Colors - Rebar color customization by diameter (RB6-DB32)"),
                    "icon": str(icons_dir / "ConfigColorRebar.svg"),
                    "action": self.cmd_config_colors,
                },
                {"name": "separator_4", "type": "separator"},
                {
                    "name": "About",
                    "label": tr("About"),
                    "tooltip": tr("About Chakkree Tools (Python Edition) © Chakkree Tiyawongsuwan"),
                    "icon": str(icons_dir / "About.svg"),
                    "action": self.cmd_about,
                },
            ],
        }

    def cmd_rebar_tools(self, parent: Optional[Any] = None) -> None:
        """Handler for Rebar Tools & Standards."""
        try:
            from PySide6.QtWidgets import QApplication
            from chakkree_tools.ingetrazo_plugin.ui.rebar_tools_dialog import RebarToolsDialog
            if QApplication.instance() is not None:
                win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                if callable(win):
                    win = win()
                dlg = RebarToolsDialog(parent=win)
                dlg.exec()
        except ImportError:
            pass

    def cmd_create_grids(
        self,
        specs: Optional[Dict[str, Any]] = None,
        show_dialog: bool = True,
        parent: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """Handler for GridLine creation."""
        if specs is not None:
            self._render_grids_to_scene(specs)
            return specs

        if show_dialog:
            try:
                from PySide6.QtWidgets import QApplication, QDialog
                from chakkree_tools.ingetrazo_plugin.ui.grid_dialog import GridLineDialog
                if QApplication.instance() is not None:
                    win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                    if callable(win):
                        win = win()
                    dlg = GridLineDialog(parent=win)
                    if dlg.exec() == QDialog.Accepted:
                        specs = dlg.get_grid_specs()
                        self._render_grids_to_scene(specs)
                        return specs
                    return None
            except ImportError:
                pass

        default_specs = {
            "x_count": 4,
            "x_spacing": 4.0,
            "y_count": 3,
            "y_spacing": 4.0,
            "height": 3.5,
        }
        self._render_grids_to_scene(default_specs)
        return default_specs

    def cmd_qto_takeoff(self, parent: Optional[Any] = None) -> Any:
        """Handler for QTO TakeOff."""
        from chakkree_tools.qto.takeoff import generate_qto_summary
        summary = generate_qto_summary(self.active_elements)
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            if QApplication.instance() is not None:
                win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                if callable(win):
                    win = win()
                lines = [
                    tr("=== Chakkree Tools QTO Summary ==="),
                    tr("Total Elements: {count}", count=summary.total_elements),
                    tr("Concrete Volume: {vol:.3f} m³", vol=summary.total_concrete_volume_m3),
                    tr("Formwork Area: {area:.2f} m²", area=summary.total_formwork_area_m2),
                    tr("Total Rebar Weight: {weight:.2f} kg", weight=summary.total_rebar_weight_kg),
                    "",
                    tr("Rebar Breakdown (BBS):"),
                ]
                for bar_type, wt in summary.rebar_weight_by_size.items():
                    lines.append(f"  • {bar_type}: {wt:.2f} kg")
                QMessageBox.information(
                    win,
                    tr("QTO & Bar Bending Schedule"),
                    "\n".join(lines),
                )
        except ImportError:
            pass
        return summary

    def cmd_config_colors(self, parent: Optional[Any] = None) -> None:
        """Handler for Rebar Colors Configuration."""
        try:
            from PySide6.QtWidgets import QApplication, QDialog
            from chakkree_tools.ingetrazo_plugin.ui.color_dialog import ColorConfigDialog
            if QApplication.instance() is not None:
                win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                if callable(win):
                    win = win()
                dlg = ColorConfigDialog(parent=win)
                if dlg.exec() == QDialog.Accepted:
                    if hasattr(self.app, "flash_status"):
                        self.app.flash_status(tr("Updated rebar color configuration"))
        except ImportError:
            pass

    def cmd_about(self, parent: Optional[Any] = None) -> None:
        """Handler for About info."""
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            from chakkree_tools.i18n import get_current_language
            if QApplication.instance() is not None:
                win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                if callable(win):
                    win = win()
                title = tr("About Chakkree Tools (Python Edition)")
                lang = get_current_language()
                if lang == "vi":
                    message = (
                        "Chakkree Tools (Phiên bản Python cho IngeTrazo) v0.1.0\n\n"
                        "Phát triển và dịch ngược từ tiện ích mở rộng SketchUp sang IngeTrazo CAD kết hợp chuẩn OpenBIM .debim.\n"
                        "Tác giả ý tưởng và mô hình gốc: Thầy Chakkree Tiyawongsuwan (อ.จักรี ติยะวงศ์สุวรรณ).\n\n"
                        "Nếu bạn yêu thích và nhận được giá trị từ công cụ này, hãy ủng hộ tác giả gốc tại:\n"
                        "https://sites.google.com/view/learn-sketchup/myextension/chakkree_tools-v0-4?authuser=0\n\n"
                        "GitHub: https://github.com/PRIDA-TAKON/chakkreeTools-python"
                    )
                else:
                    message = (
                        "Chakkree Tools (Python Edition for IngeTrazo) v0.1.0\n\n"
                        "Reverse-engineered and ported to IngeTrazo CAD with OpenBIM .debim integration.\n"
                        "Original SketchUp extension created by อ.จักรี ติยะวงศ์สุวรรณ.\n\n"
                        "หากคุณชอบและได้รับประโยชน์จากส่วนขยายนี้ สามารถสนับสนุนนักพัฒนาต้นฉบับได้ที่:\n"
                        "https://sites.google.com/view/learn-sketchup/myextension/chakkree_tools-v0-4?authuser=0\n\n"
                        "GitHub: https://github.com/PRIDA-TAKON/chakkreeTools-python"
                    )
                QMessageBox.information(win, title, message)
        except ImportError:
            pass

    def cmd_select_language(self, parent: Optional[Any] = None) -> Optional[str]:
        """Allows user to select active language (English, Tiếng Việt, ภาษาไทย, Español)."""
        try:
            from PySide6.QtWidgets import QApplication, QInputDialog
            from chakkree_tools.i18n import (
                LANGUAGE_NAMES,
                available_languages,
                get_current_language,
                set_language,
                tr,
            )
            if QApplication.instance() is not None:
                win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                if callable(win):
                    win = win()
                langs = available_languages()
                items = [f"{LANGUAGE_NAMES.get(code, code)} ({code})" for code in langs]
                current_code = get_current_language()
                curr_idx = langs.index(current_code) if current_code in langs else 0
                chosen_item, ok = QInputDialog.getItem(
                    win,
                    tr("Select Language"),
                    tr("Language..."),
                    items,
                    curr_idx,
                    False,
                )
                if ok and chosen_item:
                    selected_code = langs[items.index(chosen_item)]
                    set_language(selected_code)
                    msg = tr("Language set to {lang}", lang=LANGUAGE_NAMES.get(selected_code, selected_code))
                    if hasattr(self.app, "flash_status"):
                        self.app.flash_status(msg)
                    return selected_code
        except Exception as e:
            print(f"[chakkree_tools] Notice: Could not select language: {e}")
        return None

    def cmd_stream_to_bridge(self, host: str = "127.0.0.1", port: int = 8482) -> bool:
        """Handler to live-stream active elements to IngeTrazo via Agent Bridge."""
        from chakkree_tools.exporter.debim_exporter import DebimExporter
        from chakkree_tools.ingetrazo_plugin.agent_streamer import stream_to_ingetrazo
        exporter = DebimExporter(project_name="Chakkree Live Stream")
        for el in self.active_elements:
            exporter.add_element(el)
        manifest_yaml = exporter.to_yaml()
        try:
            result = stream_to_ingetrazo(manifest_yaml, host=host, port=port)
            if hasattr(self.app, "flash_status"):
                self.app.flash_status(tr("Chakkree Tools: Streamed to IngeTrazo successfully!"))
            return result
        except Exception as e:
            if hasattr(self.app, "flash_status"):
                self.app.flash_status(f"Stream error: {e}")
            return False

    def _get_scene_and_viewport(self) -> tuple:
        scene, viewport = None, None
        if hasattr(self.app, "scene") and callable(self.app.scene):
            scene = self.app.scene()
        elif hasattr(self.app, "_window") and hasattr(self.app._window, "viewport"):
            viewport = self.app._window.viewport
            scene = getattr(viewport, "scene", None)
        elif hasattr(self.app, "viewport"):
            viewport = self.app.viewport
            scene = getattr(viewport, "scene", None)
        return scene, viewport

    def _commit_faces_to_scene(self, scene: Any, viewport: Any, faces: List[List[Any]], status_msg: str) -> None:
        try:
            from PySide6.QtGui import QVector3D
        except ImportError:
            QVector3D = None

        mesh = scene.mesh
        for loop in faces:
            if QVector3D is not None:
                q_pts = [QVector3D(p[0], p[1], p[2]) for p in loop]
            else:
                q_pts = loop
            try:
                mesh.add_face(q_pts)
            except Exception:
                pass
        if hasattr(scene, "bump_view"):
            scene.bump_view()
        elif hasattr(scene, "version"):
            scene.version += 1
        if viewport is not None and hasattr(viewport, "update"):
            viewport.update()
        elif hasattr(self.app, "viewport") and hasattr(self.app.viewport, "update"):
            self.app.viewport.update()
        if hasattr(self.app, "flash_status"):
            self.app.flash_status(f"Chakkree Tools: {status_msg}")
        elif viewport is not None and hasattr(viewport, "flash_status"):
            viewport.flash_status(f"Chakkree Tools: {status_msg}")

    def _render_grids_to_scene(self, specs: Dict[str, Any]) -> None:
        """Renders 3D structural grid lines and bubbles into IngeTrazo active scene."""
        import math
        scene, viewport = self._get_scene_and_viewport()
        if scene is None or not hasattr(scene, "mesh"):
            return

        x_count = int(specs.get("x_count", 4))
        x_spacing = float(specs.get("x_spacing", 4.0))
        y_count = int(specs.get("y_count", 3))
        y_spacing = float(specs.get("y_spacing", 4.0))
        height = float(specs.get("height", 3.5))

        total_x = (x_count - 1) * x_spacing if x_count > 1 else 0.0
        total_y = (y_count - 1) * y_spacing if y_count > 1 else 0.0
        overhang = 1.50
        dia = 0.025  # Grid line tube diameter

        faces: List[List[Any]] = []
        from chakkree_tools.rc.rebar_mesh import generate_tubular_mesh

        # Store grid axes on plugin instance
        self.grid_specs = specs
        self.grids_x = {str(i + 1): i * x_spacing for i in range(x_count)}
        self.grids_y = {chr(65 + j): j * y_spacing for j in range(y_count)}

        # Grid lines along Y (for each X axis)
        for i in range(x_count):
            x = i * x_spacing
            p_start = (x, -overhang, 0.0)
            p_end = (x, total_y + overhang, 0.0)
            m = generate_tubular_mesh([p_start, p_end], diameter=dia, radial_segments=4)
            if "faces" in m:
                faces.extend(m["faces"])

            # Add octagonal bubble markers at both ends
            for cy in [-overhang - 0.35, total_y + overhang + 0.35]:
                bubble_poly = []
                r = 0.30
                for k in range(8):
                    ang = 2.0 * math.pi * k / 8.0
                    bubble_poly.append((x + r * math.cos(ang), cy + r * math.sin(ang), 0.005))
                faces.append(bubble_poly)

        # Grid lines along X (for each Y axis)
        for j in range(y_count):
            y = j * y_spacing
            p_start = (-overhang, y, 0.0)
            p_end = (total_x + overhang, y, 0.0)
            m = generate_tubular_mesh([p_start, p_end], diameter=dia, radial_segments=4)
            if "faces" in m:
                faces.extend(m["faces"])

            # Add octagonal bubble markers at both ends
            for cx in [-overhang - 0.35, total_x + overhang + 0.35]:
                bubble_poly = []
                r = 0.30
                for k in range(8):
                    ang = 2.0 * math.pi * k / 8.0
                    bubble_poly.append((cx + r * math.cos(ang), y + r * math.sin(ang), 0.005))
                faces.append(bubble_poly)

        if faces:
            self._commit_faces_to_scene(
                scene,
                viewport,
                faces,
                f"Created Grid Lines: {x_count}x{y_count} axes ({total_x:.1f}x{total_y:.1f}m)",
            )

    def _render_element_rebar_only(self, element: Any, scene: Any, viewport: Any) -> None:
        """Renders ONLY the 3D rebar cage faces of an element without re-adding concrete faces."""
        try:
            from chakkree_tools.rc.rebar_mesh import generate_rebar_cage
            rebar_cage = generate_rebar_cage(element)
            for item in rebar_cage:
                if "faces" in item and item["faces"]:
                    self._commit_faces_to_scene(
                        scene,
                        viewport,
                        item["faces"],
                        f"Rendered {getattr(element, 'id', 'Element')} Rebars",
                    )
        except Exception as e:
            print(f"[chakkree_tools] Notice rendering element rebars: {e}")

    def _render_column_to_scene(self, column: Any) -> None:
        """Renders 3D column concrete mesh & rebar cage faces into IngeTrazo active scene."""
        if not self.app:
            return
        try:
            scene, viewport = self._get_scene_and_viewport()
            if scene is None or not hasattr(scene, "mesh"):
                return
            width = float(getattr(column, "width", 0.30))
            depth = float(getattr(column, "depth", 0.30))
            height = float(getattr(column, "height", 3.50))
            pos = getattr(column, "position", (0.0, 0.0))
            z_bot = float(getattr(column, "elevation", 0.0))
            z_top = z_bot + height
            x, y = pos[0], pos[1]
            hw, hd = width / 2.0, depth / 2.0

            b0 = (x - hw, y - hd, z_bot)
            b1 = (x + hw, y - hd, z_bot)
            b2 = (x + hw, y + hd, z_bot)
            b3 = (x - hw, y + hd, z_bot)

            t0 = (x - hw, y - hd, z_top)
            t1 = (x + hw, y - hd, z_top)
            t2 = (x + hw, y + hd, z_top)
            t3 = (x - hw, y + hd, z_top)

            faces = [
                [b0, b3, b2, b1],
                [t0, t1, t2, t3],
                [b0, b1, t1, t0],
                [b1, b2, t2, t1],
                [b2, b3, t3, t2],
                [b3, b0, t0, t3],
            ]
            self._commit_faces_to_scene(scene, viewport, faces, f"Created RC Column {getattr(column, 'id', 'C1')} ({width}x{depth}m, H={height}m)")

            # Render 3D Rebar Cage if enabled
            if self.show_rebars:
                self._render_element_rebar_only(column, scene, viewport)
        except Exception as e:
            print(f"[chakkree_tools] Notice rendering column: {e}")

    def _render_footing_to_scene(self, footing: Any) -> None:
        """Renders 3D footing concrete mesh & rebar cage faces into IngeTrazo active scene."""
        if not self.app:
            return
        try:
            scene, viewport = self._get_scene_and_viewport()
            if scene is None or not hasattr(scene, "mesh"):
                return
            width = float(getattr(footing, "width", getattr(footing, "section_x", 1.20)))
            length = float(getattr(footing, "length", getattr(footing, "section_y", 1.20)))
            thickness = float(getattr(footing, "thickness", 0.60))
            pos = getattr(footing, "position", (0.0, 0.0))
            elevation = float(getattr(footing, "elevation", -0.70))
            z_top = elevation
            z_bot = elevation - thickness
            x, y = pos[0], pos[1]
            hw, hl = width / 2.0, length / 2.0

            b0 = (x - hw, y - hl, z_bot)
            b1 = (x + hw, y - hl, z_bot)
            b2 = (x + hw, y + hl, z_bot)
            b3 = (x - hw, y + hl, z_bot)

            t0 = (x - hw, y - hl, z_top)
            t1 = (x + hw, y - hl, z_top)
            t2 = (x + hw, y + hl, z_top)
            t3 = (x - hw, y + hl, z_top)

            faces = [
                [b0, b3, b2, b1],
                [t0, t1, t2, t3],
                [b0, b1, t1, t0],
                [b1, b2, t2, t1],
                [b2, b3, t3, t2],
                [b3, b0, t0, t3],
            ]
            self._commit_faces_to_scene(scene, viewport, faces, f"Created Footing {getattr(footing, 'id', 'F1')} ({width}x{length}m, T={thickness}m)")

            # Render 3D Rebar Cage if enabled
            if self.show_rebars:
                self._render_element_rebar_only(footing, scene, viewport)
        except Exception as e:
            print(f"[chakkree_tools] Notice rendering footing: {e}")

    def _render_beam_to_scene(self, beam: Any) -> None:
        """Renders 3D beam concrete mesh & rebar cage faces into IngeTrazo active scene."""
        if not self.app:
            return
        try:
            import math

            scene, viewport = self._get_scene_and_viewport()
            if scene is None or not hasattr(scene, "mesh"):
                return

            width = float(getattr(beam, "width", 0.20))
            depth = float(getattr(beam, "depth", 0.40))
            start = getattr(beam, "start_point", (0.0, 0.0))
            end = getattr(beam, "end_point", (4.0, 0.0))
            elevation = float(getattr(beam, "elevation", 3.20))

            dx = end[0] - start[0]
            dy = end[1] - start[1]
            L = math.hypot(dx, dy)
            if L < 1e-6:
                return

            nx = -dy / L * (width / 2.0)
            ny = dx / L * (width / 2.0)
            z_top = elevation
            z_bot = elevation - depth

            b0 = (start[0] + nx, start[1] + ny, z_bot)
            b1 = (end[0] + nx, end[1] + ny, z_bot)
            b2 = (end[0] - nx, end[1] - ny, z_bot)
            b3 = (start[0] - nx, start[1] - ny, z_bot)

            t0 = (start[0] + nx, start[1] + ny, z_top)
            t1 = (end[0] + nx, end[1] + ny, z_top)
            t2 = (end[0] - nx, end[1] - ny, z_top)
            t3 = (start[0] - nx, start[1] - ny, z_top)

            faces = [
                [b0, b3, b2, b1],  # bottom
                [t0, t1, t2, t3],  # top
                [b0, b1, t1, t0],  # side 1
                [b1, b2, t2, t1],  # end cap
                [b2, b3, t3, t2],  # side 2
                [b3, b0, t0, t3],  # start cap
            ]

            self._commit_faces_to_scene(scene, viewport, faces, f"Created RC Beam {getattr(beam, 'id', 'B1')} ({width}x{depth}m, L={L:.2f}m)")

            # Render 3D Rebar Cage if enabled
            if self.show_rebars:
                self._render_element_rebar_only(beam, scene, viewport)

            if hasattr(scene, "bump_view"):
                scene.bump_view()
            elif hasattr(scene, "version"):
                scene.version += 1

            if viewport is not None and hasattr(viewport, "update"):
                viewport.update()
            elif hasattr(self.app, "viewport") and hasattr(self.app.viewport, "update"):
                self.app.viewport.update()

            msg = f"Chakkree Tools: Created RC Beam {getattr(beam, 'id', 'B1')} ({width}x{depth}m, L={L:.2f}m)"
            if hasattr(self.app, "flash_status"):
                self.app.flash_status(msg)
            elif viewport is not None and hasattr(viewport, "flash_status"):
                viewport.flash_status(msg)
        except Exception as e:
            print(f"[chakkree_tools] Notice rendering beam: {e}")

    def _render_slab_to_scene(self, slab: Any) -> None:
        """Renders 3D slab concrete mesh & rebar cage faces into IngeTrazo active scene."""
        if not self.app:
            return
        try:
            scene, viewport = self._get_scene_and_viewport()
            if scene is None or not hasattr(scene, "mesh"):
                return
            boundary = getattr(slab, "boundary", [])
            if not boundary or len(boundary) < 3:
                return

            thickness = float(getattr(slab, "thickness", 0.10))
            elevation = float(getattr(slab, "elevation", 0.0))
            z_top = elevation
            z_bot = elevation - thickness

            n = len(boundary)
            top_pts = [(float(p[0]), float(p[1]), z_top) for p in boundary]
            bot_pts = [(float(p[0]), float(p[1]), z_bot) for p in reversed(boundary)]

            faces = [top_pts, bot_pts]

            # Side faces (vertical perimeter faces)
            for i in range(n):
                j = (i + 1) % n
                p_i = boundary[i]
                p_j = boundary[j]
                b0 = (float(p_i[0]), float(p_i[1]), z_bot)
                b1 = (float(p_j[0]), float(p_j[1]), z_bot)
                t1 = (float(p_j[0]), float(p_j[1]), z_top)
                t0 = (float(p_i[0]), float(p_i[1]), z_top)
                faces.append([b0, b1, t1, t0])

            self._commit_faces_to_scene(
                scene,
                viewport,
                faces,
                f"Created {getattr(slab, 'slab_type', 'RC')} Slab {getattr(slab, 'id', 'S1')} (T={thickness}m, Area={getattr(slab, 'area', 0.0):.2f} m2)",
            )

            # Render 3D Rebar Cage if enabled
            if self.show_rebars:
                self._render_element_rebar_only(slab, scene, viewport)
        except Exception as e:
            print(f"[chakkree_tools] Notice rendering slab: {e}")

    def cmd_create_sample_slab(self) -> Any:
        """Quickly creates a 4.0x4.0m slab and renders it into the 3D scene."""
        return self.cmd_create_slab(show_dialog=False)

    def cmd_create_sample_beam(self) -> Any:
        """Quickly creates a 4.0m RC beam (0.2x0.4m) and renders it into the 3D scene."""
        return self.cmd_create_beam(width=0.20, depth=0.40, length=4.0, show_dialog=False)

    def cmd_create_pile_cap(
        self, pile_count: int = 1, show_dialog: bool = True, parent: Optional[Any] = None
    ) -> Any:
        """
        Action to create Footing / Pile Cap. Opens FootingDialog if show_dialog is True and PySide6 is available.
        """
        if show_dialog:
            try:
                from PySide6.QtWidgets import QApplication, QDialog
                from chakkree_tools.ingetrazo_plugin.ui.footing_dialog import FootingDialog

                if QApplication.instance() is not None:
                    dlg = FootingDialog(parent=parent)
                    if dlg.exec() == QDialog.Accepted:
                        f = dlg.get_footing()
                        self.active_elements.append(f)
                        self._render_footing_to_scene(f)
                        return f
                    return None
            except ImportError:
                pass

        from chakkree_tools.rc.footing import PileCap
        f = PileCap.create_n_piles(
            id_str=f"F_{len(self.active_elements) + 1}",
            pile_count=pile_count,
        )
        self.active_elements.append(f)
        self._render_footing_to_scene(f)
        return f

    def cmd_create_column(
        self,
        width: float = 0.3,
        depth: float = 0.3,
        height: float = 3.5,
        show_dialog: bool = True,
        parent: Optional[Any] = None,
    ) -> Any:
        """
        Action to create RC Column. Opens ColumnDialog if show_dialog is True and PySide6 is available.
        """
        if show_dialog:
            try:
                from PySide6.QtWidgets import QApplication, QDialog
                from chakkree_tools.ingetrazo_plugin.ui.column_dialog import ColumnDialog

                if QApplication.instance() is not None:
                    dlg = ColumnDialog(parent=parent)
                    if dlg.exec() == QDialog.Accepted:
                        c = dlg.get_column()
                        self.active_elements.append(c)
                        self._render_column_to_scene(c)
                        return c
                    return None
            except ImportError:
                pass

        from chakkree_tools.rc.column import Column
        c = Column(
            id=f"C_{len(self.active_elements) + 1}",
            width=width,
            depth=depth,
            height=height,
        )
        self.active_elements.append(c)
        self._render_column_to_scene(c)
        return c

    def cmd_create_beam(
        self,
        width: float = 0.2,
        depth: float = 0.4,
        length: float = 4.0,
        show_dialog: bool = True,
        parent: Optional[Any] = None,
    ) -> Any:
        """
        Action to create RC Beam. Opens BeamDialog if show_dialog is True and PySide6 is available.
        """
        if show_dialog:
            try:
                from PySide6.QtWidgets import QApplication, QDialog
                from chakkree_tools.ingetrazo_plugin.ui.beam_dialog import BeamDialog

                if QApplication.instance() is not None:
                    dlg = BeamDialog(parent=parent)
                    if dlg.exec() == QDialog.Accepted:
                        b = dlg.get_beam()
                        self.active_elements.append(b)
                        self._render_beam_to_scene(b)
                        return b
                    return None
            except ImportError:
                pass

        from chakkree_tools.rc.beam import Beam
        b = Beam(
            id=f"B_{len(self.active_elements) + 1}",
            width=width,
            depth=depth,
            start_point=(0.0, 0.0),
            end_point=(length, 0.0),
        )
        self.active_elements.append(b)
        self._render_beam_to_scene(b)
        return b

    def cmd_create_slab(
        self,
        boundary: Optional[List[Any]] = None,
        show_dialog: bool = True,
        parent: Optional[Any] = None,
    ) -> Any:
        if show_dialog:
            try:
                from PySide6.QtWidgets import QApplication, QDialog
                from chakkree_tools.ingetrazo_plugin.ui.slab_dialog import SlabDialog

                if QApplication.instance() is not None:
                    win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                    if callable(win):
                        win = win()
                    dlg = SlabDialog(parent=win or parent)
                    if dlg.exec() == QDialog.Accepted:
                        s = dlg.get_slab()
                        self.active_elements.append(s)
                        self._render_slab_to_scene(s)
                        return s
                    return None
            except ImportError:
                pass

        from chakkree_tools.rc.slab import Slab
        s = Slab(
            id=f"SLAB_{len(self.active_elements) + 1}",
            boundary=boundary or [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
        )
        self.active_elements.append(s)
        self._render_slab_to_scene(s)
        return s

    def cmd_export_debim(
        self,
        output_path: Optional[Union[str, Path]] = None,
        parent: Optional[Any] = None,
    ) -> Optional[Path]:
        if output_path is None:
            try:
                from PySide6.QtWidgets import QApplication, QFileDialog
                if QApplication.instance() is not None:
                    win = parent or getattr(self.app, "window", getattr(self.app, "_window", None))
                    if callable(win):
                        win = win()
                    chosen_path, _ = QFileDialog.getSaveFileName(
                        win,
                        tr("Export Model to .debim"),
                        "chakkree_model.debim",
                        "debim Model (*.debim);;debim Manifest (*.debim.yaml);;All Files (*.*)",
                    )
                    if not chosen_path:
                        return None
                    output_path = chosen_path
                else:
                    output_path = "chakkree_model.debim"
            except ImportError:
                output_path = "chakkree_model.debim"

        from chakkree_tools.exporter.debim_exporter import export_to_debim
        grids_x = getattr(self, "grids_x", None)
        grids_y = getattr(self, "grids_y", None)
        res = export_to_debim(
            elements=self.active_elements,
            output_path=str(output_path),
            project_name="Chakkree Tools IngeTrazo Export",
            grids_x=grids_x,
            grids_y=grids_y,
            include_rebar_mesh=self.show_rebars,
        )
        if hasattr(self.app, "flash_status"):
            self.app.flash_status(tr("Exported .debim to {name}", name=Path(output_path).name))
        return res


def register_plugin(app: Optional[Any] = None) -> ChakkreeToolsPlugin:
    """
    Entry point function called by IngeTrazo plugin loader.
    """
    try:
        plugin = ChakkreeToolsPlugin(app=app)
    except Exception as e:
        print(f"[chakkree_tools] Error initializing plugin: {e}")
        plugin = ChakkreeToolsPlugin(app=None)
    if app is not None and hasattr(app, "register_tool"):
        app.register_tool(plugin)
    return plugin


def setup(app: Any) -> ChakkreeToolsPlugin:
    """
    Official setup(app) entry point called by IngeTrazo extension loader.
    Registers menus, actions, and the native PySide6 toolbar in IngeTrazo.
    """
    plugin = register_plugin(app)

    # 1. Register Menus under Extensions -> Chakkree Tools
    menu = None
    if hasattr(app, "add_menu") and callable(getattr(app, "add_menu")):
        menu = app.add_menu("Chakkree Tools")

    if menu is not None:
        menu.addAction(tr("Create Pile Cap (1-9 Piles)..."), lambda: plugin.cmd_create_pile_cap())
        menu.addAction(tr("Create RC Column (4-16 Bars)..."), lambda: plugin.cmd_create_column())
        menu.addAction(tr("Create RC Beam..."), lambda: plugin.cmd_create_beam())
        menu.addAction(tr("Create Slab (PS Plank / RC)..."), lambda: plugin.cmd_create_slab())
        menu.addSeparator()
        menu.addAction(tr("Show/Hide 3D Rebar Meshes"), lambda: plugin.cmd_toggle_rebars())
        menu.addAction(tr("Rebar Tools & Details..."), lambda: plugin.cmd_rebar_tools())
        menu.addAction(tr("Grid Lines..."), lambda: plugin.cmd_create_grids())
        menu.addAction(tr("Rebar Color Config..."), lambda: plugin.cmd_config_colors())
        menu.addSeparator()
        menu.addAction(tr("QTO Take-off Report..."), lambda: plugin.cmd_qto_takeoff())
        menu.addAction(tr("Export Model to .debim..."), lambda: plugin.cmd_export_debim())
        menu.addAction(tr("Live Stream to IngeTrazo (Port 8482)..."), lambda: plugin.cmd_stream_to_bridge())
        menu.addSeparator()
        menu.addAction(tr("Language..."), lambda: plugin.cmd_select_language())
        menu.addAction(tr("About Chakkree Tools..."), lambda: plugin.cmd_about())

    # Fallback only when submenu add_menu is not available
    elif hasattr(app, "add_menu_action"):
        app.add_menu_action(tr("Chakkree: Footings (Pile Cap)..."), lambda: plugin.cmd_create_pile_cap(), tip="Create Pile Cap / Footing")
        app.add_menu_action(tr("Chakkree: RC Columns..."), lambda: plugin.cmd_create_column(), tip="Create RC Column")
        app.add_menu_action(tr("Chakkree: RC Beams..."), lambda: plugin.cmd_create_beam(), tip="Create RC Beam")
        app.add_menu_action(tr("Chakkree: Slabs..."), lambda: plugin.cmd_create_slab(), tip="Create RC Slab")
        app.add_menu_action(tr("Chakkree: Show/Hide Rebars"), lambda: plugin.cmd_toggle_rebars(), tip="Toggle Show/Hide 3D Rebar Meshes")
        app.add_menu_action(tr("Chakkree: QTO Take-off..."), lambda: plugin.cmd_qto_takeoff(), tip="Automated BBS & Quantity Take-off")
        app.add_menu_action(tr("Chakkree: Export .debim..."), lambda: plugin.cmd_export_debim(), tip="Export to .debim manifest")
        app.add_menu_action(tr("Chakkree: Stream to Bridge (Port 8482)..."), lambda: plugin.cmd_stream_to_bridge(), tip="Stream to IngeTrazo port 8482")
        app.add_menu_action(tr("Chakkree: About..."), lambda: plugin.cmd_about(), tip="About Chakkree Tools")

    # 2. Register Toolbar on IngeTrazo main window
    win = getattr(app, "window", getattr(app, "_window", None))
    if callable(win):
        win = win()
    if win is None and hasattr(app, "viewport") and hasattr(app.viewport, "window"):
        win = app.viewport.window()
        if callable(win):
            win = win()

    if win is not None:
        try:
            from PySide6.QtWidgets import QToolBar
            from PySide6.QtGui import QIcon, QAction
            from PySide6.QtCore import Qt, QSize

            tb_id = "ChakkreeToolsToolbar"
            existing_tb = win.findChild(QToolBar, tb_id)
            if existing_tb is None:
                toolbar = QToolBar("Chakkree Tools", win)
                toolbar.setObjectName(tb_id)
                toolbar.setIconSize(QSize(24, 24))
                toolbar.setFloatable(True)
                toolbar.setMovable(True)
                toolbar.setAllowedAreas(Qt.AllToolBarAreas)

                icons_dir = Path(__file__).resolve().parent / "resources" / "icons"
                if not icons_dir.exists():
                    icons_dir = Path(__file__).resolve().parent.parent / "resources" / "icons"

                actions_data = [
                    ("RebarTools.svg", tr("Rebar Tools"), tr("Rebar Tools - Bend hooks and generate 3D reinforcement cages"), plugin.cmd_rebar_tools),
                    ("ToggleRebars.svg", tr("Show/Hide Rebars"), tr("Toggle Show/Hide 3D Rebar Meshes"), plugin.cmd_toggle_rebars),
                    ("FootingTools.svg", tr("Footings"), tr("Footing Tools - Parametric 1-9 pile caps and isolated footings"), plugin.cmd_create_pile_cap),
                    ("ColumnTools.svg", tr("Columns"), tr("Column Tools - Rectangular/Circular columns with 4-16 longitudinal bars"), plugin.cmd_create_column),
                    ("BeamTools.svg", tr("Beams"), tr("Beam Tools - Parametric RC beams with multi-zone stirrup spacing"), plugin.cmd_create_beam),
                    ("SlabTools.svg", tr("Slabs"), tr("Slab Tools - Precast plank and cast-in-place RC slabs"), plugin.cmd_create_slab),
                    (None, None, None, None),  # Separator
                    ("GridLine.svg", tr("Grid Lines"), tr("GridLine v2026 - Parametric X/Y grid axes and elevation levels"), plugin.cmd_create_grids),
                    ("TakeOff.svg", tr("QTO Take-off"), tr("Quantity Take-off - Concrete volume, formwork, and Bar Bending Schedule"), plugin.cmd_qto_takeoff),
                    ("AnalysisTool.svg", tr("Export .debim"), tr("RC Analysis - Export model to .debim for OpenBIM / debim CLI"), plugin.cmd_export_debim),
                    (None, None, None, None),  # Separator
                    ("ConfigColorRebar.svg", tr("Config Colors"), tr("Config Colors - Rebar color customization by diameter (RB6-DB32)"), plugin.cmd_config_colors),
                    ("About.svg", tr("About"), tr("About Chakkree Tools (Python Edition) © Chakkree Tiyawongsuwan"), plugin.cmd_about),
                ]

                for item in actions_data:
                    icon_name, label, tooltip, callback = item
                    if icon_name is None:
                        toolbar.addSeparator()
                        continue
                    icon_file = icons_dir / icon_name
                    action = QAction(label, toolbar)
                    if icon_file.exists():
                        action.setIcon(QIcon(str(icon_file)))
                    if tooltip:
                        action.setToolTip(tooltip)
                    if callback:
                        action.triggered.connect(lambda _c=False, cb=callback: cb())
                    toolbar.addAction(action)

                win.addToolBar(Qt.TopToolBarArea, toolbar)
        except Exception as e:
            print(f"[chakkree_tools] Notice: Could not register toolbar: {e}")

    return plugin
