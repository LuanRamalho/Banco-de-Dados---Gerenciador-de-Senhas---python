import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import json
import os
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

# --- Funções de Persistência JSON ---
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

# --- Interface de Detalhes e Edição ---
class JanelaDetalhes(tk.Toplevel):
    def __init__(self, master, dados_originais, index=None):
        super().__init__(master)
        self.title("Detalhes da Conta")
        self.geometry("500x600")
        self.configure(bg="#f0f0f0")
        
        # Estrutura base para novos registros ou cópia de existentes
        if index is not None:
            self.dados = dados_originais[index].copy()
        else:
            self.dados = {"site": "", "nome": "", "usuario": "", "senha": ""}
            
        self.index = index
        self.dados_originais = dados_originais
        self.entries = {}
        
        # Usamos um Canvas para permitir scroll caso haja muitos campos extras
        self.container = tk.Frame(self, bg="#f0f0f0")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.renderizar_campos()
        
        # Rodapé da Janela
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(btn_frame, text="+ Campo Extra", command=self.add_campo_extra, 
                  bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=20)
        
        tk.Button(btn_frame, text="Salvar Alterações", command=self.salvar, 
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="right", padx=20)

    def renderizar_campos(self):
        """Renderiza campos fixos e extras com botões de ação."""
        for widget in self.container.winfo_children():
            widget.destroy()
        self.entries = {}
        
        campos_fixos = ["site", "nome", "usuario", "senha"]
            
        for i, (label, valor) in enumerate(self.dados.items()):
            # Label do campo
            tk.Label(self.container, text=f"{label.upper()}:", bg="#f0f0f0", 
                     font=("Arial", 8, "bold"), fg="#555").grid(row=i, column=0, sticky="w", pady=8)
            
            # Frame para alinhar Entry + Botões
            frame_input = tk.Frame(self.container, bg="#f0f0f0")
            frame_input.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            
            # Tratamento de senha
            is_senha = (label == "senha")
            val_str = valor
            if is_senha and valor:
                try: val_str = fernet.decrypt(valor.encode()).decode()
                except: val_str = valor
                
            ent = tk.Entry(frame_input, font=("Arial", 10), show="*" if is_senha else "")
            ent.insert(0, str(val_str))
            ent.pack(side="left", fill="x", expand=True)
            self.entries[label] = ent
            
            # Botão de Olho (Apenas para Senha)
            if is_senha:
                self.ent_senha = ent
                self.btn_olho = tk.Button(frame_input, text="👁️", width=3, command=self.toggle_senha, 
                                         relief="flat", bg="#f0f0f0", cursor="hand2")
                self.btn_olho.pack(side="right", padx=2)
            
            # Botão de Remover (Apenas para Campos Extras)
            if label not in campos_fixos:
                btn_del = tk.Button(frame_input, text="🗑️", width=3, fg="red", relief="flat",
                                   command=lambda c=label: self.remover_campo(c), bg="#f0f0f0", cursor="hand2")
                btn_del.pack(side="right", padx=2)
            
        self.container.columnconfigure(1, weight=1)

    def toggle_senha(self):
        """Alterna visibilidade da senha."""
        if self.ent_senha.cget("show") == "*":
            self.ent_senha.config(show="")
            self.btn_olho.config(text="🙈")
        else:
            self.ent_senha.config(show="*")
            self.btn_olho.config(text="👁️")

    def add_campo_extra(self):
        """Cria uma nova chave no dicionário NoSQL."""
        nome = simpledialog.askstring("Novo Campo", "Nome do campo:")
        if nome:
            chave = nome.strip().lower()
            if chave not in self.dados:
                self.dados[chave] = ""
                self.renderizar_campos()

    def remover_campo(self, chave):
        """Remove um campo extra do registro atual."""
        if messagebox.askyesno("Confirmar", f"Remover o campo '{chave}'?"):
            del self.dados[chave]
            self.renderizar_campos()

    def salvar(self):
        """Converte as Entries de volta para o dicionário e salva no JSON."""
        novo_registro = {}
        for campo, entry in self.entries.items():
            valor = entry.get()
            if campo == "senha":
                valor = fernet.encrypt(valor.encode()).decode()
            novo_registro[campo] = valor
        
        if self.index is not None:
            self.dados_originais[self.index] = novo_registro
        else:
            self.dados_originais.append(novo_registro)
            
        salvar_dados(self.dados_originais)
        messagebox.showinfo("Sucesso", "Registro atualizado no JSON!")
        self.master.atualizar_listbox()
        self.destroy()

# --- Janela Principal ---
class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador NoSQL (JSON)")
        self.geometry("600x450")
        self.configure(bg="#00FF72")
        
        # Header / Busca
        frame_topo = tk.Frame(self, bg="#00FF72")
        frame_topo.pack(fill="x", padx=15, pady=15)
        
        tk.Label(frame_topo, text="PESQUISAR:", bg="#00FF72", font=("Arial", 9, "bold")).pack(side="left")
        self.ent_busca = tk.Entry(frame_topo, font=("Arial", 11))
        self.ent_busca.pack(side="left", fill="x", expand=True, padx=10)
        self.ent_busca.bind("<KeyRelease>", lambda e: self.atualizar_listbox())
        
        # Lista de Registros
        self.listbox = tk.Listbox(self, font=("Segoe UI", 10), selectbackground="#01731F")
        self.listbox.pack(fill="both", expand=True, padx=15)
        self.listbox.bind("<Double-1>", lambda e: self.abrir_detalhes())

        # Botões de Ação
        frame_btns = tk.Frame(self, bg="#00FF72")
        frame_btns.pack(fill="x", pady=15)
        
        tk.Button(frame_btns, text="Novo Registro", command=self.novo_registro, 
                  bg="#01731F", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=15)
        
        tk.Button(frame_btns, text="Excluir Permanentemente", command=self.excluir, 
                  bg="#750000", fg="white", font=("Arial", 9)).pack(side="right", padx=15)

        self.atualizar_listbox()

    def atualizar_listbox(self):
        self.listbox.delete(0, tk.END)
        self.dados_atuais = carregar_dados()
        termo = self.ent_busca.get().lower()
        
        for item in self.dados_atuais:
            nome = item.get('nome', 'Sem Nome').upper()
            site = item.get('site', 'Sem Site')
            if termo in nome.lower() or termo in site.lower():
                self.listbox.insert(tk.END, f" {nome}  |  {site}")

    def abrir_detalhes(self):
        selecao = self.listbox.curselection()
        if selecao:
            JanelaDetalhes(self, self.dados_atuais, selecao[0])

    def novo_registro(self):
        JanelaDetalhes(self, carregar_dados())

    def excluir(self):
        selecao = self.listbox.curselection()
        if selecao and messagebox.askyesno("Confirmar", "Deletar este item do banco JSON?"):
            dados = carregar_dados()
            dados.pop(selecao[0])
            salvar_dados(dados)
            self.atualizar_listbox()

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()