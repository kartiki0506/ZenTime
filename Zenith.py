import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
import math

# --- CONFIGURATION & THEME ---
DATA_FILE = "weekly_timetable.json"
COLORS = {
    "bg": "#F4F6F9",            # Light Grey Background
    "sidebar": "#2C3E50",       # Dark Blue Sidebar
    "sidebar_hover": "#34495E",
    "accent": "#3498DB",        # Bright Blue
    "text": "#2C3E50",
    "white": "#FFFFFF",
    "danger": "#E74C3C",        # Red
    "success": "#2ECC71",       # Green
    "warning": "#F1C40F",       # Yellow
    "card_bg": "#FFFFFF"
}

# --- HELPER FUNCTIONS ---
def time_to_min(t_str):
    """Convert HH:MM string to minutes from midnight."""
    try:
        t = datetime.strptime(t_str, "%H:%M")
        return t.hour * 60 + t.minute
    except:
        return 0

def min_to_time(mins):
    """Convert minutes from midnight to HH:MM."""
    h = int(mins // 60)
    m = int(mins % 60)
    return f"{h:02d}:{m:02d}"

# --- CORE APPLICATION ---
class ModernTimetableApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚀 Zenith - Smart Scheduler")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(bg=COLORS["bg"])
        
        # Data Storage
        self.weekly_data = self.load_data()
        self.current_view_date = datetime.now().strftime("%d-%m-%Y")
        self.current_view_day = datetime.now().strftime("%A")

        # Setup Styles
        self._setup_styles()

        # Layout: Sidebar + Main Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_sidebar()
        self._create_main_area()
        
        # Default Page
        self.show_dashboard()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # General
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["white"], relief="flat")
        
        # Labels
        style.configure("Header.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 24, "bold"))
        style.configure("SubHeader.TLabel", background=COLORS["white"], foreground=COLORS["text"], font=("Segoe UI", 14, "bold"))
        style.configure("Body.TLabel", background=COLORS["white"], foreground="#555", font=("Segoe UI", 11))
        
        # Buttons
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, focuscolor=COLORS["accent"])
        style.map("Accent.TButton", background=[("active", "#2980B9")])
        
        style.configure("Danger.TButton", background=COLORS["danger"], foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        
        # Inputs
        style.configure("TEntry", padding=5, relief="flat")
        style.configure("TCombobox", padding=5)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.weekly_data, f, indent=2)

    # --- UI LAYOUTS ---
    def _create_sidebar(self):
        sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=250)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo
        tk.Label(sidebar, text="ZENITH", bg=COLORS["sidebar"], fg="white", font=("Segoe UI", 22, "bold")).pack(pady=40)

        # Nav Buttons
        self.nav_btns = {}
        opts = [("📊 Dashboard", self.show_dashboard), 
                ("✍️ Editor", self.show_editor), 
                ("📈 Analytics", self.show_analytics)]
        
        for text, cmd in opts:
            btn = tk.Button(sidebar, text=text, bg=COLORS["sidebar"], fg="#BDC3C7", 
                            font=("Segoe UI", 12), bd=0, cursor="hand2",
                            activebackground=COLORS["sidebar_hover"], activeforeground="white",
                            command=cmd, anchor="w", padx=20, pady=10)
            btn.pack(fill="x", pady=2)
            self.nav_btns[text] = btn

        # Footer
        tk.Label(sidebar, text="v2.0 Pro", bg=COLORS["sidebar"], fg="#7F8C8D", font=("Segoe UI", 9)).pack(side="bottom", pady=20)

    def _create_main_area(self):
        self.main_frame = tk.Frame(self, bg=COLORS["bg"])
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def set_active_nav(self, name):
        for key, btn in self.nav_btns.items():
            if name in key:
                btn.config(bg=COLORS["sidebar_hover"], fg="white")
            else:
                btn.config(bg=COLORS["sidebar"], fg="#BDC3C7")

    # ================= DASHBOARD (TIMELINE) =================
    def show_dashboard(self):
        self.clear_main()
        self.set_active_nav("Dashboard")
        
        # Header
        top_bar = tk.Frame(self.main_frame, bg=COLORS["bg"])
        top_bar.pack(fill="x", pady=(0, 20))
        ttk.Label(top_bar, text="Today's Timeline", style="Header.TLabel").pack(side="left")
        
        # Date Selector (Simple wrapper for demo)
        day_key = f"{self.current_view_day} {self.current_view_date}"
        ttk.Label(top_bar, text=f"Viewing: {day_key}", font=("Segoe UI", 12), background=COLORS["bg"]).pack(side="right", padx=10)

        if day_key not in self.weekly_data:
            self.render_empty_state(day_key)
            return

        data = self.weekly_data[day_key]
        schedule = self.calculate_schedule(data)

        # Statistics Summary
        stats_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        stats_frame.pack(fill="x", pady=(0, 20))
        
        total_tasks = len([x for x in schedule if x['type'] == 'Task'])
        completed = len([x for x in schedule if x['type'] == 'Task' and x.get('completed')])
        
        self.create_stat_card(stats_frame, "Total Events", str(len(schedule)), COLORS["accent"], 0)
        self.create_stat_card(stats_frame, "Tasks Done", f"{completed}/{total_tasks}", COLORS["success"], 1)
        self.create_stat_card(stats_frame, "Day Status", self.get_day_mood(data.get('tasks',[])), COLORS["warning"], 2)

        # Scrollable Canvas for Timeline
        canvas_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_inner = tk.Frame(canvas, bg="white")
        
        scrollable_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_inner, anchor="nw", width=950) # Adjust width for scroll
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Draw Timeline
        self.draw_timeline(scrollable_inner, schedule, day_key)

    def create_stat_card(self, parent, title, value, color, col_idx):
        card = tk.Frame(parent, bg="white", padx=20, pady=15)
        card.grid(row=0, column=col_idx, padx=10, sticky="ew")
        parent.grid_columnconfigure(col_idx, weight=1)
        
        tk.Label(card, text=title, font=("Segoe UI", 10), fg="#7f8c8d", bg="white").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 20, "bold"), fg=color, bg="white").pack(anchor="w")
        # Strip
        tk.Frame(card, bg=color, height=3).pack(fill="x", pady=(10,0))

    def draw_timeline(self, parent, schedule, day_key):
        # Sort by time
        schedule.sort(key=lambda x: x['start_min'])
        
        for item in schedule:
            row = tk.Frame(parent, bg="white", pady=5)
            row.pack(fill="x")
            
            # Color Coding
            bg_c = "#ECF0F1" # Default gray
            border_c = "#BDC3C7"
            if item['type'] == "Class": bg_c, border_c = "#E8F6F3", "#1ABC9C"
            elif item['type'] == "Meal": bg_c, border_c = "#FEF9E7", "#F1C40F"
            elif item['type'] == "Task": bg_c, border_c = "#EBF5FB", "#3498DB"

            # Time Block
            time_box = tk.Frame(row, bg=bg_c, width=80, height=50)
            time_box.pack(side="left", padx=(0, 15))
            time_box.pack_propagate(False)
            tk.Label(time_box, text=item['start'], font=("Segoe UI", 10, "bold"), bg=bg_c, fg="#2C3E50").pack(expand=True)

            # Details Block (Visual Card)
            card = tk.Frame(row, bg="white", highlightbackground=border_c, highlightthickness=1, highlightcolor=border_c, padx=10, pady=10)
            card.pack(side="left", fill="x", expand=True)
            
            # Title & Type
            header = tk.Frame(card, bg="white")
            header.pack(fill="x")
            tk.Label(header, text=item['name'], font=("Segoe UI", 12, "bold"), bg="white", fg="#2C3E50").pack(side="left")
            
            # Checkbox for tasks
            if item['type'] == 'Task':
                var = tk.BooleanVar(value=item.get('completed', False))
                chk = ttk.Checkbutton(header, variable=var, command=lambda v=var, n=item['name']: self.toggle_task(day_key, n, v))
                chk.pack(side="right")
            
            # Subtext
            dur = f"{item['end']} ({item['duration']}m)"
            tk.Label(card, text=f"{item['type']} • {dur}", font=("Segoe UI", 10), bg="white", fg="#7F8C8D").pack(anchor="w")

    def toggle_task(self, day_key, task_name, var):
        data = self.weekly_data[day_key]
        for t in data['tasks']:
            if t['name'] == task_name:
                t['completed'] = var.get()
        self.save_data()
        # Refresh stats only (lazy reload)
        self.after(100, self.show_dashboard)

    # ================= EDITOR (INPUT) =================
    def show_editor(self):
        self.clear_main()
        self.set_active_nav("Editor")
        
        # Container
        container = tk.Frame(self.main_frame, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        
        # --- Left Panel (Controls) ---
        left_panel = ttk.Frame(container, style="Card.TFrame", padding=20)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_panel, text="📅 Setup Day", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 15))
        
        # Date Inputs
        f_date = tk.Frame(left_panel, bg="white")
        f_date.pack(fill="x", pady=5)
        self.day_var = ttk.Combobox(f_date, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], width=12)
        self.day_var.set(self.current_view_day)
        self.day_var.pack(side="left", padx=(0,5))
        
        self.date_var = ttk.Entry(f_date, width=15)
        self.date_var.insert(0, self.current_view_date)
        self.date_var.pack(side="left")
        
        ttk.Button(f_date, text="Load/Create", style="Accent.TButton", command=self.load_editor_data).pack(side="left", padx=10)

        # Tabs for adding content
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill="both", expand=True, pady=20)
        
        # Task Tab
        tab_task = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        notebook.add(tab_task, text="  + Add Task  ")
        
        ttk.Label(tab_task, text="Task Name", background="white").pack(anchor="w")
        self.e_task = ttk.Entry(tab_task, width=30); self.e_task.pack(fill="x", pady=5)
        
        ttk.Label(tab_task, text="Duration (min)", background="white").pack(anchor="w")
        self.e_dur = ttk.Entry(tab_task, width=30); self.e_dur.pack(fill="x", pady=5)
        
        ttk.Label(tab_task, text="Priority", background="white").pack(anchor="w")
        self.e_prio = ttk.Combobox(tab_task, values=["High", "Medium", "Low"], state="readonly")
        self.e_prio.set("Medium"); self.e_prio.pack(fill="x", pady=5)
        
        ttk.Button(tab_task, text="Add to List", style="Accent.TButton", command=self.add_task_to_mem).pack(pady=15, fill="x")

        # Class Tab
        tab_class = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        notebook.add(tab_class, text="  + Add Class/Fixed  ")
        
        ttk.Label(tab_class, text="Event Name", background="white").pack(anchor="w")
        self.e_cls = ttk.Entry(tab_class); self.e_cls.pack(fill="x", pady=5)
        
        f_time = tk.Frame(tab_class, bg="white")
        f_time.pack(fill="x")
        ttk.Label(f_time, text="Start (HH:MM)", background="white").pack(side="left")
        ttk.Label(f_time, text="End (HH:MM)", background="white").pack(side="right")
        
        f_time_inp = tk.Frame(tab_class, bg="white")
        f_time_inp.pack(fill="x", pady=5)
        self.e_start = ttk.Entry(f_time_inp, width=10); self.e_start.pack(side="left")
        self.e_end = ttk.Entry(f_time_inp, width=10); self.e_end.pack(side="right")
        
        ttk.Button(tab_class, text="Add Fixed Event", style="Accent.TButton", command=self.add_class_to_mem).pack(pady=15, fill="x")

        # --- Right Panel (Preview) ---
        right_panel = ttk.Frame(container, style="Card.TFrame", padding=20)
        right_panel.pack(side="right", fill="both", expand=True)
        
        ttk.Label(right_panel, text="Draft Items", style="SubHeader.TLabel").pack(anchor="w")
        
        self.draft_list = tk.Listbox(right_panel, font=("Segoe UI", 11), bd=0, bg="#ECF0F1", highlightthickness=0, activestyle="none")
        self.draft_list.pack(fill="both", expand=True, pady=15)
        
        btn_row = tk.Frame(right_panel, bg="white")
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Remove Selected", style="Danger.TButton", command=self.remove_draft_item).pack(side="left")
        ttk.Button(btn_row, text="💾 Save & Generate", style="Accent.TButton", command=self.save_draft).pack(side="right")

        # Temporary storage for editor
        self.editor_data = {"tasks": [], "classes": [], "meals": {}}

    def load_editor_data(self):
        key = f"{self.day_var.get()} {self.date_var.get()}"
        self.editor_data = {"tasks": [], "classes": [], "meals": {}}
        
        # Default Meals
        self.editor_data["meals"] = {"Breakfast": "09:00", "Lunch": "13:00", "Dinner": "20:00"}
        
        if key in self.weekly_data:
            # Load existing
            existing = self.weekly_data[key]
            self.editor_data["tasks"] = existing.get("tasks", [])
            self.editor_data["classes"] = existing.get("classes", [])
            if "meals" in existing: self.editor_data["meals"] = existing["meals"]
        
        self.refresh_draft_list()
        messagebox.showinfo("Loaded", f"Loaded data for {key}")

    def add_task_to_mem(self):
        n = self.e_task.get(); d = self.e_dur.get(); p = self.e_prio.get()
        if n and d:
            self.editor_data["tasks"].append({"name": n, "duration": int(d), "priority": p, "completed": False})
            self.e_task.delete(0, tk.END); self.e_dur.delete(0, tk.END)
            self.refresh_draft_list()

    def add_class_to_mem(self):
        n = self.e_cls.get(); s = self.e_start.get(); e = self.e_end.get()
        if n and s and e:
            self.editor_data["classes"].append({"name": n, "start": s, "end": e})
            self.e_cls.delete(0, tk.END); self.e_start.delete(0, tk.END); self.e_end.delete(0, tk.END)
            self.refresh_draft_list()

    def refresh_draft_list(self):
        self.draft_list.delete(0, tk.END)
        for c in self.editor_data["classes"]:
            self.draft_list.insert(tk.END, f"🔒 {c['name']} ({c['start']}-{c['end']})")
        for t in self.editor_data["tasks"]:
            self.draft_list.insert(tk.END, f"📝 {t['name']} ({t['duration']}m) [{t['priority']}]")

    def remove_draft_item(self):
        sel = self.draft_list.curselection()
        if not sel: return
        idx = sel[0]
        n_classes = len(self.editor_data["classes"])
        if idx < n_classes:
            self.editor_data["classes"].pop(idx)
        else:
            self.editor_data["tasks"].pop(idx - n_classes)
        self.refresh_draft_list()

    def save_draft(self):
        key = f"{self.day_var.get()} {self.date_var.get()}"
        self.weekly_data[key] = self.editor_data
        self.save_data()
        
        # Update global view vars
        self.current_view_day = self.day_var.get()
        self.current_view_date = self.date_var.get()
        
        messagebox.showinfo("Saved", "Timetable generated successfully!")
        self.show_dashboard()

    # ================= ANALYTICS =================
    def show_analytics(self):
        self.clear_main()
        self.set_active_nav("Analytics")
        
        ttk.Label(self.main_frame, text="Time Distribution", style="Header.TLabel").pack(pady=20)
        
        key = f"{self.current_view_day} {self.current_view_date}"
        if key not in self.weekly_data:
            self.render_empty_state(key)
            return

        data = self.weekly_data[key]
        schedule = self.calculate_schedule(data)
        
        # Calculate totals (minutes)
        totals = {"Class": 0, "Task": 0, "Meal": 0, "Free": 0}
        day_minutes = 24 * 60
        occupied = 0
        
        for item in schedule:
            dur = item['duration']
            totals[item['type']] += dur
            occupied += dur
            
        totals["Free"] = max(0, (14 * 60) - occupied) # Assuming 14 hour active day for chart
        
        # Draw Pie Chart using Canvas
        canvas = tk.Canvas(self.main_frame, bg=COLORS["bg"], width=400, height=400, highlightthickness=0)
        canvas.pack()
        
        colors_map = {"Class": "#1ABC9C", "Task": "#3498DB", "Meal": "#F1C40F", "Free": "#BDC3C7"}
        start_deg = 0
        total_val = sum(totals.values())
        
        legend_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        legend_frame.pack(pady=20)

        for cat, val in totals.items():
            if val > 0:
                extent = (val / total_val) * 360
                canvas.create_arc(50, 50, 350, 350, start=start_deg, extent=extent, fill=colors_map[cat], outline="white")
                start_deg += extent
                
                # Legend
                lbl = tk.Label(legend_frame, text=f" {cat}: {val//60}h {val%60}m ", bg=COLORS["bg"], fg=colors_map[cat], font=("Segoe UI", 12, "bold"))
                lbl.pack(side="left", padx=10)

    # ================= LOGIC & UTILS =================
    def calculate_schedule(self, data):
        """
        Smart Algorithm:
        1. Place fixed events (Classes, Meals).
        2. Identify gaps.
        3. Fit tasks into gaps.
        """
        timeline = []
        
        # 1. Fixed Events
        for c in data.get("classes", []):
            s, e = time_to_min(c["start"]), time_to_min(c["end"])
            timeline.append({"name": c["name"], "start_min": s, "end_min": e, "type": "Class", "duration": e-s})
            
        for m, t in data.get("meals", {}).items():
            s = time_to_min(t)
            timeline.append({"name": m, "start_min": s, "end_min": s+45, "type": "Meal", "duration": 45})

        timeline.sort(key=lambda x: x['start_min'])
        
        # 2. Place Tasks
        tasks = sorted(data.get("tasks", []), key=lambda x: {"High": 0, "Medium": 1, "Low": 2}[x["priority"]])
        
        # Define active day range (e.g., 08:00 to 23:00)
        day_start = 8 * 60
        day_end = 23 * 60
        
        for task in tasks:
            t_dur = task["duration"] # already in minutes in new editor logic? let's ensure
            # Note: Old editor saved hours, new saves minutes. Let's handle both.
            if t_dur < 10: t_dur = t_dur * 60 # Assume hours if small number
            
            placed = False
            current_pointer = day_start
            
            # Try to find a gap
            for i in range(len(timeline) + 1):
                # Determine gap window
                gap_start = current_pointer
                if i < len(timeline):
                    gap_end = timeline[i]['start_min']
                    next_event_end = timeline[i]['end_min']
                else:
                    gap_end = day_end
                    next_event_end = day_end # End of loop
                
                if gap_end - gap_start >= t_dur:
                    # Found space!
                    timeline.append({
                        "name": task["name"],
                        "start_min": gap_start,
                        "end_min": gap_start + t_dur,
                        "type": "Task",
                        "duration": t_dur,
                        "completed": task.get("completed", False)
                    })
                    placed = True
                    timeline.sort(key=lambda x: x['start_min'])
                    break
                
                current_pointer = max(current_pointer, next_event_end)
                
        # Add formatted time strings
        for item in timeline:
            item['start'] = min_to_time(item['start_min'])
            item['end'] = min_to_time(item['end_min'])
            
        return timeline

    def get_day_mood(self, tasks):
        score = sum({"High": 3, "Medium": 2, "Low": 1}.get(t["priority"], 1) for t in tasks)
        if score >= 12: return "🔥 Intense"
        elif score >= 6: return "⚖️ Balanced"
        else: return "🍃 Chill"

    def render_empty_state(self, day_key):
        f = tk.Frame(self.main_frame, bg=COLORS["bg"])
        f.pack(expand=True)
        tk.Label(f, text="💤", font=("Segoe UI", 60), bg=COLORS["bg"]).pack()
        tk.Label(f, text="No schedule found for this day.", font=("Segoe UI", 16), bg=COLORS["bg"], fg="#95a5a6").pack(pady=10)
        ttk.Button(f, text="Create Schedule", style="Accent.TButton", command=self.show_editor).pack(pady=10)

if __name__ == "__main__":
    app = ModernTimetableApp()
    app.mainloop()

