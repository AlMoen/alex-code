import os
import sys
import json
import psutil
from datetime import datetime

# DevOps-innstillinger: Sett grensene for når alarmen skal gå (i prosent)
CPU_TERSKEL = 80.0
RAM_TERSKEL = 70.0
DISK_TERSKEL = 90.0


def hent_system_metrikker():
    """Henter ekte helsedata fra maskinvaren."""
    try:
        # Hent CPU-bruk over et lite sekund
        cpu_bruk = psutil.cpu_percent(interval=0.5)

        # Hent RAM/Minne-status
        ram = psutil.virtual_memory()
        ram_bruk = ram.percent

        # Hent Disk/Lagring-status for hoveddisken
        disk = psutil.disk_usage('/')
        disk_bruk = disk.percent

        return {
            "cpu": cpu_bruk,
            "ram": ram_bruk,
            "disk": disk_bruk,
            "detaljer": {
                "ram_total_gb": round(ram.total / (1024**3), 2),
                "ram_ledig_gb": round(ram.available / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_ledig_gb": round(disk.free / (1024**3), 2)
            }
        }
    except Exception as e:
        print(f"🚨 Kunne ikke hente maskinvaredata: {e}")
        sys.exit(1)


def analyser_og_logg():
    print("🛰️ Cloud Sentinel skanner skyinfrastruktur (MacBook Air)...")

    # 1. Hent de ferske tallene
    metrikker = hent_system_metrikker()

    # 2. Sjekk om noen av verdiene bryter grensene våre
    alarm_tilstand = False
    utlosere = []

    if metrikker["cpu"] > CPU_TERSKEL:
        alarm_tilstand = True
        utlosere.append(
            f"CPU over terskel ({metrikker['cpu']}% > {CPU_TERSKEL}%)")

    if metrikker["ram"] > RAM_TERSKEL:
        alarm_tilstand = True
        utlosere.append(
            f"RAM over terskel ({metrikker['ram']}% > {RAM_TERSKEL}%)")

    if metrikker["disk"] > DISK_TERSKEL:
        alarm_tilstand = True
        utlosere.append(
            f"DISK over terskel ({metrikker['disk']}% > {DISK_TERSKEL}%)")

    # 3. Strukturere den profesjonelle logg-rapporten
    helse_rapport = {
        "overvaaking_id": f"SENTINEL-{int(datetime.now().timestamp())}",
        "tidsstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "ALARM" if alarm_tilstand else "HEALTHY",
        "system_data": metrikker,
        "alarmer": utlosere
    }

    # 4. Lagre rapporten i en strukturert loggmappe
    logg_mappe = "system_logger"
    if not os.path.exists(logg_mappe):
        os.makedirs(logg_mappe)

    filnavn = f"{logg_mappe}/status_rapport.json"
    with open(filnavn, "w", encoding="utf-8") as f:
        json.dump(helse_rapport, f, indent=4, ensure_ascii=False)

    # 5. Output til terminalen (Slik ekte verktøy som Datadog eller Splunk gjør det)
    print("\n=== SKANNING FULLFØRT ===")
    if alarm_tilstand:
        print(f"🔴 STATUS: ALARM REKVIRERT!")
        for alarm in utlosere:
            print(f"   ⚠️ {alarm}")
    else:
        print("🟢 STATUS: SYSTEM HEALTHY (Alle verdier innenfor normalen)")

    print(
        f"📊 CPU: {metrikker['cpu']}% | RAM: {metrikker['ram']}% | DISK: {metrikker['disk']}%")
    print(f"💾 Logg lagret i: {filnavn}\n")


if __name__ == "__main__":
    analyser_og_logg()
