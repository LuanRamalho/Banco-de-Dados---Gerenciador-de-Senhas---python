import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import json
import os
import random
import string
from cryptography.fernet import Fernet

# --- Configurações de Criptografia ---
CHAVE_FILE = "chave.key"
DB_JSON = "senhas.json"

def carregar_ou_gerar_chave():
    if not os.path.exists(CHAVE_FILE):
        chave = Fernet.generate_key()
        with open(CHAVE_FILE, "wb") as f:
            f.write(chave)
        return chave
    with open(CHAVE_FILE, "rb") as f:
        return f.read()

chave = carregar_ou_gerar_chave()
fernet = Fernet(chave)

# --- Funções de Persistência JSON (NoSQL) ---
def carregar_dados():
    if not os.path.exists(DB_JSON):
        return []
    with open(DB_JSON, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def salvar_dados(dados):
    with open(DB_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- Janela do Gerador de Senhas ---
class JanelaGerador(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Gerar Senha Forte")
        self.geometry("350x450")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)

        tk.Label(self, text="GERADOR DE SENHAS", font=("Arial", 12, "bold"), bg="#f0f0f0", pady=10).pack()

        self.vars = {
            "Maiúsculas": tk.BooleanVar(value=True),
            "Minúsculas": tk.BooleanVar(value=True),
            "Números": tk.BooleanVar(value=True),
            "Especiais": tk.BooleanVar(value=True)
        }

        for texto, var in self.vars.items():
            tk.Checkbutton(self, text=texto, variable=var, bg="#f0f0f0", font=("Arial", 10)).pack(anchor="w", padx=50)

        tk.Label(self, text="Tamanho da Senha:", bg="#f0f0f0", pady=5).pack()
        self.ent_tamanho = tk.Entry(self, width=5, justify="center")
        self.ent_tamanho.insert(0, "16")
        self.ent_tamanho.pack()

        self.ent_resultado = tk.Entry(self, font=("Consolas", 12), justify="center", bd=2)
        self.ent_resultado.pack(pady=20, padx=20, fill="x")

        tk.Button(self, text="Gerar Senha", command=self.gerar, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Button(self, text="Copiar Senha", command=self.copiar, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

    def gerar(self):
        caracteres = ""
        if self.vars["Maiúsculas"].get(): caracteres += string.ascii_uppercase
        if self.vars["Minúsculas"].get(): caracteres += string.ascii_lowercase
        if self.vars["Números"].get(): caracteres += string.digits
        if self.vars["Especiais"].get(): caracteres += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not caracteres:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma opção!")
            return

        try:
            tamanho = int(self.ent_tamanho.get())
            senha = "".join(random.choice(caracteres) for _ in range(tamanho))
            self.ent_resultado.delete(0, tk.END)
            self.ent_resultado.insert(0, senha)
        except ValueError:
            messagebox.showerror("Erro", "Insira um número válido.")

    def copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.ent_resultado.get())
        messagebox.showinfo("Copiado", "Senha copiada!")

# --- Interface de Detalhes ---
class JanelaDetalhes(tk.Toplevel):
    def __init__(self, master, dados_originais, index=None):
        super().__init__(master)
        self.title("Detalhes da Conta")
        self.geometry("500x700")
        self.configure(bg="#f0f0f0")
        
        if index is not None:
            self.dados = dados_originais[index].copy()
        else:
            self.dados = {"site": "", "nome": "", "usuario": "", "senha": ""}
            
        self.index = index
        self.dados_originais = dados_originais
        self.entries = {}
        self.senhas_extras = []
        
        for chave_nome in self.dados.keys():
            if "senha" in chave_nome.lower() and chave_nome.lower() != "senha":
                self.senhas_extras.append(chave_nome)

        self.container = tk.Frame(self, bg="#f0f0f0")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.renderizar_campos()
        
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text="+ Texto Extra", command=lambda: self.add_campo(False), 
                  bg="#2196F3", fg="white", font=("Arial", 8, "bold")).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="+ Senha Extra", command=lambda: self.add_campo(True), 
                  bg="#9C27B0", fg="white", font=("Arial", 8, "bold")).pack(side="left", padx=10)

        tk.Button(btn_frame, text="🔑 Gerador", command=lambda: JanelaGerador(self), 
                  bg="#607D8B", fg="white", font=("Arial", 8, "bold")).pack(side="left", padx=10)
        
        tk.Button(self, text="Salvar Alterações", command=self.salvar, 
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(fill="x", padx=20, pady=10)

    def renderizar_campos(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.entries = {}
        
        campos_fixos = ["site", "nome", "usuario", "senha"]
            
        for i, (label, valor) in enumerate(self.dados.items()):
            tk.Label(self.container, text=f"{label.upper()}:", bg="#f0f0f0", 
                     font=("Arial", 8, "bold"), fg="#555").grid(row=i, column=0, sticky="w", pady=8)
            
            frame_input = tk.Frame(self.container, bg="#f0f0f0")
            frame_input.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            
            is_senha = (label == "senha" or label in self.senhas_extras)
            
            val_str = valor
            if is_senha and valor:
                try: val_str = fernet.decrypt(valor.encode()).decode()
                except: val_str = valor
                
            ent = tk.Entry(frame_input, font=("Arial", 10), show="*" if is_senha else "")
            ent.insert(0, str(val_str))
            ent.pack(side="left", fill="x", expand=True)
            self.entries[label] = ent
            
            if is_senha:
                btn_olho = tk.Button(frame_input, text="👁️", width=3, relief="flat", bg="#f0f0f0")
                btn_olho.config(command=lambda e=ent, b=btn_olho: self.toggle_senha(e, b))
                btn_olho.pack(side="right", padx=2)
            
            if label not in campos_fixos:
                btn_del = tk.Button(frame_input, text="✕", width=3, fg="red", relief="flat",
                                   command=lambda c=label: self.remover_campo(c), bg="#f0f0f0")
                btn_del.pack(side="right", padx=2)
            
        self.container.columnconfigure(1, weight=1)

    def toggle_senha(self, entry, botao):
        if entry.cget("show") == "*":
            entry.config(show="")
            botao.config(text="🙈")
        else:
            entry.config(show="*")
            botao.config(text="👁️")

    def add_campo(self, eh_senha):
        nome = simpledialog.askstring("Novo Campo", "Nome do campo:")
        if nome:
            chave = nome.strip().lower()
            if chave not in self.dados:
                self.dados[chave] = ""
                if eh_senha: self.senhas_extras.append(chave)
                self.renderizar_campos()

    def remover_campo(self, chave):
        if messagebox.askyesno("Confirmar", f"Remover '{chave}'?"):
            if chave in self.senhas_extras: self.senhas_extras.remove(chave)
            del self.dados[chave]
            self.renderizar_campos()

    def salvar(self):
        novo_reg = {}
        for campo, entry in self.entries.items():
            valor = entry.get()
            if campo == "senha" or campo in self.senhas_extras:
                valor = fernet.encrypt(valor.encode()).decode()
            novo_reg[campo] = valor
        
        if self.index is not None: self.dados_originais[self.index] = novo_reg
        else: self.dados_originais.append(novo_reg)
            
        salvar_dados(self.dados_originais)
        self.master.atualizar_listbox()
        self.destroy()

# --- Janela Principal ---
class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Senhas")
        self.geometry("950x600")
        self.configure(bg="#00FF72")
        
        self.indice_selecionado = None
        self.card_selecionado_widget = None
        
        # Pesquisa
        frame_topo = tk.Frame(self, bg="#00FF72")
        frame_topo.pack(fill="x", padx=15, pady=15)
        
        tk.Label(frame_topo, text="PESQUISAR:", bg="#00FF72", font=("Arial", 9, "bold")).pack(side="left")
        self.ent_busca = tk.Entry(frame_topo, font=("Arial", 11))
        self.ent_busca.pack(side="left", fill="x", expand=True, padx=10)
        self.ent_busca.bind("<KeyRelease>", lambda e: self.atualizar_listbox())
        
        # Área de Cards com Scroll
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Frame que contém os cards
        self.frame_cards = tk.Frame(self.canvas, bg="white")
        
        # Configurar grid dinâmico para preencher largura
        self.frame_cards.columnconfigure(0, weight=1)
        self.frame_cards.columnconfigure(1, weight=1)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame_cards, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.frame_cards.bind("<Configure>", self.ajustar_scroll)
        self.canvas.bind("<Configure>", self.ajustar_largura_frame)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=(15, 0))
        self.scrollbar.pack(side="right", fill="y", padx=(0, 15))

        # Rodapé
        frame_btns = tk.Frame(self, bg="#00FF72")
        frame_btns.pack(fill="x", pady=15)
        
        tk.Button(frame_btns, text="Novo Registro", command=self.novo_registro, 
                  bg="#01731F", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=15)
        
        tk.Button(frame_btns, text="Excluir Permanentemente", command=self.excluir, 
                  bg="#750000", fg="white", font=("Arial", 9)).pack(side="right", padx=15)

        self.atualizar_listbox()

    def ajustar_scroll(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def ajustar_largura_frame(self, event):
        # Ajusta a largura do frame interno para o tamanho do canvas ao maximizar
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def criar_card(self, item, real_index, row, col):
        card = tk.Frame(self.frame_cards, bg="white", highlightbackground="#01731F", 
                        highlightthickness=1, cursor="hand2", padx=15, pady=10)
        # Sticky 'ew' faz o card expandir horizontalmente no grid
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        nome = item.get('nome', 'Sem Nome').upper()
        site = item.get('site', 'Sem Site')
        
        lbl_nome = tk.Label(card, text=nome, font=("Segoe UI", 10, "bold"), bg="white", fg="#01731F")
        lbl_nome.pack(anchor="w")
        
        lbl_site = tk.Label(card, text=site, font=("Segoe UI", 9), bg="white", fg="#555")
        lbl_site.pack(anchor="w")
        
        for w in [card, lbl_nome, lbl_site]:
            w.bind("<Button-1>", lambda e, idx=real_index, c=card: self.selecionar_card(idx, c))
            w.bind("<Double-1>", lambda e, idx=real_index: self.abrir_detalhes_manual(idx))

    def selecionar_card(self, index, widget):
        if self.card_selecionado_widget:
            self.card_selecionado_widget.config(bg="white")
            for child in self.card_selecionado_widget.winfo_children():
                child.config(bg="white")
        
        self.indice_selecionado = index
        self.card_selecionado_widget = widget
        widget.config(bg="#E0FFE0")
        for child in widget.winfo_children():
            child.config(bg="#E0FFE0")

    def atualizar_listbox(self):
        for widget in self.frame_cards.winfo_children():
            widget.destroy()
        
        self.indice_selecionado = None
        self.card_selecionado_widget = None
        self.dados_atuais = carregar_dados()
        termo = self.ent_busca.get().lower()
        
        # Filtra e posiciona em 2 colunas
        itens_filtrados = [i for i, item in enumerate(self.dados_atuais) 
                          if termo in item.get('nome', '').lower() or termo in item.get('site', '').lower()]
        
        for i, real_index in enumerate(itens_filtrados):
            row = i // 2
            col = i % 2
            self.criar_card(self.dados_atuais[real_index], real_index, row, col)

    def abrir_detalhes_manual(self, index):
        JanelaDetalhes(self, self.dados_atuais, index)

    def novo_registro(self):
        JanelaDetalhes(self, carregar_dados())

    def excluir(self):
        if self.indice_selecionado is not None:
            if messagebox.askyesno("Confirmar", "Deletar este item do banco JSON?"):
                dados = carregar_dados()
                dados.pop(self.indice_selecionado)
                salvar_dados(dados)
                self.atualizar_listbox()
        else:
            messagebox.showwarning("Aviso", "Selecione um card primeiro.")

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
