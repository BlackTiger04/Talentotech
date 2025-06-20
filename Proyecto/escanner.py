# -*- coding: utf-8 -*-
"""escanner.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1o33-mHBCM-qeKF26KdeZQT_MN6bp0_cn
"""

# -*- coding: utf-8 -*-
import socket
import time
import random
from concurrent.futures import ThreadPoolExecutor
import argparse
from datetime import datetime
import sys
from colorama import Fore, Style, init
from fpdf import FPDF

# Inicializar colores para terminal
init(autoreset=True)

# Configuración global
VERSION = "2.1"
AUTHOR = "BlackTiger04"
MAX_THREADS = 50
DELAY_MIN = 0.05
DELAY_MAX = 0.5

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Reporte de Simulación de Escaneo', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln()

def mostrar_banner():
    """Banner de presentación mejorado con colores"""
    print(f"""
    {Fore.RED}****************************************************{Style.RESET_ALL}
    {Fore.RED}*{Fore.YELLOW}           HERRAMIENTA DE ESCANEO AVANZADO        {Fore.RED}*
    *                POR {Fore.CYAN}{AUTHOR}{Fore.YELLOW}{' '*(16-len(AUTHOR))}{Fore.RED}*
    *      Bootcamp de Ciberseguridad - Laboratorio    *
    *                Versión {Fore.GREEN}{VERSION}{Fore.YELLOW}{' '*(8-len(VERSION))}{Fore.RED}*
    ****************************************************{Style.RESET_ALL}
    """)

def parse_args():
    """Parseo de argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Herramienta de escaneo de puertos avanzado")
    parser.add_argument("target", help="IP del objetivo")
    parser.add_argument("-p", "--ports", help="Rango de puertos (ej: 20-100,80,443)", default="1-1024")
    parser.add_argument("-t", "--threads", type=int, help="Hilos de ejecución", default=MAX_THREADS)
    parser.add_argument("-v", "--verbose", help="Modo verboso", action="store_true")
    parser.add_argument("--no-evasion", help="Desactivar evasión de firewall", action="store_true")
    return parser.parse_args()

def generar_rango_puertos(rango_str):
    """Convierte un string de rango a lista de puertos"""
    puertos = []
    for parte in rango_str.split(','):
        if '-' in parte:
            inicio, fin = map(int, parte.split('-'))
            puertos.extend(range(inicio, fin+1))
        else:
            puertos.append(int(parte))
    return sorted(set(puertos))  # Eliminar duplicados

def detectar_servicio(banner, puerto):
    """Detección mejorada de servicios"""
    if not banner:
        # Detección por puerto conocido
        servicios = {
            21: "FTP",
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            3389: "RDP",
            445: "SMB",
            3306: "MySQL"
        }
        return servicios.get(puerto, "Unknown")

    banner_str = str(banner).lower()

    if b"ftp" in banner_str.lower():
        return "FTP"
    elif b"http" in banner_str:
        return "HTTP"
    elif b"microsoft-iis" in banner_str.lower():
        return "IIS"
    elif b"smb" in banner_str.lower() or b"\xffSMB" in banner:
        return "SMB"
    elif b"rdp" in banner_str.lower() or b"\x03\x00\x00" in banner:
        return "RDP"
    elif b"mysql" in banner_str.lower():
        return "MySQL"
    else:
        return "Unknown Service"

def escanear_puerto(ip, puerto, args, inicio_escaneo):
    """Escanea un puerto individual con técnicas avanzadas"""
    try:
        # Técnica de evasión
        if not args.no_evasion:
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)

            inicio = time.time()
            resultado = s.connect_ex((ip, puerto))

            if resultado == 0:  # Puerto abierto
                # Banner grabbing avanzado
                try:
                    banner = s.recv(1024) if puerto not in [21, 22] else b''
                except:
                    banner = b''

                tiempo_respuesta = time.time() - inicio
                servicio = detectar_servicio(banner, puerto)
                estado = "OPEN"

                if args.verbose:
                    tiempo_transcurrido = time.time() - inicio_escaneo
                    print(f"{Fore.GREEN}[+] {tiempo_transcurrido:6.2f}s Puerto {puerto:5d} | {estado:6} | {servicio:20} | {banner[:30]!r}{Style.RESET_ALL}")

                return (puerto, True, tiempo_respuesta, servicio, banner.decode(errors='ignore')[:100])
            else:
                return (puerto, False, 0, None, None)

    except (socket.timeout, ConnectionRefusedError):
        return (puerto, False, 0, None, None)
    except Exception as e:
        if args.verbose:
            print(f"{Fore.RED}[-] Error en puerto {puerto}: {str(e)}{Style.RESET_ALL}")
        return (puerto, False, 0, None, None)

def mostrar_resultados(resultados, tiempo_total):
    """Muestra los resultados del escaneo"""
    print("\n" + "="*80)
    print(f"{Fore.CYAN}RESULTADOS DEL ESCANEO".center(80))
    print("="*80 + Style.RESET_ALL)

    abiertos = [r for r in resultados if r[1]]
    criticos = [p for p, _, _, s, _ in abiertos if s in ["FTP", "HTTP", "HTTPS", "RDP", "SMB", "MySQL"]]

    print(f"\n{Fore.YELLOW}[+] Tiempo total: {tiempo_total:.2f} segundos{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Puertos escaneados: {len(resultados)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[+] Puertos abiertos: {len(abiertos)}{Style.RESET_ALL}")
    print(f"{Fore.RED}[!] Puertos críticos: {len(criticos)}{Style.RESET_ALL}")

    if abiertos:
        print(f"\n{Fore.GREEN}[PUERTOS ABIERTOS]{Style.RESET_ALL}")
        for puerto, _, tiempo, servicio, banner in sorted(abiertos, key=lambda x: x[0]):
            print(f"  {Fore.CYAN}{puerto:5d}{Style.RESET_ALL} | {servicio:20} | {tiempo:.3f}s | {banner[:50]!r}")

def generar_reporte(resultados, tiempo_total, target):
    """Genera un reporte PDF con los resultados"""
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Información general
    pdf.chapter_title('Información del Escaneo')
    pdf.chapter_body(f"""
    Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    Objetivo: {target}
    Tiempo total de escaneo: {tiempo_total:.2f} segundos
    Puertos escaneados: {len(resultados)}
    """)

    # Puertos abiertos
    abiertos = [r for r in resultados if r[1]]
    pdf.chapter_title('Puertos Abiertos Detectados')

    if abiertos:
        # Encabezado de tabla
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(20, 10, 'Puerto', 1, 0, 'C')
        pdf.cell(40, 10, 'Servicio', 1, 0, 'C')
        pdf.cell(20, 10, 'Tiempo', 1, 0, 'C')
        pdf.cell(110, 10, 'Banner', 1, 1, 'C')

        # Contenido de tabla
        pdf.set_font('Arial', '', 10)
        for puerto, _, tiempo, servicio, banner in sorted(abiertos, key=lambda x: x[0]):
            pdf.cell(20, 10, str(puerto), 1, 0, 'C')
            pdf.cell(40, 10, servicio, 1, 0, 'C')
            pdf.cell(20, 10, f"{tiempo:.3f}s", 1, 0, 'C')
            pdf.cell(110, 10, banner[:50] if banner else "N/A", 1, 1, 'L')
    else:
        pdf.chapter_body("No se encontraron puertos abiertos.")

    # Guardar PDF
    filename = f"reporte_escaneo_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    print(f"\n{Fore.GREEN}[+] Reporte generado: {filename}{Style.RESET_ALL}")

def main():
    """Función principal"""
    mostrar_banner()
    args = parse_args()

    try:
        puertos = generar_rango_puertos(args.ports)
        inicio_escaneo = time.time()

        print(f"{Fore.CYAN}[*] Iniciando escaneo contra {args.target}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Rango de puertos: {args.ports}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Hilos: {args.threads}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Evasión de firewall: {'ON' if not args.no_evasion else 'OFF'}{Style.RESET_ALL}")
        print(f"\n{Fore.BLUE}{'[ESCANEANDO]'.center(80, '-')}{Style.RESET_ALL}")

        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            resultados = list(executor.map(
                lambda p: escanear_puerto(args.target, p, args, inicio_escaneo),
                puertos
            ))

        tiempo_total = time.time() - inicio_escaneo
        mostrar_resultados(resultados, tiempo_total)
        generar_reporte(resultados, tiempo_total, args.target)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Escaneo interrumpido por el usuario{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error crítico: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()