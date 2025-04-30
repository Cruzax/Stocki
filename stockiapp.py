import customtkinter as ctk
import os
import psutil
import threading
import time

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Stocki Assist")
app.geometry("700x700")
app.configure(bg="#A8DADC")

main_frame = ctk.CTkFrame(master=app, fg_color="#A8DADC")
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

chat_box = ctk.CTkTextbox(master=main_frame, corner_radius=10, width=600, height=500, font=("Helvetica", 14))
chat_box.pack(pady=10)
chat_box.configure(state="disabled")

entry = ctk.CTkEntry(master=main_frame, width=500, height=40, placeholder_text="Écris ta demande ici...")
entry.pack(pady=(10,5))

def envoyer():
    user_message = entry.get()
    if user_message.strip() != "":
        afficher_message("Moi", user_message)
        entry.delete(0, "end")
        threading.Thread(target=repondre, args=(user_message,)).start()

send_button = ctk.CTkButton(master=main_frame, text="Envoyer", command=envoyer)
send_button.pack()

def afficher_message(auteur, message):
    chat_box.configure(state="normal")
    if auteur == "Moi":
        chat_box.insert("end", f"🧑 {message}\n\n")
    else:
        for lettre in message:
            chat_box.insert("end", lettre)
            chat_box.update()
            time.sleep(0.02)  # Vitesse d'apparition des lettres
        chat_box.insert("end", "\n\n")
    chat_box.configure(state="disabled")
    chat_box.see("end")

def loading_message():
    chat_box.configure(state="normal")
    load = chat_box.index("end-1c")
    chat_box.insert("end", "🤖 ...\n")
    chat_box.update()
    return load

def remove_loading(load_index):
    chat_box.delete(load_index, "end")

def repondre(message):
    load_index = loading_message()
    time.sleep(1.2)  # Simulation temps de réflexion Stocki
    chat_box.configure(state="normal")
    remove_loading(load_index)

    if "stockage" in message.lower():
        usage = psutil.disk_usage('/')
        total = usage.total // (2**30)
        free = usage.free // (2**30)
        afficher_message("Stocki", f"Ton disque fait {total} Go.\nIl te reste {free} Go libres.")
    elif "nettoyage" in message.lower():
        afficher_message("Stocki", "Je prépare un scan... 🚀 (à venir très bientôt)")
    else:
        afficher_message("Stocki", "Hmm... Je n'ai pas compris. Réessaye avec d'autres mots ! 🤔")

app.mainloop()
