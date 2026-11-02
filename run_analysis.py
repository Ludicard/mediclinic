#!/usr/bin/env python3
"""
Script de automatización para la ejecución de análisis estático de código.
Ejecuta Pylint, Flake8 y Bandit si están instalados, o un analizador AST demostrativo.
"""

import os
import sys
import shutil
import subprocess
import ast


def check_tool(tool_name: str) -> bool:
    """Verifica si una herramienta CLI está disponible en el PATH."""
    return shutil.which(tool_name) is not None


def run_command_and_save(cmd: list, output_file: str, description: str) -> None:
    """Ejecuta un comando de análisis y guarda el reporte en archivo de texto."""
    print(f"\n{'='*70}")
    print(f"Ejecutando: {description}")
    print(f"Comando: {' '.join(cmd)}")
    print(f"{'='*70}")

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False
        )
        output = proc.stdout
        print(output)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[✓] Reporte generado y guardado en: {output_file}")
    except Exception as e:
        print(f"[✗] Error al ejecutar {tool_name}: {e}")


def fallback_ast_scanner(project_dir: str):
    """
    Analizador estático básico basado en el módulo estándar ast de Python.
    Permite identificar hallazgos clave sin requerir dependencias externas.
    """
    print("\n" + "=" * 70)
    print("ANALIZADOR ESTÁTICO NATIVO (Basado en AST de Python Standard Library)")
    print("=" * 70)
    
    findings = []

    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                try:
                    tree = ast.parse(content, filename=path)
                except SyntaxError as e:
                    findings.append(f"[ERROR SINTAXIS] {rel_path}:{e.lineno} -> {e}")
                    continue

                for node in ast.walk(tree):
                    # 1. Hallazgo de Seguridad: Uso de MD5
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute) and node.func.attr == "md5":
                            findings.append(
                                f"[SEGURIDAD - Bandit B303] {rel_path}:{node.lineno} "
                                f"-> Uso de función hash criptográficamente insegura 'hashlib.md5()'."
                            )
                        if isinstance(node.func, ast.Attribute) and node.func.attr == "mktemp":
                            findings.append(
                                f"[SEGURIDAD - Bandit B306] {rel_path}:{node.lineno} "
                                f"-> Uso de tempfile.mktemp() propenso a Race Conditions. Usar NamedTemporaryFile."
                            )

                    # 2. Hallazgo de Seguridad: SQL Injection por formato de cadenas
                    if isinstance(node, ast.JoinedStr):
                        # Detectar f-strings que contengan cláusulas SQL
                        raw_str = content.splitlines()[node.lineno - 1] if node.lineno <= len(content.splitlines()) else ""
                        if "SELECT " in raw_str.upper() and "WHERE" in raw_str.upper():
                            findings.append(
                                f"[SEGURIDAD - Bandit B608] {rel_path}:{node.lineno} "
                                f"-> Posible inyección SQL construyendo query con interpolación de cadenas: {raw_str.strip()}"
                            )

                    # 3. Hallazgo de Estilo: Bare except
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        findings.append(
                            f"[ESTILO/CALIDAD - Pylint W0702] {rel_path}:{node.lineno} "
                            f"-> Cláusula 'except:' genérica que oculta posibles fallos críticos."
                        )

    print(f"\nTotal de hallazgos críticos detectados por AST nativo: {len(findings)}\n")
    for idx, item in enumerate(findings, 1):
        print(f"{idx}. {item}")

    print("\n" + "=" * 70)


def main():
    print("=" * 70)
    print("  VERIFICACIÓN DE HERRAMIENTAS DE ANÁLISIS ESTÁTICO DE CÓDIGO")
    print("=" * 70)

    pylint_ok = check_tool("pylint")
    flake8_ok = check_tool("flake8")
    bandit_ok = check_tool("bandit")

    tools_available = [t for t, ok in [("pylint", pylint_ok), ("flake8", flake8_ok), ("bandit", bandit_ok)] if ok]

    if not tools_available:
        print("[!] No se detectaron las herramientas 'pylint', 'flake8' o 'bandit' en el entorno global.")
        print("[*] Ejecutando análisis nativo de demostración...")
        fallback_ast_scanner("mediclinic")
        print("\nPara ejecutar las herramientas profesionales y generar los reportes formales:")
        print("  1. Cree o active un entorno virtual:")
        print("       python3 -m venv .venv")
        print("       source .venv/bin/activate")
        print("  2. Instale las herramientas:")
        print("       pip install -r requirements.txt")
        print("  3. Vuelva a ejecutar este script:")
        print("       python3 run_analysis.py")
        return

    # Si están disponibles, ejecutamos cada una
    if pylint_ok:
        run_command_and_save(
            ["pylint", "mediclinic"],
            "reporte_pylint.txt",
            "Pylint (Estilo, convenciones PEP8, código duplicado y errores)"
        )

    if flake8_ok:
        run_command_and_save(
            ["flake8", "mediclinic", "--statistics"],
            "reporte_flake8.txt",
            "Flake8 (Estilo PEP8 y complejidad)"
        )

    if bandit_ok:
        run_command_and_save(
            ["bandit", "-r", "mediclinic", "-f", "txt"],
            "reporte_bandit.txt",
            "Bandit (Vulnerabilidades de seguridad en Python)"
        )


if __name__ == "__main__":
    main()

