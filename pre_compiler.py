"""
Misteremio Bot Pre-Compiler
Ferramenta do Desenvolvedor para compilar o Misteremio Bot com data de expiracao customizada.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import shutil
import os
import re
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

MAIN_PY = os.path.join(os.path.dirname(__file__), "main.py")


class PreCompilerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Misteremio Bot Pre-Compiler")
        self.geometry("520x620")
        self.resizable(False, False)
        self.configure(fg_color="#0d0d0d")

        # ---- HEADER ----
        header = ctk.CTkFrame(self, fg_color="#111", corner_radius=0)
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header, text="⚙  Misteremio Bot Pre-Compiler",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d26a"
        ).pack(pady=10)
        ctk.CTkLabel(
            header, text="Ferramenta do Desenvolvedor · Zezenia Bot",
            font=ctk.CTkFont(size=11),
            text_color="#888"
        ).pack(pady=(0, 10))

        # ---- DATA DE EXPIRACAO ----
        date_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        date_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            date_frame, text="Data de Expiração",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            date_frame, text="O bot funcionará até (inclusive) a data abaixo:",
            font=ctk.CTkFont(size=11), text_color="#aaa"
        ).pack(anchor="w", padx=15)

        row = ctk.CTkFrame(date_frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=10)

        # Dia
        ctk.CTkLabel(row, text="Dia", font=ctk.CTkFont(size=11), text_color="#bbb", width=60).pack(side="left")
        self.day_var = ctk.StringVar(value="31")
        self.entry_day = ctk.CTkEntry(row, textvariable=self.day_var, width=60, justify="center",
                                      fg_color="#222", text_color="white", border_color="#444")
        self.entry_day.pack(side="left", padx=(0, 10))

        # Mes
        ctk.CTkLabel(row, text="Mês", font=ctk.CTkFont(size=11), text_color="#bbb", width=60).pack(side="left")
        self.month_var = ctk.StringVar(value="03")
        self.entry_month = ctk.CTkEntry(row, textvariable=self.month_var, width=60, justify="center",
                                        fg_color="#222", text_color="white", border_color="#444")
        self.entry_month.pack(side="left", padx=(0, 10))

        # Ano
        ctk.CTkLabel(row, text="Ano", font=ctk.CTkFont(size=11), text_color="#bbb", width=60).pack(side="left")
        self.year_var = ctk.StringVar(value="2026")
        self.entry_year = ctk.CTkEntry(row, textvariable=self.year_var, width=80, justify="center",
                                       fg_color="#222", text_color="white", border_color="#444")
        self.entry_year.pack(side="left", padx=(0, 10))

        # Preview da data
        self.lbl_preview = ctk.CTkLabel(
            date_frame, text="", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d26a"
        )
        self.lbl_preview.pack(pady=(0, 12))

        for v in [self.day_var, self.month_var, self.year_var]:
            v.trace_add("write", lambda *a: self.update_preview())
        self.update_preview()

        # ---- PASTA DE SAIDA ----
        out_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        out_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            out_frame, text="Pasta de Saída",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="white"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        self.output_var = ctk.StringVar(value=r"d:\Antigravity_Projects\Misteremio Bot_Release")
        ctk.CTkEntry(out_frame, textvariable=self.output_var, width=460,
                     fg_color="#222", text_color="white", border_color="#444"
                     ).pack(padx=15, pady=(0, 12))

        # ---- BOTAO COMPILAR ---- (fixo no bottom antes do log)
        self.btn_compile = ctk.CTkButton(
            self, text="⚡  COMPILAR EXECUTÁVEL",
            height=48, font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#00d26a", hover_color="#009950", text_color="black",
            corner_radius=6, command=self.start_build
        )
        self.btn_compile.pack(fill="x", padx=20, pady=(5, 5))

        # ---- LOG ----
        log_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        ctk.CTkLabel(
            log_frame, text="Log de Build",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#888"
        ).pack(anchor="w", padx=15, pady=(8, 2))

        self.log_box = ctk.CTkTextbox(
            log_frame, fg_color="#0a0a0a", text_color="#00ff88",
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=4, height=100
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def update_preview(self):
        try:
            d = int(self.day_var.get())
            m = int(self.month_var.get())
            y = int(self.year_var.get())
            dt = datetime(y, m, d)
            self.lbl_preview.configure(
                text=f"✓  Válido até: {d:02d}/{m:02d}/{y}",
                text_color="#00d26a"
            )
        except Exception:
            self.lbl_preview.configure(text="⚠  Data inválida", text_color="#e74c3c")

    def log(self, msg, color="#00ff88"):
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")

    def start_build(self):
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            datetime(year, month, day)  # Valida
        except Exception:
            messagebox.showerror("Data Inválida", "Por favor insira uma data válida.")
            return

        self.btn_compile.configure(state="disabled", text="⏳  Compilando...")
        self.log_box.delete("1.0", "end")
        threading.Thread(target=self._build, args=(day, month, year), daemon=True).start()

    def _build(self, day, month, year):
        try:
            output_dir = self.output_var.get()
            date_display = f"{day:02d}/{month:02d}/{year}"

            # Calcula o dia seguinte (inicio do bloqueio)
            from datetime import timedelta
            expiry_dt = datetime(year, month, day) + timedelta(days=1)
            ey, em, ed = expiry_dt.year, expiry_dt.month, expiry_dt.day

            self.after(0, self.log, f"> Lendo main.py...", "#00ff88")

            with open(MAIN_PY, "r", encoding="utf-8") as f:
                original = f.read()

            # Substitui a linha de expiracao dinamicamente
            new_lines = []
            for line in original.split("\n"):
                if "expiry_date = datetime(" in line:
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(" " * indent + f'expiry_date = datetime({ey}, {em}, {ed})  # Valido ate {date_display}')
                elif '"Licença Expirada"' in line or "'Licença Expirada'" in line:
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(" " * indent + f'tkinter.messagebox.showerror("Licença Expirada", "A licença do Misteremio Bot era válida até {date_display} e acabou de expirar.\\nEntre em contato com o desenvolvedor.")')
                else:
                    new_lines.append(line)

            modified = "\n".join(new_lines)

            self.after(0, self.log, f"> Injetando data: valido ate {date_display}...", "#00ff88")
            with open(MAIN_PY, "w", encoding="utf-8") as f:
                f.write(modified)

            try:
                self.after(0, self.log, "> Iniciando PyInstaller (pode levar alguns minutos)...", "#ffaa00")

                cwd = os.path.dirname(MAIN_PY)
                proc = subprocess.Popen(
                    ["pyinstaller", "Misteremio Bot.spec", "--noconfirm"],
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in proc.stdout:
                    stripped = line.strip()
                    if "INFO:" in stripped or "WARNING:" in stripped or "ERROR:" in stripped:
                        short = stripped.split("INFO:")[-1].split("WARNING:")[-1].split("ERROR:")[-1].strip()
                        if short:
                            self.after(0, self.log, f"  {short[:90]}", "#666")
                proc.wait()

                exe_src = os.path.join(cwd, "dist", "Misteremio Bot.exe")
                if os.path.exists(exe_src):
                    # Monta pasta de saida
                    os.makedirs(output_dir, exist_ok=True)
                    shutil.copy(exe_src, os.path.join(output_dir, "Misteremio Bot.exe"))

                    # Assets
                    prints_src = os.path.join(cwd, "prints")
                    prints_dst = os.path.join(output_dir, "prints")
                    if os.path.exists(prints_dst):
                        shutil.rmtree(prints_dst)
                    shutil.copytree(prints_src, prints_dst)

                    os.makedirs(os.path.join(output_dir, "profiles"), exist_ok=True)
                    os.makedirs(os.path.join(output_dir, "routes"), exist_ok=True)

                    # README
                    with open(os.path.join(output_dir, "README.txt"), "w", encoding="utf-8") as f:
                        f.write(f"Misteremio Bot - Licenca valida ate {date_display}\n\n")
                        f.write("INSTRUCOES:\n1. Execute Misteremio Bot.exe como Administrador\n")
                        f.write("2. Calibre as zonas na interface\n")
                        f.write("3. Configure combos e heals em CONFIG\n\n")
                        f.write("IMPORTANTE: Requer conexao com a internet para autenticacao.\n")

                    size = os.path.getsize(os.path.join(output_dir, "Misteremio Bot.exe")) / 1024 / 1024
                    self.after(0, self.log, f"\n✅ BUILD CONCLUIDO!", "#00ff88")
                    self.after(0, self.log, f"   Arquivo: {output_dir}\\Misteremio Bot.exe", "#00ff88")
                    self.after(0, self.log, f"   Tamanho: {size:.0f} MB", "#00ff88")
                    self.after(0, self.log, f"   Validade: ate {date_display}", "#00ff88")
                    self.after(0, lambda: messagebox.showinfo("Sucesso!", f"Misteremio Bot.exe compilado com sucesso!\n\nValido ate: {date_display}\nSalvo em: {output_dir}"))
                else:
                    self.after(0, self.log, "\n❌ ERRO: .exe nao foi gerado! Verifique o PyInstaller.", "#e74c3c")
                    self.after(0, lambda: messagebox.showerror("Erro", "O executável não foi gerado. Verifique o log."))
            finally:
                # SEMPRE restaura o main.py original
                with open(MAIN_PY, "w", encoding="utf-8") as f:
                    f.write(original)
                self.after(0, self.log, "> main.py restaurado ao original.", "#888")

        except Exception as e:
            self.after(0, self.log, f"\n❌ ERRO CRITICO: {e}", "#e74c3c")
        finally:
            self.after(0, lambda: self.btn_compile.configure(state="normal", text="⚡  COMPILAR EXECUTÁVEL"))


if __name__ == "__main__":
    app = PreCompilerApp()
    app.mainloop()
