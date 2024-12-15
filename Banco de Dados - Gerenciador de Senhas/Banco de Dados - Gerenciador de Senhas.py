import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import sqlite3
from cryptography.fernet import Fernet
import os

# --- Funções de Criptografia ---
def gerar_chave():
    chave = Fernet.generate_key()
    return chave

def criptografar(mensagem, chave):
    f = Fernet(chave)
    mensagem_criptografada = f.encrypt(mensagem.encode())
    return mensagem_criptografada

def descriptografar(mensagem_criptografada, chave):
    f = Fernet(chave)
    mensagem_descriptografada = f.decrypt(mensagem_criptografada).decode()
    return mensagem_descriptografada

# --- Funções do Banco de Dados ---
def criar_tabela():
    conexao = sqlite3.connect('senhas.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            nome TEXT,  -- Campo "Nome" adicionado
            usuario TEXT,
            senha BLOB NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

def salvar_senha(site, nome, usuario, senha_criptografada): #Adicionado o campo nome no banco de dados
    conexao = sqlite3.connect('senhas.db')
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO senhas (site, nome, usuario, senha) VALUES (?, ?, ?, ?)", (site, nome, usuario, senha_criptografada))#Adicionado o campo nome no banco de dados
    conexao.commit()
    conexao.close()

def buscar_senhas(termo_busca): #Função de busca implementada
    conexao = sqlite3.connect('senhas.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT id, site, nome, usuario, senha FROM senhas WHERE site LIKE ? OR nome LIKE ?", ('%' + termo_busca + '%', '%' + termo_busca + '%',)) #Busca pelo site ou pelo nome
    resultados = cursor.fetchall()
    conexao.close()
    return resultados

def atualizar_senha(id, site, nome, usuario, senha_criptografada): #Função para atualizar os dados no banco de dados.
    conexao = sqlite3.connect('senhas.db')
    cursor = conexao.cursor()
    cursor.execute("UPDATE senhas SET site=?, nome=?, usuario=?, senha=? WHERE id=?", (site, nome, usuario, senha_criptografada, id))
    conexao.commit()
    conexao.close()

def excluir_senha(id): #Função para excluir dados do banco de dados.
    conexao = sqlite3.connect('senhas.db')
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM senhas WHERE id=?", (id,))
    conexao.commit()
    conexao.close()

def buscar_todas_senhas():
    conexao = sqlite3.connect('senhas.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT site, nome, usuario, senha FROM senhas")
    resultados = cursor.fetchall()
    conexao.close()
    return resultados

# --- Interface Gráfica ---
def salvar_senha_interface():
    site = entry_site.get()
    nome = entry_nome.get() # Pega o valor do campo nome
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    if not site or not senha or not nome: #Verifica se o campo nome também foi preenchido.
        messagebox.showerror("Erro", "Preencha todos os campos.")
        return

    senha_criptografada = criptografar(senha, chave)
    salvar_senha(site, nome, usuario, senha_criptografada) #Adicionado o campo nome na função salvar senha

    messagebox.showinfo("Sucesso", "Senha salva com sucesso.")
    entry_site.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_usuario.delete(0, tk.END)
    entry_senha.delete(0, tk.END)


def visualizar_senhas_interface():
    def editar_senha():
        try:
            indice_selecionado = listbox_senhas.curselection()[0]
            id_selecionado = resultados_exibidos[indice_selecionado][0]
            site_atual = resultados_exibidos[indice_selecionado][1]
            nome_atual = resultados_exibidos[indice_selecionado][2]
            usuario_atual = resultados_exibidos[indice_selecionado][3]
            senha_criptografada_atual = resultados_exibidos[indice_selecionado][4]
            senha_descriptografada_atual = descriptografar(senha_criptografada_atual, chave)

            # Dialogo para editar todos os campos
            janela_edicao = tk.Toplevel(janela_visualizacao)
            janela_edicao.title("Editar Senha")
            janela_edicao.configure(bg="#CCFF00")

            label_site_edicao = tk.Label(janela_edicao, text="Site:", font=("Arial",12), bg="#CCFF00")
            entry_site_edicao = tk.Entry(janela_edicao, font=("Arial",12))
            entry_site_edicao.insert(0, site_atual) #insere o valor atual do site no entry

            label_nome_edicao = tk.Label(janela_edicao, text="Nome:", font=("Arial",12), bg="#CCFF00")
            entry_nome_edicao = tk.Entry(janela_edicao, font=("Arial",12))
            entry_nome_edicao.insert(0, nome_atual)

            label_usuario_edicao = tk.Label(janela_edicao, text="Usuário:", font=("Arial",12), bg="#CCFF00")
            entry_usuario_edicao = tk.Entry(janela_edicao, font=("Arial",12))
            entry_usuario_edicao.insert(0, usuario_atual)

            label_senha_edicao = tk.Label(janela_edicao, text="Senha:", font=("Arial",12), bg="#CCFF00")
            entry_senha_edicao = tk.Entry(janela_edicao, show="*", font=("Arial",12))
            entry_senha_edicao.insert(0, senha_descriptografada_atual)


            def salvar_edicao(): #função para salvar as alterações feitas
                novo_site = entry_site_edicao.get()
                novo_nome = entry_nome_edicao.get()
                novo_usuario = entry_usuario_edicao.get()
                nova_senha = entry_senha_edicao.get()

                senha_criptografada_nova = criptografar(nova_senha, chave)
                atualizar_senha(id_selecionado, novo_site, novo_nome, novo_usuario, senha_criptografada_nova)
                messagebox.showinfo("Sucesso", "Senha atualizada.")
                atualizar_listbox()
                janela_edicao.destroy() #fecha a janela de edição

            botao_salvar_edicao = tk.Button(janela_edicao, text="Salvar", command=salvar_edicao, font=("Arial",12,"bold"), bg="#5F003A", fg="#ffffff")

            label_site_edicao.grid(row=0, column=0)
            entry_site_edicao.grid(row=0, column=1)
            label_nome_edicao.grid(row=1, column=0)
            entry_nome_edicao.grid(row=1, column=1)
            label_usuario_edicao.grid(row=2, column=0)
            entry_usuario_edicao.grid(row=2, column=1)
            label_senha_edicao.grid(row=3, column=0)
            entry_senha_edicao.grid(row=3, column=1)
            botao_salvar_edicao.grid(row=4, column=1)

        except IndexError:
            messagebox.showerror("Erro", "Selecione um item para editar.")

    def excluir_senha_interface():  # Renomeia a função interna (CORRETO)
        try:
            indice_selecionado = listbox_senhas.curselection()[0]
            id_selecionado = resultados_exibidos[indice_selecionado][0]
            site_selecionado = resultados_exibidos[indice_selecionado][1]
            resposta = messagebox.askyesno("Confirmação", f"Deseja excluir a senha de {site_selecionado}?")
            if resposta:
                excluir_senha(id_selecionado)  # Chama a função do banco de dados (CORRETO)
                messagebox.showinfo("Sucesso", "Senha excluída.")
                atualizar_listbox()
        except IndexError:
            messagebox.showerror("Erro", "Selecione um item para excluir.")
    
    def atualizar_listbox():
        listbox_senhas.delete(0, tk.END)
        resultados = buscar_senhas(entry_busca_visualizar.get())
        global resultados_exibidos
        resultados_exibidos = resultados
        if resultados:
            for resultado in resultados:
                listbox_senhas.insert(tk.END, f"Site: {resultado[1]}, Nome: {resultado[2]}, Usuário: {resultado[3]}, Senha: {descriptografar(resultado[4], chave)}") # Exibe todos os dados
        else:
            listbox_senhas.insert(tk.END, "Nenhuma senha encontrada.")

    janela_visualizacao = tk.Toplevel(janela)
    janela_visualizacao.title("Senhas Salvas")
    janela_visualizacao.configure(bg="#00FF72")

    # Widgets 
    label_busca_visualizar = tk.Label(janela_visualizacao, text="Buscar Site/Nome:", font=("arial",12), bg="#00FF72")
    entry_busca_visualizar = tk.Entry(janela_visualizacao)
    botao_buscar_visualizar = tk.Button(janela_visualizacao, text="Buscar", command=atualizar_listbox, font=("Arial",12,"bold"), bg="#7A0067", fg="#ffffff")

    listbox_senhas = tk.Listbox(janela_visualizacao, width=80, font=("Courier", 10))

    botao_editar_visualizar = tk.Button(janela_visualizacao, text="Editar", command=editar_senha, font=("Arial",12,"bold"), bg="#01731F", fg="#ffffff")
    botao_excluir_visualizar = tk.Button(janela_visualizacao, text="Excluir", command=excluir_senha_interface, font=("Arial",12,"bold"), bg="#750000", fg="#ffffff")

    # Layout com padding para espaçamento
    label_busca_visualizar.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_busca_visualizar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    botao_buscar_visualizar.grid(row=0, column=2, padx=5, pady=5)
    listbox_senhas.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew") #sticky para expandir
    botao_editar_visualizar.grid(row=2, column=1, padx=5, pady=5)
    botao_excluir_visualizar.grid(row=2, column=2, padx=5, pady=5)
    
    janela_visualizacao.columnconfigure(1, weight=1)

    atualizar_listbox()

# --- Inicialização ---
criar_tabela()

if not os.path.exists("chave.key"):
    chave = gerar_chave()
    with open("chave.key", "wb") as arquivo_chave:
        arquivo_chave.write(chave)
else:
    with open("chave.key", "rb") as arquivo_chave:
        chave = arquivo_chave.read()

janela = tk.Tk()
janela.title("Gerenciador de Senhas")
janela.configure(bg="#e0f2f7") # Cor de fundo da janela principal

# --- Widgets ---
label_site = tk.Label(janela, text="Site:", background="#e0f2f7", foreground="#1a237e", font=("Arial", 12))
entry_site = tk.Entry(janela, font=("Arial",12))

label_nome = tk.Label(janela, text="Nome da conta:", background="#e0f2f7", foreground="#1a237e", font=("Arial", 12))
entry_nome = tk.Entry(janela, font=("Arial",12))

label_usuario = tk.Label(janela, text="Usuário:", background="#e0f2f7", foreground="#1a237e", font=("Arial", 12))
entry_usuario = tk.Entry(janela, font=("Arial",12))
label_senha = tk.Label(janela, text="Senha:", background="#e0f2f7", foreground="#1a237e", font=("Arial", 12))
entry_senha = tk.Entry(janela, show="*", font=("Arial",12))

botao_salvar = tk.Button(janela, text="Salvar Senha", command=salvar_senha_interface, font=("Arial", 12, "bold"), bg="#006956", fg="#ffffff")
botao_visualizar = tk.Button(janela, text="Visualizar Senhas", command=visualizar_senhas_interface, font=("Arial", 12, "bold"), bg="#3A7C00", fg="#ffffff")

# --- Layout --- (Com padding e sticky)
label_site.grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_site.grid(row=0, column=1, padx=10, pady=5, sticky="ew") #sticky para ocupar espaço horizontal
label_nome.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_nome.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
label_usuario.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_usuario.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
label_senha.grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_senha.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
botao_salvar.grid(row=4, column=1, padx=10, pady=10)
botao_visualizar.grid(row=5, column=1, padx=10, pady=10)

janela.columnconfigure(1, weight=1)  # Configura a coluna 1 para expandir

janela.mainloop()