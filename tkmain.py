"""
@author: Team Mizogg
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser
import os
import glob
import subprocess
import webbrowser
import signal
import platform
import multiprocessing
import threading
import queue
import configparser
from datetime import datetime

class ConsoleWindow(ttk.Frame):
    def __init__(self, parent, title="Console"):
        super().__init__(parent)
        self.title = title
        self.output_queue = queue.Queue()
        self.setup_ui()
        self.after(100, self.check_queue)

    def setup_ui(self):
        # Create text widget with scrollbar
        self.text = tk.Text(self, wrap=tk.WORD, height=10, width=50, bg='black', fg='white')
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def append_output(self, text):
        self.output_queue.put(text)

    def check_queue(self):
        try:
            while True:
                text = self.output_queue.get_nowait()
                self.text.insert(tk.END, text + "\n")
                self.text.see(tk.END)
                self.text.update_idletasks()
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_queue)

class CommandThread(threading.Thread):
    def __init__(self, command, console):
        super().__init__()
        self.command = command
        self.console = console
        self.process = None
        self.daemon = True
        self.running = True

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            while self.running:
                line = self.process.stdout.readline()
                if not line:
                    break
                self.console.append_output(line.strip())
                
        except Exception as e:
            self.console.append_output(f"Error: {str(e)}")
        finally:
            if self.process:
                self.process.stdout.close()
                self.process.wait()

    def terminate(self):
        self.running = False
        if self.process:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/f", "/t", "/pid", str(self.process.pid)], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            else:
                self.process.terminate()

class KeyHunterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyHunter Puzzles TKinter GUI ")
        self.current_instances = 1
        self.console_frames = []
        self.command_threads = {}
        self.cpu_count = multiprocessing.cpu_count()
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="5")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create menu
        self.create_menu()

        # Create shared configuration
        self.create_shared_config()

        # Create console grid
        self.console_grid = ttk.Frame(self.main_container)
        self.console_grid.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create initial console
        self.update_grid_layout(1)

        # Add credits
        self.add_credits()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Instances menu
        instances_menu = tk.Menu(menubar, tearoff=0)
        for num in [1, 2, 4, 6, 8]:
            instances_menu.add_command(
                label=str(num),
                command=lambda n=num: self.update_grid_layout(n)
            )
        menubar.add_cascade(label="Instances", menu=instances_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help Telegram Group", command=self.open_telegram)
        help_menu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def create_shared_config(self):
        config_frame = ttk.LabelFrame(self.main_container, text="Shared Configuration", padding="5")
        config_frame.pack(fill=tk.X, pady=5)

        # Key Hunt Configuration
        hunt_frame = ttk.LabelFrame(config_frame, text="Key Hunt Configuration", padding="5")
        hunt_frame.pack(fill=tk.X, pady=5)

        # Row 1
        row1 = ttk.Frame(hunt_frame)
        row1.pack(fill=tk.X, pady=2)

        # CPU Count
        ttk.Label(row1, text="Number of CPUs:").pack(side=tk.LEFT, padx=5)
        self.thread_combo = ttk.Combobox(row1, width=5)
        self.thread_combo.pack(side=tk.LEFT, padx=5)
        self.update_cpu_options()

        # Crypto Type
        ttk.Label(row1, text="Crypto:").pack(side=tk.LEFT, padx=5)
        self.crypto_combo = ttk.Combobox(row1, values=["btc", "eth"], width=5)
        self.crypto_combo.set("btc")
        self.crypto_combo.pack(side=tk.LEFT, padx=5)
        self.crypto_combo.bind('<<ComboboxSelected>>', self.update_look_type_options)

        # Mode
        ttk.Label(row1, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_combo = ttk.Combobox(row1, values=["address", "bsgs", "rmd160"], width=10)
        self.mode_combo.set("address")
        self.mode_combo.pack(side=tk.LEFT, padx=5)
        self.mode_combo.bind('<<ComboboxSelected>>', self.update_movement_mode_options)

        # Movement Mode
        ttk.Label(row1, text="Movement Mode:").pack(side=tk.LEFT, padx=5)
        self.move_mode_combo = ttk.Combobox(row1, values=["random", "sequential"], width=10)
        self.move_mode_combo.set("random")
        self.move_mode_combo.pack(side=tk.LEFT, padx=5)

        # Stride
        ttk.Label(row1, text="Stride:").pack(side=tk.LEFT, padx=5)
        self.stride_entry = ttk.Entry(row1, width=10)
        self.stride_entry.insert(0, "1")
        self.stride_entry.pack(side=tk.LEFT, padx=5)

        # K factor
        ttk.Label(row1, text="K factor:").pack(side=tk.LEFT, padx=5)
        self.k_combo = ttk.Combobox(row1, values=['1', '4', '8', '16', '24', '32', '64', '128', '256', '512', '756', '1024', '2048'], width=5)
        self.k_combo.set("1")
        self.k_combo.pack(side=tk.LEFT, padx=5)

        # N Value
        ttk.Label(row1, text="N Value:").pack(side=tk.LEFT, padx=5)
        self.n_value_entry = ttk.Entry(row1, width=20)
        self.n_value_entry.insert(0, "0x1000000000000000")
        self.n_value_entry.pack(side=tk.LEFT, padx=5)

        # Key Space Configuration
        keyspace_frame = ttk.LabelFrame(config_frame, text="Key Space Configuration", padding="5")
        keyspace_frame.pack(fill=tk.X, pady=5)

        # Key Space
        ttk.Label(keyspace_frame, text="Key Space:").pack(side=tk.LEFT, padx=5)
        self.keyspace_entry = ttk.Entry(keyspace_frame, width=50)
        self.keyspace_entry.insert(0, "400000000000000000:7FFFFFFFFFFFFFFFFF")
        self.keyspace_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Bits slider and entry
        bits_frame = ttk.Frame(keyspace_frame)
        bits_frame.pack(fill=tk.X, pady=5)
        ttk.Label(bits_frame, text="Bits:").pack(side=tk.LEFT, padx=5)
        
        # Create bits_entry first
        self.bits_entry = ttk.Entry(bits_frame, width=5)
        self.bits_entry.insert(0, "71")
        self.bits_entry.pack(side=tk.RIGHT, padx=5)
        self.bits_entry.bind('<Return>', lambda e: self.updateSliderAndRanges())
        
        # Then create bits_slider
        self.bits_slider = ttk.Scale(bits_frame, from_=1, to=256, orient=tk.HORIZONTAL, command=self.update_keyspace_range)
        self.bits_slider.set(71)
        self.bits_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # File Configuration
        file_frame = ttk.LabelFrame(config_frame, text="File Configuration", padding="5")
        file_frame.pack(fill=tk.X, pady=5)

        # Look Type
        ttk.Label(file_frame, text="Look Type:").pack(side=tk.LEFT, padx=5)
        self.look_combo = ttk.Combobox(file_frame, values=["compress", "uncompress", "both"], width=10)
        self.look_combo.set("compress")
        self.look_combo.pack(side=tk.LEFT, padx=5)

        # Input File
        ttk.Label(file_frame, text="Input File:").pack(side=tk.LEFT, padx=5)
        self.input_file_entry = ttk.Entry(file_frame, width=20)
        self.input_file_entry.insert(0, "btc.txt")
        self.input_file_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Start All Instances", command=self.start_all_instances).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop All Instances", command=self.stop_all_instances).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔥 Check if Found 🔥", command=self.found_prog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Check Progress 💾", command=self.check_prog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Range Tools 💾", command=self.range_check).pack(side=tk.LEFT, padx=5)

        # Quiet mode checkbox
        self.quiet_var = tk.BooleanVar()
        ttk.Checkbutton(button_frame, text="Quiet mode", variable=self.quiet_var).pack(side=tk.LEFT, padx=5)

    def update_cpu_options(self):
        max_cpus = self.cpu_count // self.current_instances
        if max_cpus < 1:
            max_cpus = 1
        self.thread_combo['values'] = [str(i) for i in range(1, max_cpus + 1)]
        self.thread_combo.set("1")

    def update_grid_layout(self, num_instances):
        self.current_instances = num_instances
        self.console_frames.clear()
        
        # Clear existing consoles
        for widget in self.console_grid.winfo_children():
            widget.destroy()

        # Calculate grid dimensions
        if num_instances == 1:
            rows, cols = 1, 1
        elif num_instances == 2:
            rows, cols = 1, 2
        elif num_instances == 4:
            rows, cols = 2, 2
        elif num_instances == 6:
            rows, cols = 2, 3
        elif num_instances == 8:
            rows, cols = 2, 4

        # Create new consoles
        instance_number = 1
        for row in range(rows):
            for col in range(cols):
                console = ConsoleWindow(self.console_grid, f"Instance {instance_number}/{num_instances}")
                console.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
                self.console_frames.append(console)
                instance_number += 1

        # Update grid weights
        for i in range(rows):
            self.console_grid.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            self.console_grid.grid_columnconfigure(i, weight=1)

        # Update CPU options
        self.update_cpu_options()

    def update_look_type_options(self, event=None):
        crypto = self.crypto_combo.get()
        if crypto == "eth":
            self.look_combo.configure(state="disabled")
        else:
            self.look_combo.configure(state="normal")

    def update_movement_mode_options(self, event=None):
        mode = self.mode_combo.get()
        if mode == "bsgs":
            self.move_mode_combo['values'] = ["sequential", "backward", "both", "random", "dance"]
            self.bits_slider.configure(from_=50)
        else:
            self.move_mode_combo['values'] = ["random", "sequential"]
            self.bits_slider.configure(from_=1)
        self.move_mode_combo.set(self.move_mode_combo['values'][0])

    def update_keyspace_range(self, value):
        try:
            bits = int(float(value))
            start_range = 2 ** (bits - 1)
            end_range = 2 ** bits - 1
            self.keyspace_entry.delete(0, tk.END)
            self.keyspace_entry.insert(0, f"{start_range:X}:{end_range:X}")
            self.bits_entry.delete(0, tk.END)
            self.bits_entry.insert(0, str(bits))
        except ValueError:
            pass

    def updateSliderAndRanges(self):
        try:
            bits = int(self.bits_entry.get())
            mode = self.mode_combo.get()
            if mode == "bsgs":
                bits = max(50, min(bits, 256))
            else:
                bits = max(1, min(bits, 256))
            
            if bits == 256:
                start_range = "8000000000000000000000000000000000000000000000000000000000000000"
                end_range = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140"
            else:
                start_range = 2 ** (bits - 1)
                end_range = 2 ** bits - 1
                start_range = f"{start_range:X}"
                end_range = f"{end_range:X}"
            
            self.bits_slider.set(bits)
            self.keyspace_entry.delete(0, tk.END)
            self.keyspace_entry.insert(0, f"{start_range}:{end_range}")
        
        except ValueError:
            messagebox.showinfo("Range Error", "Range should be in Bit 1-256")

    def construct_command_key(self, start_range, end_range):
        """Construct keyhunt command with current configuration"""
        mode = self.mode_combo.get()
        thread_count = self.thread_combo.get()
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "keyhunt")

        if platform.system() == "Windows":
            command = [os.path.join(base_path, "keyhunt.exe"), "-m", mode, "-t", thread_count]
        else:
            command = [os.path.join(base_path, "keyhunt"), "-m", mode, "-t", thread_count]

        # Add range
        command.extend(["-r", f"{format(start_range, 'x')}:{format(end_range, 'x')}"])

        # Add other parameters
        file = self.input_file_entry.get().strip()
        if file:
            input_file_relative_path = ["input", file]
            input_file_path = os.path.join(*input_file_relative_path)
            command.extend(["-f", input_file_path])

        move_mode = self.move_mode_combo.get()
        if move_mode == 'random':
            if mode == 'bsgs':
                command.extend(["-B", move_mode])
            else:
                command.append("-R")
        elif move_mode == 'sequential':
            if mode == 'bsgs':
                command.extend(["-B", move_mode])
            else:
                command.append("-S")
        elif move_mode == 'backward' and mode == 'bsgs':
            command.extend(["-B", move_mode])
        elif move_mode == 'dance' and mode == 'bsgs':
            command.extend(["-B", move_mode])
        elif move_mode == 'both' and mode == 'bsgs':
            command.extend(["-B", move_mode])

        if not (mode == 'bsgs' and move_mode == 'both'):
            stride = self.stride_entry.get().strip()
            if stride:
                command.extend(["-I", stride])

        crypto = self.crypto_combo.get()
        if crypto == "eth":
            command.extend(["-c", crypto])
            
        look = self.look_combo.get()
        if look and crypto != "eth":  # Only add look type if not ETH
            command.extend(["-l", look])

        if mode == 'bsgs':
            n_value = self.n_value_entry.get().strip()
            if n_value:
                command.extend(["-n", n_value])
            kamount = self.k_combo.get()
            command.extend(["-k", kamount])

        if self.quiet_var.get():
            command.append("-q")

        return command

    def start_all_instances(self):
        try:
            # Get the range from shared input
            range_text = self.keyspace_entry.get().strip()
            if not range_text:
                messagebox.showwarning("Error", "Please enter a range")
                return

            start_range, end_range = range_text.split(':')
            # Convert hex strings to integers
            start_range = int(start_range, 16)
            end_range = int(end_range, 16)

            # Split range among instances
            ranges = self.split_range(start_range, end_range, len(self.console_frames))

            # Start each instance with its portion of the range
            for i, console in enumerate(self.console_frames):
                instance_start, instance_end = ranges[i]
                self.start_instance(console, instance_start, instance_end, i + 1)

        except ValueError as e:
            messagebox.showwarning("Error", f"Invalid range format: {str(e)}\nPlease use hex format (e.g., 400000000000000000:7FFFFFFFFFFFFFFFFF)")

    def start_instance(self, console, start_range, end_range, instance_number):
        """Start a single instance with the given range"""
        console.append_output(f"Instance {instance_number}/{len(self.console_frames)}")
        console.append_output(f"Range: {format(start_range, 'x')} to {format(end_range, 'x')}")
        
        command = self.construct_command_key(start_range, end_range)
        self.execute_command(console, command, instance_number)

    def execute_command(self, console, command, instance_number):
        """Execute command and show output in the given console window"""
        # Stop existing thread for this instance if it exists
        if instance_number in self.command_threads:
            self.command_threads[instance_number].terminate()
            self.command_threads[instance_number].join()

        # Convert command list to string for display
        command_str = ' '.join(str(x) for x in command)
        console.append_output(f"Executing command: {command_str}")

        # Create and start new thread for this instance
        thread = CommandThread(command, console)
        thread.start()
        
        # Store the thread
        self.command_threads[instance_number] = thread

    def stop_all_instances(self):
        """Stop all running instances"""
        try:
            for instance_number, thread in list(self.command_threads.items()):
                if thread and thread.is_alive():
                    thread.terminate()
                    thread.join()
                    
                    # Kill any remaining keyhunt processes
                    if platform.system() == "Windows":
                        try:
                            subprocess.run(["taskkill", "/f", "/im", "keyhunt.exe"], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=2)
                        except subprocess.TimeoutExpired:
                            pass
                        except Exception:
                            pass
                    else:
                        try:
                            subprocess.run(["pkill", "-f", "keyhunt"], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL,
                                         timeout=2)
                        except subprocess.TimeoutExpired:
                            pass
                        except Exception:
                            pass
                    
                if instance_number <= len(self.console_frames):
                    self.console_frames[instance_number - 1].append_output("Process stopped by user")
            
            # Clear the thread dictionary
            self.command_threads.clear()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def split_range(self, start, end, num_splits):
        """Split a range into equal parts"""
        total_range = end - start
        chunk_size = total_range // num_splits
        remainder = total_range % num_splits
        
        ranges = []
        current_start = start
        
        for i in range(num_splits):
            extra = 1 if i < remainder else 0
            current_end = current_start + chunk_size + extra - 1
            if i == num_splits - 1:
                current_end = end
            ranges.append((current_start, current_end))
            current_start = current_end + 1
        
        return ranges

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Binary Files", "*.bin"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            file_name = os.path.basename(file_path)
            self.input_file_entry.delete(0, tk.END)
            self.input_file_entry.insert(0, file_name)

    def found_prog(self):
        file_path = 'KEYFOUNDKEYFOUND.txt'
        self.read_and_display_file(file_path, "😀😀 Keyhunt File found. Check for Winners 😀😀.", "😞😞No Winners Yet 😞😞")

    def read_and_display_file(self, file_path, success_message, error_message):
        for console in self.console_frames:
            console.append_output(f"Attempting to read file: {file_path}")
        try:
            if not os.path.exists(file_path):
                for console in self.console_frames:
                    console.append_output(f"⚠️ {error_message} File not found. Please check the file path.")
                return None
                
            with open(file_path, 'r') as file:
                output_from_text = file.read()
                for console in self.console_frames:
                    console.append_output(success_message)
                    console.append_output(output_from_text)
                return output_from_text
        except FileNotFoundError:
            for console in self.console_frames:
                console.append_output(f"⚠️ {error_message} File not found. Please check the file path.")
            return None
        except Exception as e:
            for console in self.console_frames:
                console.append_output(f"An error occurred: {str(e)}")
            return None

    def check_prog(self):
        directory = '.'
        dat_files = glob.glob(os.path.join(directory, '*.dat'))
        
        if dat_files:
            file_path = dat_files[0]
            if messagebox.askyesno("Progress File", "Do you want to delete the progress file?"):
                os.remove(file_path)
                for console in self.console_frames:
                    console.append_output("Progress deleted successfully.")
            else:
                for console in self.console_frames:
                    console.append_output("Progress kept.")
        else:
            for console in self.console_frames:
                console.append_output("Progress not found.")

    def range_check(self):
        # Create a new top-level window
        range_window = tk.Toplevel(self.root)
        range_window.title("Range Tools")
        range_window.geometry("600x400")
        
        # Create main frame
        main_frame = ttk.Frame(range_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Range Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Range Input", padding="5")
        input_frame.pack(fill=tk.X, pady=5)
        
        # Start Range
        start_frame = ttk.Frame(input_frame)
        start_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_frame, text="Start Range:").pack(side=tk.LEFT, padx=5)
        start_entry = ttk.Entry(start_frame, width=50)
        start_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # End Range
        end_frame = ttk.Frame(input_frame)
        end_frame.pack(fill=tk.X, pady=2)
        ttk.Label(end_frame, text="End Range:").pack(side=tk.LEFT, padx=5)
        end_entry = ttk.Entry(end_frame, width=50)
        end_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        def check_range():
            try:
                start = int(start_entry.get(), 16)
                end = int(end_entry.get(), 16)
                if start >= end:
                    messagebox.showerror("Error", "Start range must be less than end range")
                    return
                
                # Calculate range size
                range_size = end - start + 1  # Add 1 to include both start and end
                bits = (range_size).bit_length()
                
                # Update result text
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Range Size: {range_size:,} keys\n")
                result_text.insert(tk.END, f"Bits: {bits}\n")
                result_text.insert(tk.END, f"Start: {hex(start)}\n")
                result_text.insert(tk.END, f"End: {hex(end)}\n")
                
                # Calculate estimated time (assuming 1 million keys per second)
                keys_per_second = 1_000_000
                estimated_seconds = range_size / keys_per_second
                days = int(estimated_seconds // (24 * 3600))
                hours = int((estimated_seconds % (24 * 3600)) // 3600)
                minutes = int((estimated_seconds % 3600) // 60)
                
                result_text.insert(tk.END, f"\nEstimated Time (at 1M keys/sec):\n")
                result_text.insert(tk.END, f"{days:,} days, {hours} hours, {minutes} minutes\n")
                
            except ValueError as e:
                messagebox.showerror("Error", "Invalid range format. Please use hexadecimal values.")
        
        def split_range():
            try:
                start = int(start_entry.get(), 16)
                end = int(end_entry.get(), 16)
                if start >= end:
                    messagebox.showerror("Error", "Start range must be less than end range")
                    return
                
                # Get number of splits
                num_splits = simpledialog.askinteger("Split Range", "Enter number of splits:", 
                                                   minvalue=2, maxvalue=100)
                if not num_splits:
                    return
                
                # Calculate splits
                total_range = end - start
                chunk_size = total_range // num_splits
                remainder = total_range % num_splits
                
                # Update result text
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Range split into {num_splits} parts:\n\n")
                
                current_start = start
                for i in range(num_splits):
                    extra = 1 if i < remainder else 0
                    current_end = current_start + chunk_size + extra - 1
                    if i == num_splits - 1:
                        current_end = end
                    
                    result_text.insert(tk.END, f"Part {i+1}:\n")
                    result_text.insert(tk.END, f"Start: {hex(current_start)}\n")
                    result_text.insert(tk.END, f"End: {hex(current_end)}\n")
                    result_text.insert(tk.END, f"Size: {current_end - current_start + 1:,} keys\n\n")
                    
                    current_start = current_end + 1
                
            except ValueError as e:
                messagebox.showerror("Error", "Invalid range format. Please use hexadecimal values.")
        
        def load_current_range():
            try:
                current_range = self.keyspace_entry.get().strip()
                if current_range:
                    start, end = current_range.split(':')
                    start_entry.delete(0, tk.END)
                    start_entry.insert(0, start)
                    end_entry.delete(0, tk.END)
                    end_entry.insert(0, end)
            except Exception as e:
                messagebox.showerror("Error", "Failed to load current range")
        
        # Add buttons
        ttk.Button(button_frame, text="Check Range", command=check_range).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Split Range", command=split_range).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Current Range", command=load_current_range).pack(side=tk.LEFT, padx=5)
        
        # Result Text
        result_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        result_text = tk.Text(result_frame, wrap=tk.WORD, height=10, bg='black', fg='white')
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_text.yview)
        result_text.configure(yscrollcommand=scrollbar.set)
        
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load current range if available
        load_current_range()

    def open_settings(self):
        # Create a new top-level window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x500")
        
        # Create main frame
        main_frame = ttk.Frame(settings_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Theme Section
        theme_frame = ttk.LabelFrame(main_frame, text="Theme Settings", padding="5")
        theme_frame.pack(fill=tk.X, pady=5)
        
        # Theme Selection
        theme_select_frame = ttk.Frame(theme_frame)
        theme_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_select_frame, text="Select Theme:").pack(side=tk.LEFT, padx=5)
        self.theme_combo = ttk.Combobox(theme_select_frame, width=20)
        self.theme_combo['values'] = [
            "Default Dark",
            "Default Light",
            "Blue Dark",
            "Blue Light",
            "Green Dark",
            "Green Light",
            "Purple Dark",
            "Purple Light",
            "Solarized Dark",
            "Solarized Light",
            "Monokai",
            "Nord",
            "Custom"
        ]
        self.theme_combo.set("Default Dark")
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        self.theme_combo.bind('<<ComboboxSelected>>', self.preview_theme)
        
        # Custom Theme Colors
        custom_frame = ttk.LabelFrame(theme_frame, text="Custom Theme Colors", padding="5")
        custom_frame.pack(fill=tk.X, pady=5)
        
        # Background Color
        bg_frame = ttk.Frame(custom_frame)
        bg_frame.pack(fill=tk.X, pady=2)
        ttk.Label(bg_frame, text="Background:").pack(side=tk.LEFT, padx=5)
        self.bg_color = ttk.Entry(bg_frame, width=10)
        self.bg_color.insert(0, "#000000")
        self.bg_color.pack(side=tk.LEFT, padx=5)
        ttk.Button(bg_frame, text="Pick", command=lambda: self.pick_color("bg")).pack(side=tk.LEFT, padx=5)
        
        # Text Color
        text_frame = ttk.Frame(custom_frame)
        text_frame.pack(fill=tk.X, pady=2)
        ttk.Label(text_frame, text="Text:").pack(side=tk.LEFT, padx=5)
        self.text_color = ttk.Entry(text_frame, width=10)
        self.text_color.insert(0, "#FFFFFF")
        self.text_color.pack(side=tk.LEFT, padx=5)
        ttk.Button(text_frame, text="Pick", command=lambda: self.pick_color("text")).pack(side=tk.LEFT, padx=5)
        
        # Button Color
        button_frame = ttk.Frame(custom_frame)
        button_frame.pack(fill=tk.X, pady=2)
        ttk.Label(button_frame, text="Button:").pack(side=tk.LEFT, padx=5)
        self.button_color = ttk.Entry(button_frame, width=10)
        self.button_color.insert(0, "#404040")
        self.button_color.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Pick", command=lambda: self.pick_color("button")).pack(side=tk.LEFT, padx=5)
        
        # Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text="Theme Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=5, bg='black', fg='white')
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_text.insert(tk.END, "This is a preview of how the theme will look.\n")
        self.preview_text.insert(tk.END, "The console output will use these colors.")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Apply Theme", command=self.apply_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Theme", command=self.save_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Default", command=self.reset_theme).pack(side=tk.LEFT, padx=5)
        
        # Load current theme
        self.load_current_theme()

    def pick_color(self, color_type):
        color = colorchooser.askcolor(title="Choose Color")[1]
        if color:
            if color_type == "bg":
                self.bg_color.delete(0, tk.END)
                self.bg_color.insert(0, color)
            elif color_type == "text":
                self.text_color.delete(0, tk.END)
                self.text_color.insert(0, color)
            elif color_type == "button":
                self.button_color.delete(0, tk.END)
                self.button_color.insert(0, color)
            self.preview_theme()

    def preview_theme(self, event=None):
        theme = self.theme_combo.get()
        if theme == "Custom":
            bg = self.bg_color.get()
            text = self.text_color.get()
            button = self.button_color.get()
        else:
            colors = self.get_theme_colors(theme)
            bg = colors['bg']
            text = colors['text']
            button = colors['button']
        
        self.preview_text.configure(bg=bg, fg=text)
        self.style.configure('TButton', background=button)
        self.style.configure('TLabel', background=bg, foreground=text)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabelframe', background=bg)
        self.style.configure('TLabelframe.Label', background=bg, foreground=text)

    def get_theme_colors(self, theme):
        themes = {
            "Default Dark": {
                'bg': '#1E1E1E',  # Dark gray
                'text': '#E0E0E0',  # Light gray
                'button': '#2D2D2D'  # Slightly lighter gray
            },
            "Default Light": {
                'bg': '#F5F5F5',  # Light gray
                'text': '#2D2D2D',  # Dark gray
                'button': '#E0E0E0'  # Medium gray
            },
            "Blue Dark": {
                'bg': '#0D1117',  # GitHub dark blue
                'text': '#58A6FF',  # Bright blue
                'button': '#1F6FEB'  # Medium blue
            },
            "Blue Light": {
                'bg': '#F0F8FF',  # Alice blue
                'text': '#0066CC',  # Deep blue
                'button': '#B0E0E6'  # Powder blue
            },
            "Green Dark": {
                'bg': '#0A1929',  # Dark navy
                'text': '#00FF9D',  # Bright mint
                'button': '#00CC7E'  # Medium mint
            },
            "Green Light": {
                'bg': '#F0FFF0',  # Honeydew
                'text': '#228B22',  # Forest green
                'button': '#98FB98'  # Pale green
            },
            "Purple Dark": {
                'bg': '#1A1B26',  # Dark navy
                'text': '#BB9AF7',  # Light purple
                'button': '#7AA2F7'  # Medium purple
            },
            "Purple Light": {
                'bg': '#F8F0FF',  # Light lavender
                'text': '#663399',  # Rebecca purple
                'button': '#E6E6FA'  # Lavender
            },
            "Solarized Dark": {
                'bg': '#002B36',  # Dark teal
                'text': '#93A1A1',  # Light gray
                'button': '#073642'  # Darker teal
            },
            "Solarized Light": {
                'bg': '#FDF6E3',  # Light cream
                'text': '#657B83',  # Dark gray
                'button': '#EEE8D5'  # Light cream
            },
            "Monokai": {
                'bg': '#272822',  # Dark gray
                'text': '#F8F8F2',  # Off-white
                'button': '#3E3D32'  # Medium gray
            },
            "Nord": {
                'bg': '#2E3440',  # Dark blue-gray
                'text': '#ECEFF4',  # Light gray
                'button': '#3B4252'  # Medium blue-gray
            }
        }
        return themes.get(theme, themes["Default Dark"])

    def apply_theme(self):
        theme = self.theme_combo.get()
        if theme == "Custom":
            colors = {
                'bg': self.bg_color.get(),
                'text': self.text_color.get(),
                'button': self.button_color.get()
            }
        else:
            colors = self.get_theme_colors(theme)
        
        # Apply theme to all console windows
        for console in self.console_frames:
            console.text.configure(bg=colors['bg'], fg=colors['text'])
        
        # Save theme to config
        self.save_theme_to_config(colors)
        
        messagebox.showinfo("Theme Applied", "Theme has been applied successfully!")

    def save_theme(self):
        theme = self.theme_combo.get()
        if theme == "Custom":
            colors = {
                'bg': self.bg_color.get(),
                'text': self.text_color.get(),
                'button': self.button_color.get()
            }
            # Save custom theme
            self.save_theme_to_config(colors)
            messagebox.showinfo("Theme Saved", "Custom theme has been saved!")
        else:
            messagebox.showinfo("Theme Saved", f"{theme} theme is already saved!")

    def save_theme_to_config(self, colors):
        config = configparser.ConfigParser()
        if os.path.exists('config.ini'):
            config.read('config.ini')
        
        if not config.has_section('Theme'):
            config.add_section('Theme')
        
        config['Theme']['background'] = colors['bg']
        config['Theme']['text'] = colors['text']
        config['Theme']['button'] = colors['button']
        
        with open('config.ini', 'w') as f:
            config.write(f)

    def load_current_theme(self):
        config = configparser.ConfigParser()
        if os.path.exists('config.ini'):
            config.read('config.ini')
            if config.has_section('Theme'):
                self.bg_color.delete(0, tk.END)
                self.bg_color.insert(0, config.get('Theme', 'background', fallback='#000000'))
                self.text_color.delete(0, tk.END)
                self.text_color.insert(0, config.get('Theme', 'text', fallback='#FFFFFF'))
                self.button_color.delete(0, tk.END)
                self.button_color.insert(0, config.get('Theme', 'button', fallback='#404040'))
                self.theme_combo.set("Custom")
                self.preview_theme()

    def reset_theme(self):
        self.theme_combo.set("Default Dark")
        self.preview_theme()
        self.apply_theme()

    def open_telegram(self):
        webbrowser.open("https://t.me/TeamHunter_GUI")

    def about(self):
        about_text = """
KeyHunter Puzzles GUI - Advanced Bitcoin Key Hunting Tool made with Tkinter the Tk GUI toolkit for Python

Major Features:
1. Multi-Instance Support
2. Theme Customization
3. Advanced Range Management
4. Enhanced Scanning Capabilities
5. User-Friendly Interface

Made by Team Mizogg
© mizogg.com 2018 - 2025
        """
        messagebox.showinfo("About", about_text)

    def add_credits(self):
        credits_frame = ttk.Frame(self.main_container)
        credits_frame.pack(fill=tk.X, pady=5)
        
        credits_text = "Tkinter GUI • Made by Team Mizogg • Full Version 1.2 • © mizogg.com 2018 - 2025"
        ttk.Label(credits_frame, text=credits_text).pack()

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists('config.ini'):
            config.read('config.ini')
            # TODO: Load theme settings

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyHunterGUI(root)
    root.mainloop() 
