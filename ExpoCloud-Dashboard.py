import customtkinter as ctk
import subprocess
import threading
import sys
import os
import time 
import aws_status  

VOLUME_ID = "vol-03e00b448d1d656f9" 
INSTANCE_NAME = "ExpoDev"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DevDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(" AWS DevOps Dashboard")
        self.geometry("850x650")
        self.last_updated_time = 0  
        
        self.label_title = ctk.CTkLabel(self, text="Cloud Environment Manager", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=(20, 10))

        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(pady=10, padx=20, fill="x")

        self.ec2_label = ctk.CTkLabel(self.status_frame, text="EC2 Status: Unknown", font=ctk.CTkFont(size=14))
        self.ec2_label.pack(side="left", padx=20, pady=10)

        self.ebs_label = ctk.CTkLabel(self.status_frame, text="EBS Status: Unknown", font=ctk.CTkFont(size=14))
        self.ebs_label.pack(side="left", padx=20, pady=10)

        self.btn_refresh = ctk.CTkButton(self.status_frame, text=" Refresh Status", width=120, fg_color="#E67E22", hover_color="#D35400", command=self.update_status_thread)
        self.btn_refresh.pack(side="right", padx=10, pady=10)

        self.time_label = ctk.CTkLabel(self.status_frame, text="Last updated: Just now", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        self.time_label.pack(side="right", padx=10, pady=10)

        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(pady=10)

        self.btn_start = ctk.CTkButton(self.actions_frame, text=" START DEV", width=180, height=45, fg_color="#27AE60", hover_color="#2ECC71", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: self.run_script("Start-Dev.py"))
        self.btn_start.pack(side="left", padx=15)

        self.btn_stop = ctk.CTkButton(self.actions_frame, text=" STOP DEV", width=180, height=45, fg_color="#C0392B", hover_color="#E74C3C", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: self.run_script("Stop-Dev.py"))
        self.btn_stop.pack(side="right", padx=15)

        self.terminal_label = ctk.CTkLabel(self, text="Terminal Output:", font=ctk.CTkFont(size=14, weight="bold"))
        self.terminal_label.pack(anchor="w", padx=20, pady=(15, 0))

        self.terminal_box = ctk.CTkTextbox(self, width=800, height=300, font=ctk.CTkFont(family="Consolas", size=13), text_color="#00FF00", fg_color="#1E1E1E")
        self.terminal_box.pack(pady=10, padx=20, fill="both", expand=True)
        self.terminal_box.insert("0.0", "Welcome to AWS Dashboard! Ready to execute commands...\n")

        self.update_timer()
        self.update_status_thread()

    def update_timer(self):
        if self.last_updated_time > 0:
            diff = int(time.time() - self.last_updated_time)
            if diff < 60:
                self.time_label.configure(text=f"Last updated: {diff} sec ago")
            else:
                mins = diff // 60
                self.time_label.configure(text=f"Last updated: {mins} min ago")
        self.after(1000, self.update_timer)

    def update_status_thread(self):
        self.ec2_label.configure(text="EC2 Status: Fetching...")
        self.ebs_label.configure(text="EBS Status: Fetching...")
        threading.Thread(target=self._fetch_aws_data, daemon=True).start()

    def _fetch_aws_data(self):
        ec2_res = aws_status.get_ec2_state(INSTANCE_NAME)
        ebs_res = aws_status.get_ebs_state(VOLUME_ID)
        self.after(0, self._apply_aws_data, ec2_res, ebs_res)

    def _apply_aws_data(self, ec2_res, ebs_res):
        self.ec2_label.configure(text=f"EC2: {ec2_res}")
        self.ebs_label.configure(text=f"EBS: {ebs_res}")
        self.last_updated_time = time.time()
        self.log_to_terminal("[INFO] Fetched latest status from AWS.")

    def log_to_terminal(self, text):
        self.terminal_box.insert("end", text + "\n")
        self.terminal_box.see("end") 

    def run_script(self, script_name):
        if not os.path.exists(script_name):
            self.log_to_terminal(f"[ERROR] File '{script_name}' not found!")
            return

        self.log_to_terminal(f"\n[{script_name}] >> Starting execution...")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="disabled")

        threading.Thread(target=self._execute_and_read, args=(script_name,), daemon=True).start()

    def _execute_and_read(self, script_name):
        process = subprocess.Popen(["python", "-u", script_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)        
        for line in iter(process.stdout.readline, ''):
            if line:
                self.after(0, self.log_to_terminal, line.strip())

        process.stdout.close()
        process.wait()
        
        self.after(0, self.log_to_terminal, f"[{script_name}] >> Execution finished.")
        self.after(0, lambda: self.btn_start.configure(state="normal"))
        self.after(0, lambda: self.btn_stop.configure(state="normal"))
        self.after(0, self.update_status_thread)

if __name__ == "__main__":
    app = DevDashboard()
    app.mainloop()