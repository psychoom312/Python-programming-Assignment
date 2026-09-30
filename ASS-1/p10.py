import sys
import os
import json
import csv
import re
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

DATA_FILE = "assignment_tracker_data.json"

class AssignmentTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Assignment Tracker")
        self.geometry("1000x650")
        self.minsize(900, 550)
        
        # Core data storage structures
        self.students = {}       # enrollment -> student_name
        self.submissions = []     # list of dicts: {enrollment, name, assignment, status, marks, remarks}
        
        self.load_data()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # 1. Main UI Layout Definition
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel Framework: Control and Inputs
        left_panel = ttk.Frame(main_paned, width=320)
        main_paned.add(left_panel, weight=0)
        
        # Right Panel Framework: Data View and Filtering Options
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=1)
        
        # ----------------- LEFT PANEL: INPUT FORMS -----------------
        # Student Registration Section
        student_frame = ttk.LabelFrame(left_panel, text=" Register Student ", padding=10)
        student_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(student_frame, text="Enrollment ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_stud_id = ttk.Entry(student_frame)
        self.ent_stud_id.grid(row=0, column=1, fill=tk.X, expand=True, pady=2)
        
        ttk.Label(student_frame, text="Student Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ent_stud_name = ttk.Entry(student_frame)
        self.ent_stud_name.grid(row=1, column=1, fill=tk.X, expand=True, pady=2)
        
        btn_add_student = ttk.Button(student_frame, text="Add Student", command=self.add_student)
        btn_add_student.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky=tk.EW)
        
        # Submission Intake Section
        sub_frame = ttk.LabelFrame(left_panel, text=" Log Submission / Marks Update ", padding=10)
        sub_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(sub_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cmb_sub_id = ttk.Combobox(sub_frame, postcommand=self.update_student_combobox, state="readonly")
        self.cmb_sub_id.grid(row=0, column=1, fill=tk.X, expand=True, pady=2)
        
        ttk.Label(sub_frame, text="Assignment:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cmb_assign = ttk.Combobox(sub_frame, values=[f"Assignment {i}" for i in range(1, 11)], state="readonly")
        self.cmb_assign.grid(row=1, column=1, fill=tk.X, expand=True, pady=2)
        self.cmb_assign.set("Assignment 1")
        
        ttk.Label(sub_frame, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.var_status = tk.StringVar(value="Completed")
        rad_comp = ttk.Radiobutton(sub_frame, text="Completed", value="Completed", variable=self.var_status, command=self.toggle_marks_state)
        rad_pend = ttk.Radiobutton(sub_frame, text="Pending", value="Pending", variable=self.var_status, command=self.toggle_marks_state)
        rad_comp.grid(row=2, column=1, sticky=tk.W, pady=2)
        rad_pend.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(sub_frame, text="Marks (Max 100):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.ent_marks = ttk.Entry(sub_frame)
        self.ent_marks.grid(row=4, column=1, fill=tk.X, expand=True, pady=2)
        
        ttk.Label(sub_frame, text="Remarks:").grid(row=5, column=0, sticky=tk.NW, pady=2)
        self.txt_remarks = tk.Text(sub_frame, height=4, width=20)
        self.txt_remarks.grid(row=5, column=1, fill=tk.BOTH, expand=True, pady=2)
        
        btn_save_sub = ttk.Button(sub_frame, text="Save / Update Record", command=self.save_submission)
        btn_save_sub.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky=tk.EW)
        
        # ----------------- RIGHT PANEL: DATA DISPLAY & TOOLS -----------------
        # Dynamic Filtration Control Section
        filter_frame = ttk.LabelFrame(right_panel, text=" Live Workspace Filter Controls ", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Show Status:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.cmb_filter_status = ttk.Combobox(filter_frame, values=["All Statuses", "Completed", "Pending"], state="readonly", width=15)
        self.cmb_filter_status.grid(row=0, column=1, padx=(0, 15))
        self.cmb_filter_status.set("All Statuses")
        self.cmb_filter_status.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        ttk.Label(filter_frame, text="Search Term:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.ent_search = ttk.Entry(filter_frame, width=25)
        self.ent_search.grid(row=0, column=3, padx=(0, 10))
        self.ent_search.bind("<KeyRelease>", lambda e: self.refresh_table())
        
        btn_export = ttk.Button(filter_frame, text="Export CSV Report", command=self.export_csv)
        btn_export.grid(row=0, column=4, padx=(20, 0), sticky=tk.E)
        
        # High-Performance Virtual Treeview List Component
        table_frame = ttk.Frame(right_panel)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("enrollment", "name", "assignment", "status", "marks", "remarks")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("enrollment", text="Enrollment ID", command=lambda: self.sort_table("enrollment"))
        self.tree.heading("name", text="Student Name", command=lambda: self.sort_table("name"))
        self.tree.heading("assignment", text="Assignment", command=lambda: self.sort_table("assignment"))
        self.tree.heading("status", text="Status", command=lambda: self.sort_table("status"))
        self.tree.heading("marks", text="Marks", command=lambda: self.sort_table("marks"))
        self.tree.heading("remarks", text="Remarks", command=lambda: self.sort_table("remarks"))
        
        self.tree.column("enrollment", width=100, anchor=tk.CENTER)
        self.tree.column("name", width=150, anchor=tk.W)
        self.tree.column("assignment", width=120, anchor=tk.CENTER)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        self.tree.column("marks", width=80, anchor=tk.CENTER)
        self.tree.column("remarks", width=250, anchor=tk.W)
        
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        scroll_y.grid(row=0, column=1, sticky=tk.NS)
        scroll_x.grid(row=1, column=0, sticky=tk.EW)
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
        
        # Status Monitoring Footer Bar
        self.lbl_status_bar = ttk.Label(right_panel, text="Records Loaded: 0", font=(None, 9, "italic"))
        self.lbl_status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Sort state tracking variables
        self.sort_ascending = True
        self.last_sort_col = None

    # ----------------- ENGINE OPERATIONS & ACTION CONTROLS -----------------
    def toggle_marks_state(self):
        if self.var_status.get() == "Pending":
            self.ent_marks.delete(0, tk.END)
            self.ent_marks.configure(state="disabled")
        else:
            self.ent_marks.configure(state="normal")

    def update_student_combobox(self):
        # Dynamically updates drop-down list entries cleanly
        sorted_ids = sorted(self.students.keys())
        self.cmb_sub_id['values'] = [f"{sid} - {self.students[sid]}" for sid in sorted_ids]

    def add_student(self):
        sid = self.ent_stud_id.get().strip()
        name = self.ent_stud_name.get().strip()
        
        if not re.match(r'^[a-zA-Z0-9_\-]+$', sid):
            messagebox.showerror("Validation Error", "Enrollment ID must contain only alphanumeric characters, dashes, or underscores.")
            return
        if not name:
            messagebox.showerror("Validation Error", "Student Name cannot be empty.")
            return
            
        if sid in self.students:
            messagebox.showwarning("Duplicate Registration", f"Student with ID '{sid}' is already registered.")
            return
            
        self.students[sid] = name
        self.save_data()
        self.update_student_combobox()
        
        self.ent_stud_id.delete(0, tk.END)
        self.ent_stud_name.delete(0, tk.END)
        messagebox.showinfo("Success", f"Successfully registered student: {name}")

    def save_submission(self):
        selected_student = self.cmb_sub_id.get()
        if not selected_student:
            messagebox.showerror("Validation Error", "Please select a registered student ID.")
            return
            
        enrollment = selected_student.split(" - ")[0]
        name = self.students[enrollment]
        assignment = self.cmb_assign.get()
        status = self.var_status.get()
        remarks = self.txt_remarks.get("1.0", tk.END).strip()
        
        marks = ""
        if status == "Completed":
            marks_str = self.ent_marks.get().strip()
            try:
                marks_val = float(marks_str)
