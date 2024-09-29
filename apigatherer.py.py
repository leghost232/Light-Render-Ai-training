import tkinter as tk
import time
import os
link_list=[]
last_list =[".com",".online","edu"]
def save_link():
    global link
    link = entry.get()
    print(f"Link kaydedildi: {link}")
def check_url(url,api):
    global link
    global link_list
    for i in str(link):
        link_list.append(i)
    if link_list[-4] in last_list:
        pass
    else:
        print("Yanlış site uzantısı!")




root = tk.Tk()
root.title("Link Kaydet")
root.geometry("500x500")  # Pencere boyutunu ayarla
root.resizable(False, False)  # Boyut değişikliğini engelle


entry = tk.Entry(root, width=40)
entry.pack(pady=10)

button = tk.Button(root, text="Linki Kaydet", command=save_link,check_url(l,))
button.pack(pady=20)


root.mainloop()
