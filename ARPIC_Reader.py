import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import base64
from PIL import Image, ImageTk
import io
from tkinterdnd2 import DND_FILES, TkinterDnD
from cryptography.fernet import Fernet

# ฟังก์ชันสำหรับการเข้ารหัสภาพเป็น Base64 สองรอบ
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            first_encode = base64.b64encode(image_file.read())
            second_encode = base64.b64encode(first_encode)
            return second_encode.decode('utf-8')  # แปลงเป็นสตริง
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเข้ารหัสภาพได้: {str(e)}")

# ฟังก์ชันสำหรับถอดรหัสภาพจาก Base64
def decrypt_image(encrypted_base64, password):
    key = base64.urlsafe_b64encode(password.ljust(32)[:32].encode())  # สร้างคีย์จากรหัสผ่าน
    cipher = Fernet(key)

    encrypted_data = base64.b64decode(encrypted_base64)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data

# ฟังก์ชันสำหรับอ่านไฟล์ .arpic
def read_file(file_path):
    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as arpic_file:
            data = json.load(arpic_file)

        # ตรวจสอบว่ามีรหัสผ่านหรือไม่
        password = data.get("password", None)  
        if password:
            user_input = simpledialog.askstring("กรุณากรอกรหัสผ่าน", "กรุณากรอกรหัสผ่าน:", show='*')
            if user_input != password:
                messagebox.showerror("ข้อผิดพลาด", "รหัสผ่านไม่ถูกต้อง!")
                return  # ถ้ารหัสผ่านผิดให้หยุดที่นี่

        # ถ้ารหัสผ่านถูกต้อง หรือไม่มีรหัสผ่าน ให้แสดงข้อมูลต่อไป
        display_data(data)

    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถอ่านไฟล์ได้: {str(e)}")

# ฟังก์ชันสำหรับแสดงข้อมูลและภาพ
def display_data(data):
    # สร้างหน้าต่างใหม่สำหรับแสดงข้อมูล
    display_window = tk.Toplevel(root)
    display_window.title("แสดงข้อมูล ARPIC")

    tk.Label(display_window, text="ชื่อไฟล์: " + data.get("file_name", "N/A")).pack(pady=5)
    tk.Label(display_window, text="ผู้สร้าง: " + data.get("creator", "N/A")).pack(pady=5)
    tk.Label(display_window, text="วันที่สร้าง: " + data.get("created_date", "N/A")).pack(pady=5)
    tk.Label(display_window, text="สถานที่ถ่ายภาพ: " + data.get("location", "N/A")).pack(pady=5)
    tk.Label(display_window, text="วันที่ถ่ายภาพ: " + data.get("taken_date", "N/A")).pack(pady=5)

    # แสดงภาพพร้อม alt text
    if "base64_pic" in data:
        base64_pic = data["base64_pic"]
        try:
            # ถอดรหัสภาพ
            if data.get("password"):
                image_data = decrypt_image(base64.b64decode(base64_pic), data["password"])
            else:
                image_data = base64.b64decode(base64_pic)

            image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)

            # สร้างเฟรมสำหรับแสดงภาพและข้อความ alt text
            frame = tk.Frame(display_window)
            frame.pack(pady=5)

            # แสดงภาพ
            label = tk.Label(frame, image=photo)
            label.image = photo
            label.pack()

            # แสดงข้อความ alt text
            alt_text_label = tk.Label(frame, text="คลิกสองครั้งเพื่อเปิดเต็มหน้าจอ", fg="grey")
            alt_text_label.pack()

            # เพิ่มฟังก์ชันให้แสดงภาพเต็มหน้าจอเมื่อคลิกสองครั้ง
            label.bind("<Double-Button-1>", lambda e: display_fullscreen(image))

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถแสดงภาพได้: {str(e)}")

# ฟังก์ชันสำหรับแสดงภาพเต็มหน้าจอ
def display_fullscreen(image):
    full_screen_window = tk.Toplevel(root)
    full_screen_window.title("แสดงภาพเต็มหน้าจอ")
    
    # ดึงขนาดจอ
    screen_width = full_screen_window.winfo_screenwidth()
    screen_height = full_screen_window.winfo_screenheight()

    # ปรับขนาดภาพให้ฟิตเต็มหน้าจอ
    image.thumbnail((screen_width, screen_height), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    label = tk.Label(full_screen_window, image=photo)
    label.image = photo
    label.pack(fill="both", expand=True)

    # ทำให้หน้าต่างเต็มจอ
    full_screen_window.attributes('-fullscreen', True)

    # ออกจากโหมดเต็มจอเมื่อคลิกที่หน้าต่าง
    full_screen_window.bind("<Button-1>", lambda e: full_screen_window.destroy())

# ฟังก์ชันจัดการการวางไฟล์
def drop(event):
    file_path = event.data
    read_file(file_path)

# สร้างหน้าต่างหลัก
try:
    root = TkinterDnD.Tk()  # ใช้ TkinterDnD แทน Tk
    root.title("ตัวอ่านไฟล์ ARPIC")
    root.geometry("300x200")

    # ปรับให้สามารถลากไฟล์เข้ามาในโปรแกรม
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', drop)

    label = tk.Label(root, text="ลากไฟล์ ARPIC มาที่นี่")
    label.pack(pady=20)

    root.mainloop()
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {str(e)}")  # พิมพ์ข้อผิดพลาด
