"""
Build Script para gerar 12 executaveis do Misteremio Bot com expiracao mensal.
Um .exe por mes de 2026, cada um expirando no ultimo dia do mes.
"""
import os
import shutil
import subprocess
import calendar

# Ultimos dias de cada mes de 2026 (2026 NAO eh bissexto)
MONTHS = [
    (1,  "Janeiro",   31),
    (2,  "Fevereiro", 28),
    (3,  "Marco",     31),
    (4,  "Abril",     30),
    (5,  "Maio",      31),
    (6,  "Junho",     30),
    (7,  "Julho",     31),
    (8,  "Agosto",    31),
    (9,  "Setembro",  30),
    (10, "Outubro",   31),
    (11, "Novembro",  30),
    (12, "Dezembro",  31),
]

MAIN_PY = "main.py"
OUTPUT_BASE = r"d:\Antigravity_Projects\Misteremio Bot_Monthly"

def read_main():
    with open(MAIN_PY, "r", encoding="utf-8") as f:
        return f.read()

def write_main(content):
    with open(MAIN_PY, "w", encoding="utf-8") as f:
        f.write(content)

def set_expiry(original_content, month, last_day, month_name):
    """Substitui as duas linhas criticas: expiry_date e a mensagem de erro."""
    
    # Calcula o dia seguinte ao ultimo dia valido (inicio do bloqueio)
    if month == 12:
        next_year, next_month, next_day = 2027, 1, 1
    else:
        next_year, next_month, next_day = 2026, month + 1, 1
    
    date_display = f"{last_day:02d}/{month:02d}/2026"
    
    new_content = original_content
    
    # Substitui linha de expiracao
    old_expiry = 'expiry_date = datetime(2026, 3, 5) # Expira no começo do dia 5 (válido até dia 4 inteiro)'
    new_expiry = f'expiry_date = datetime({next_year}, {next_month}, {next_day}) # Valido ate {date_display}'
    new_content = new_content.replace(old_expiry, new_expiry)
    
    # Na segunda iteracao e seguintes, o padrao antigo ja mudou. Vamos usar marcador fixo
    # Procura por qualquer linha com expiry_date = datetime( e substitui
    lines = new_content.split("\n")
    final_lines = []
    for line in lines:
        if "expiry_date = datetime(" in line:
            indent = len(line) - len(line.lstrip())
            final_lines.append(" " * indent + f"expiry_date = datetime({next_year}, {next_month}, {next_day})  # Valido ate {date_display}")
        elif "era válida até" in line or "era valida ate" in line:
            indent = len(line) - len(line.lstrip())
            final_lines.append(" " * indent + f'tkinter.messagebox.showerror("Licença Expirada", "A licença do Misteremio Bot era válida até {date_display} e acabou de expirar.\\nEntre em contato com o desenvolvedor.")')
        else:
            final_lines.append(line)
    
    return "\n".join(final_lines)

def build_exe(month_num, month_name, last_day):
    print(f"\n{'='*60}")
    print(f"  Compilando: Misteremio Bot - {month_name.upper()} 2026 (valido ate {last_day:02d}/{month_num:02d}/2026)")
    print(f"{'='*60}")
    
    original = read_main()
    modified = set_expiry(original, month_num, last_day, month_name)
    write_main(modified)
    
    try:
        result = subprocess.run(
            ["pyinstaller", "Misteremio Bot.spec", "--noconfirm"],
            capture_output=False,
            text=True
        )
        
        exe_source = r"dist\Misteremio Bot.exe"
        if os.path.exists(exe_source):
            folder_name = f"{month_num:02d}_{month_name}_2026"
            dest_folder = os.path.join(OUTPUT_BASE, folder_name)
            os.makedirs(dest_folder, exist_ok=True)
            
            shutil.copy(exe_source, os.path.join(dest_folder, "Misteremio Bot.exe"))
            
            # Copia assets necessarios
            prints_dst = os.path.join(dest_folder, "prints")
            if os.path.exists(prints_dst):
                shutil.rmtree(prints_dst)
            shutil.copytree("prints", prints_dst)
            
            os.makedirs(os.path.join(dest_folder, "profiles"), exist_ok=True)
            os.makedirs(os.path.join(dest_folder, "routes"), exist_ok=True)
            
            with open(os.path.join(dest_folder, "README.txt"), "w", encoding="utf-8") as f:
                f.write(f"Misteremio Bot - Licenca {month_name} 2026\n")
                f.write(f"Valida ate: {last_day:02d}/{month_num:02d}/2026\n\n")
                f.write("INSTRUCOES:\n")
                f.write("1. Execute Misteremio Bot.exe como Administrador\n")
                f.write("2. Calibre as zonas na interface\n")
                f.write("3. Configure seus combos e heals em CONFIG\n\n")
                f.write("IMPORTANTE: O bot requer conexao com a internet para autenticacao.\n")
            
            size_mb = os.path.getsize(os.path.join(dest_folder, "Misteremio Bot.exe")) / 1024 / 1024
            print(f"  OK: {folder_name} ({size_mb:.0f} MB)")
            return True
        else:
            print(f"  ERRO: exe nao encontrado apos build!")
            return False
    finally:
        write_main(original)

if __name__ == "__main__":
    print("\nMisteremio Bot - Build Script Mensal 2026")
    print(f"Output: {OUTPUT_BASE}\n")
    
    success = []
    failed = []
    
    for month_num, month_name, last_day in MONTHS:
        ok = build_exe(month_num, month_name, last_day)
        if ok:
            success.append(f"{month_name} (ate {last_day:02d}/{month_num:02d})")
        else:
            failed.append(month_name)
    
    print("\n" + "="*60)
    print("RESULTADO FINAL:")
    print(f"  Sucesso: {len(success)}/{len(MONTHS)}")
    for s in success:
        print(f"    + {s}")
    if failed:
        print(f"  Falhas: {failed}")
    
    if success:
        print("\nCompactando pasta completa de distribuicao...")
        zip_path = r"d:\Antigravity_Projects\Misteremio Bot_Monthly_AllVersions"
        shutil.make_archive(zip_path, "zip", OUTPUT_BASE)
        size = os.path.getsize(zip_path + ".zip") / 1024 / 1024 / 1024
        print(f"ZIP gerado: {zip_path}.zip ({size:.1f} GB)")
    
    print("\nBuild concluido!")
