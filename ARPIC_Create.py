import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import base64
import json
from cryptography.fernet import Fernet
import os

# ฟังก์ชันสำหรับแปลงภาพเป็น Base64
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# ฟังก์ชันสำหรับเข้ารหัสภาพด้วยรหัสผ่าน
def encrypt_image(image_path, password):
    key = base64.urlsafe_b64encode(password.ljust(32)[:32].encode())  # สร้างคีย์จากรหัสผ่าน
    cipher = Fernet(key)

    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
        encrypted_data = cipher.encrypt(img_data)
        return base64.b64encode(encrypted_data).decode('utf-8')

# ฟังก์ชันสำหรับแปลง Base64 เป็น Base64 อีกครั้ง
def double_encode_base64(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

# ฟังก์ชันสำหรับสร้างไฟล์ .arpic
def create_file():
    file_name = file_name_entry.get()
    creator = creator_entry.get()
    created_date = created_date_entry.get()
    location = location_entry.get()
    taken_date = taken_date_entry.get()
    password = password_entry.get()
    
    image_path = filedialog.askopenfilename(title="เลือกภาพ", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not image_path:
        return

    if password:
        # เข้ารหัสภาพถ้ามีรหัสผ่าน
        base64_pic = encrypt_image(image_path, password)
    else:
        # แปลงภาพเป็น Base64 ถ้าไม่มีรหัสผ่าน
        base64_pic = image_to_base64(image_path)

    # แปลง Base64 ที่ได้เป็น Base64 อีกครั้ง
    double_encoded_pic = double_encode_base64(base64_pic)

    # สร้างข้อมูลที่จะบันทึก
    data = {
        "file_name": file_name,
        "creator": creator,
        "created_date": created_date,
        "location": location,
        "taken_date": taken_date,
        "password": password if password else None,  # ใส่รหัสผ่านถ้ามี
        "base64_pic": double_encoded_pic
    }

    # ให้ผู้ใช้เลือกตำแหน่งในการบันทึกไฟล์
    save_path = filedialog.asksaveasfilename(defaultextension=".arpic", filetypes=[("ARPIC Files", "*.arpic")])
    if save_path:
        with open(save_path, "w", encoding="utf-8") as arpic_file:
            json.dump(data, arpic_file, ensure_ascii=False, indent=4)
        messagebox.showinfo("สำเร็จ", "สร้างไฟล์ ARPIC สำเร็จ")

# สร้างหน้าต่าง GUI
root = tk.Tk()
root.title("สร้างไฟล์ ARPIC")
root.geometry("400x300")

# ส่วนสำหรับกรอกข้อมูล
tk.Label(root, text="ชื่อไฟล์:").pack(pady=5)
file_name_entry = tk.Entry(root)
file_name_entry.pack(pady=5)

tk.Label(root, text="ผู้สร้าง:").pack(pady=5)
creator_entry = tk.Entry(root)
creator_entry.pack(pady=5)

tk.Label(root, text="วันที่สร้าง (YYYY-MM-DD):").pack(pady=5)
created_date_entry = tk.Entry(root)
created_date_entry.pack(pady=5)

tk.Label(root, text="สถานที่ถ่ายภาพ:").pack(pady=5)
location_entry = tk.Entry(root)
location_entry.pack(pady=5)

tk.Label(root, text="วันที่ถ่ายภาพ (YYYY-MM-DD):").pack(pady=5)
taken_date_entry = tk.Entry(root)
taken_date_entry.pack(pady=5)

tk.Label(root, text="รหัสผ่าน (ถ้ามี):").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

# ปุ่มสำหรับสร้างไฟล์
tk.Button(root, text="สร้างไฟล์ .arpic", command=create_file).pack(pady=20)

root.mainloop()
