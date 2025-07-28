import qrcode
import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from pyzbar import pyzbar
import threading
import time

class QRCodeGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("QR Code Generator & Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.url_var = tk.StringVar()
        self.qr_image = None
        self.scanning = False
        self.cap = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="QR Code Generator & Scanner", 
                            font=("Arial", 16, "bold"), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # URL Input Frame
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(input_frame, text="Masukkan URL:", 
                font=("Arial", 12), bg='#f0f0f0').pack(anchor='w')
        
        url_entry = tk.Entry(input_frame, textvariable=self.url_var, 
                            font=("Arial", 11), width=60)
        url_entry.pack(pady=5, fill='x')
        
        # Buttons Frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        generate_btn = tk.Button(button_frame, text="Generate QR Code", 
                               command=self.generate_qr, bg='#4CAF50', 
                               fg='white', font=("Arial", 12), padx=20)
        generate_btn.pack(side='left', padx=5)
        
        save_btn = tk.Button(button_frame, text="Save QR Code", 
                           command=self.save_qr, bg='#2196F3', 
                           fg='white', font=("Arial", 12), padx=20)
        save_btn.pack(side='left', padx=5)
        
        scan_btn = tk.Button(button_frame, text="Scan QR Code", 
                           command=self.toggle_scanning, bg='#FF9800', 
                           fg='white', font=("Arial", 12), padx=20)
        scan_btn.pack(side='left', padx=5)
        
        # QR Code Display Frame
        self.qr_frame = tk.Frame(self.root, bg='white', relief='solid', borderwidth=2)
        self.qr_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        self.qr_label = tk.Label(self.qr_frame, text="QR Code akan ditampilkan di sini", 
                                bg='white', font=("Arial", 12))
        self.qr_label.pack(expand=True)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Siap", 
                                   font=("Arial", 10), bg='#f0f0f0', fg='green')
        self.status_label.pack(pady=5)
        
    def generate_qr(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Masukkan URL terlebih dahulu!")
            return
            
        # Tambahkan http:// jika tidak ada protokol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create QR image
            self.qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Resize for display
            display_size = (300, 300)
            display_image = self.qr_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            self.photo = ImageTk.PhotoImage(display_image)
            self.qr_label.configure(image=self.photo, text="")
            
            self.status_label.configure(text=f"QR Code berhasil dibuat untuk: {url}", fg='green')
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat QR Code: {str(e)}")
            self.status_label.configure(text="Error saat membuat QR Code", fg='red')
    
    def save_qr(self):
        if self.qr_image is None:
            messagebox.showerror("Error", "Generate QR Code terlebih dahulu!")
            return
            
        try:
            filename = f"qrcode_{int(time.time())}.png"
            self.qr_image.save(filename)
            messagebox.showinfo("Success", f"QR Code disimpan sebagai {filename}")
            self.status_label.configure(text=f"QR Code disimpan: {filename}", fg='green')
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan QR Code: {str(e)}")
    
    def toggle_scanning(self):
        if not self.scanning:
            self.start_scanning()
        else:
            self.stop_scanning()
    
    def start_scanning(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Tidak dapat mengakses kamera!")
                return
                
            self.scanning = True
            self.status_label.configure(text="Scanning QR Code... (ESC untuk berhenti)", fg='blue')
            
            # Start scanning in separate thread
            scan_thread = threading.Thread(target=self.scan_qr_codes, daemon=True)
            scan_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai scanning: {str(e)}")
    
    def stop_scanning(self):
        self.scanning = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.status_label.configure(text="Scanning dihentikan", fg='orange')
    
    def scan_qr_codes(self):
        while self.scanning:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Decode QR codes
            qr_codes = pyzbar.decode(frame)
            
            for qr_code in qr_codes:
                # Extract QR code data
                qr_data = qr_code.data.decode('utf-8')
                
                # Draw rectangle around QR code
                points = qr_code.polygon
                if len(points) == 4:
                    pts = np.array([[point.x, point.y] for point in points], np.int32)
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                
                # Display QR code data
                cv2.putText(frame, f"QR: {qr_data[:50]}...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Show confirmation dialog
                self.root.after(0, lambda data=qr_data: self.handle_scanned_qr(data))
            
            # Display frame
            cv2.imshow('QR Code Scanner (ESC untuk keluar)', frame)
            
            # Break on ESC key
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                break
        
        self.stop_scanning()
    
    def handle_scanned_qr(self, qr_data):
        if not self.scanning:
            return
            
        self.stop_scanning()
        
        # Ask user if they want to open the URL
        result = messagebox.askyesno("QR Code Detected", 
                                   f"QR Code terdeteksi:\n{qr_data}\n\nBuka link ini?")
        
        if result:
            try:
                webbrowser.open(qr_data)
                self.status_label.configure(text=f"Membuka: {qr_data}", fg='green')
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka URL: {str(e)}")
        else:
            self.status_label.configure(text="Scan selesai", fg='green')
    
    def run(self):
        # Handle window close
        def on_closing():
            self.stop_scanning()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

def main():
    try:
        app = QRCodeGenerator()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Pastikan semua library yang dibutuhkan sudah terinstall:")
        print("pip install qrcode[pil] opencv-python pyzbar pillow")

if __name__ == "__main__":
    main()