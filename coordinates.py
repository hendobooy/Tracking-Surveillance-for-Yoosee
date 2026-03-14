import tkinter as tk
import pyautogui

def atualizar_coordenadas():
    # Pega a posição do mouse
    x, y = pyautogui.position()
    label.config(text=f"Mouse: X={x} Y={y}")
    # Atualiza a cada 10ms
    root.after(10, atualizar_coordenadas)

# Configuração da Janela (Pop-up)
root = tk.Tk()
root.title("Coordenadas")
root.attributes("-topmost", True)  # Mantém sempre no topo
root.attributes("-alpha", 0.8)     # Deixa levemente transparente
root.overrideredirect(True)        # Remove as bordas da janela
root.geometry("200x40+10+10")      # Tamanho e posição inicial (canto superior)

label = tk.Label(root, text="", font=("Helvetica", 12, "bold"), fg="white", bg="black")
label.pack(expand=True, fill="both")

# Inicia a atualização
atualizar_coordenadas()
root.mainloop()