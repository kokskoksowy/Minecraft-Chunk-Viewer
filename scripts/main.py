import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import anvil
import time

class RegionCountGUI:
    def __init__(self, master, region_count):
        self.master = master
        master.title("Region Count Information")

        self.region_count = region_count

        self.region_count_label = tk.Label(master, text=f"Ilość regionów w folderze: {self.region_count}")
        self.region_count_label.pack(pady=10)

        self.close_button = tk.Button(master, text="Zamknij", command=master.destroy)
        self.close_button.pack(pady=10)


class RegionFolderSelectorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Minecraft Region Chunk Checker")

        self.region_folder_path = tk.StringVar()
        self.region_count = 0  # Store the region count after folder selection

        # 1. Static Text Label
        self.instruction_label = tk.Label(master, text="Wybierz folder zawierający pliki regionów (.mca)")
        self.instruction_label.pack(pady=10)

        # 2. Choose Folder Button
        self.choose_button = tk.Button(master, text="Wybierz folder regionów", command=self.browse_folder)
        self.choose_button.pack(pady=10)

        # 3. Region Count Label (initially empty)
        self.region_count_label = tk.Label(master, text="Ilość regionów: 0")
        self.region_count_label.pack(pady=10)

        # 4. Recalculate Chunks Button
        self.recalculate_button = tk.Button(master, text="Przekalkuluj chunków", command=self.recalculate_chunks)
        self.recalculate_button.pack(pady=10)
        self.recalculate_button.config(state=tk.DISABLED)  # Disabled until folder is selected

        # Progress Bar variables
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()  # Initially hide the progress bar

        self.chunk_count_label = tk.Label(master, text="Ilość wykrytych chunków: 0")
        self.chunk_count_label.pack(pady=10)
        self.chunk_count_label.pack_forget()  # Initially hide chunk count label

        self.current_region_label = tk.Label(master, text="Kalkulacja regionu: Brak")
        self.current_region_label.pack(pady=10)
        self.current_region_label.pack_forget()

        self.elapsed_time_label = tk.Label(master, text="Czas kalkulacji: 0s")
        self.elapsed_time_label.pack(pady=10)
        self.elapsed_time_label.pack_forget()

    def browse_folder(self):
        """Opens a file dialog to select a folder."""
        folder_selected = filedialog.askdirectory(initialdir="C:\\",
                                                  title="Wybierz folder z regionami")

        if folder_selected:
            self.region_folder_path.set(folder_selected)
            self.region_count = self.count_regions(folder_selected)  # Store region count
            self.region_count_label.config(text=f"Ilość regionów: {self.region_count}")
            self.recalculate_button.config(state=tk.NORMAL)  # Enable the button

    def count_regions(self, folder_path):
        """Counts the number of .mca files in a given folder."""
        count = 0
        try:
            for filename in os.listdir(folder_path):
                if filename.endswith(".mca"):
                    count += 1
            return count
        except FileNotFoundError:
            messagebox.showerror("Error", f"Folder not found at {folder_path}")
            return 0  # Changed return to 0 for a default value
        except Exception as e:
            messagebox.showerror("Error", f"Error processing folder: {e}")
            return 0  # Changed return to 0 for a default value

    def recalculate_chunks(self):
        """Recalculates the total number of chunks in the selected region folder."""
        folder_path = self.region_folder_path.get()

        if not folder_path:
            messagebox.showerror("Error", "Proszę wybrać folder regionów.")
            return

        # Prepare UI elements
        self.recalculate_button.config(state=tk.DISABLED)  # Disable the button during processing
        self.progress_bar.pack(pady=10)  # Show the progress bar
        self.chunk_count_label.pack(pady=10)  # Show the chunk count label
        self.current_region_label.pack(pady=10)
        self.elapsed_time_label.pack(pady=10)
        self.chunk_count_label.config(text="Ilość wykrytych chunków: 0")
        self.current_region_label.config(text="Kalkulacja regionu: Brak")
        self.elapsed_time_label.config(text="Czas kalkulacji: 0s")

        total_chunks = 0
        region_files = [f for f in os.listdir(folder_path) if f.endswith(".mca")]  # Only process .mca files
        num_region_files = len(region_files)

        # Set up the progress bar
        self.progress_bar["maximum"] = num_region_files
        self.progress_bar["value"] = 0

        start_time = time.time()  # Start time for total elapsed time

        # Process each region file
        for i, region_file in enumerate(region_files):
            region_file_path = os.path.join(folder_path, region_file)

            # Update the current region label
            self.current_region_label.config(text=f"Kalkulacja regionu: {region_file}")
            self.master.update()

            region_start_time = time.time()  # Start time for individual region

            chunk_count = self.count_chunks_in_region(region_file_path)
            if chunk_count is not None:
                total_chunks += chunk_count

            # Update the UI (progress bar and chunk count)
            self.chunk_count_label.config(text=f"Ilość wykrytych chunków: {total_chunks}")
            self.progress_bar["value"] = i + 1

            elapsed_time = time.time() - start_time  # Calculate total elapsed time
            self.elapsed_time_label.config(text=f"Czas kalkulacji: {elapsed_time:.1f}s")

            self.master.update()  # Force UI update to see progress

        # Clean up UI elements after processing
        self.recalculate_button.config(state=tk.NORMAL)  # Re-enable the button
        messagebox.showinfo("Zakończono", f"Przeliczanie chunków zakończone. Znaleziono łącznie: {total_chunks} chunków.")

    def count_chunks_in_region(self, region_file_path):
        """Counts the number of existing chunks in a single region file."""
        try:
            region = anvil.Region.from_file(region_file_path)
            chunk_count = 0
            for x in range(32):
                for z in range(32):
                    try:
                        anvil.Chunk.from_region(region, x, z)  # Try to load the chunk
                        chunk_count += 1
                    except Exception as e:
                        pass  # Chunk doesn't exist, move to the next
            return chunk_count
        except FileNotFoundError:
            messagebox.showerror("Error", f"Region file not found at {region_file_path}")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Error processing region file: {e}")
            return None



# --- Example Usage ---
if __name__ == '__main__':
    root = tk.Tk()
    gui = RegionFolderSelectorGUI(root)
    root.mainloop()