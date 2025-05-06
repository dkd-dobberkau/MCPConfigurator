#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Konfigurationsmanager

Dieses Script hilft bei der Verwaltung von MCP-Konfigurationsdateien, indem es:
- Einzelne JSON-Konfigurationsdateien in eine zentrale JSON-Datei kombiniert
- Das Aktivieren und Deaktivieren von Konfigurationen ermöglicht
- Konfigurationen in einem Ordnerstruktur verwaltet
"""

import os
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path

class MCPConfigManager:
    def __init__(self, base_dir=None):
        """
        Initialisierung des MCP-Konfigurationsmanagers.
        
        Args:
            base_dir (str, optional): Das Basisverzeichnis für die Konfigurationsverwaltung.
                                     Standardmäßig wird ein 'mcp_configs' Ordner im aktuellen Verzeichnis verwendet.
        """
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), "mcp_configs")
        
        self.base_dir = Path(base_dir)
        self.available_dir = self.base_dir / "available"
        self.active_dir = self.base_dir / "active"
        self.backups_dir = self.base_dir / "backups"
        self.combined_file = self.base_dir / "claude_desktop_config.json"
        
        # Verzeichnisstruktur erstellen, falls nicht vorhanden
        for directory in [self.base_dir, self.available_dir, self.active_dir, self.backups_dir]:
            directory.mkdir(exist_ok=True, parents=True)
    
    def is_valid_json(self, file_path):
        """
        Überprüft, ob eine Datei gültiges JSON enthält.
        
        Args:
            file_path (Path): Pfad zur JSON-Datei
            
        Returns:
            bool: True, wenn die Datei gültiges JSON enthält, sonst False
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        except Exception as e:
            print(f"Fehler beim Überprüfen von {file_path}: {str(e)}")
            return False
    
    def add_config(self, file_path):
        """
        Fügt eine neue Konfigurationsdatei zum verfügbaren Verzeichnis hinzu.
        
        Args:
            file_path (str): Pfad zur JSON-Konfigurationsdatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        source_path = Path(file_path)
        
        if not source_path.exists():
            print(f"Fehler: Die Datei {file_path} existiert nicht.")
            return False
            
        if not self.is_valid_json(source_path):
            print(f"Fehler: Die Datei {file_path} enthält kein gültiges JSON.")
            return False
        
        dest_path = self.available_dir / source_path.name
        
        try:
            shutil.copy2(source_path, dest_path)
            print(f"Konfiguration {source_path.name} wurde zu verfügbaren Konfigurationen hinzugefügt.")
            return True
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Konfiguration: {str(e)}")
            return False
    
    def enable_config(self, config_name):
        """
        Aktiviert eine Konfiguration, indem sie aus 'available' nach 'active' kopiert wird.
        
        Args:
            config_name (str): Name der Konfigurationsdatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        source_path = self.available_dir / config_name
        
        if not source_path.exists():
            print(f"Fehler: Die Konfiguration {config_name} existiert nicht im verfügbaren Verzeichnis.")
            return False
        
        dest_path = self.active_dir / config_name
        
        try:
            shutil.copy2(source_path, dest_path)
            print(f"Konfiguration {config_name} wurde aktiviert.")
            return True
        except Exception as e:
            print(f"Fehler beim Aktivieren der Konfiguration: {str(e)}")
            return False
    
    def disable_config(self, config_name):
        """
        Deaktiviert eine Konfiguration, indem sie aus dem 'active' Verzeichnis entfernt wird.
        
        Args:
            config_name (str): Name der Konfigurationsdatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        config_path = self.active_dir / config_name
        
        if not config_path.exists():
            print(f"Fehler: Die Konfiguration {config_name} ist nicht aktiviert.")
            return False
        
        try:
            os.remove(config_path)
            print(f"Konfiguration {config_name} wurde deaktiviert.")
            return True
        except Exception as e:
            print(f"Fehler beim Deaktivieren der Konfiguration: {str(e)}")
            return False
    
    def list_configs(self):
        """
        Listet alle verfügbaren und aktiven Konfigurationen auf.
        """
        print("\nVerfügbare Konfigurationen:")
        for file in sorted(self.available_dir.glob("*.json")):
            print(f"  - {file.name}")
        
        print("\nAktive Konfigurationen:")
        for file in sorted(self.active_dir.glob("*.json")):
            print(f"  - {file.name}")
    
    def create_backup(self):
        """
        Erstellt ein Backup der aktuellen kombinierten Konfiguration.
        
        Returns:
            Path: Pfad zur Backup-Datei
        """
        if not self.combined_file.exists():
            print(f"Warnung: Keine kombinierte Konfiguration vorhanden ({self.combined_file}), die gesichert werden könnte.")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backups_dir / f"config_backup_{timestamp}.json"
        
        try:
            shutil.copy2(self.combined_file, backup_file)
            print(f"Backup erstellt: {backup_file.name}")
            return backup_file
        except Exception as e:
            print(f"Fehler beim Erstellen des Backups: {str(e)}")
            return None
    
    def deep_merge(self, source, destination):
        """
        Führt einen tiefen Merge von zwei Dictionaries durch.
        
        Args:
            source (dict): Quell-Dictionary
            destination (dict): Ziel-Dictionary, in das die Werte eingefügt werden
            
        Returns:
            dict: Das zusammengeführte Dictionary
        """
        for key, value in source.items():
            if key in destination:
                if isinstance(value, dict) and isinstance(destination[key], dict):
                    # Rekursiv für verschachtelte Dictionaries
                    destination[key] = self.deep_merge(value, destination[key])
                elif isinstance(value, list) and isinstance(destination[key], list):
                    # Bei Listen fügen wir einfach zusammen
                    destination[key] = destination[key] + value
                else:
                    # Bei einfachen Werten übernehmen wir den neueren Wert
                    destination[key] = value
            else:
                # Wenn der Schlüssel nicht existiert, fügen wir ihn hinzu
                destination[key] = value
        return destination
    
    def combine_configs(self):
        """
        Kombiniert alle aktiven Konfigurationen in eine einzige JSON-Datei.
        Verwendet deep_merge, um verschachtelte Strukturen korrekt zusammenzuführen.
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        if self.combined_file.exists():
            self.create_backup()
        
        active_configs = list(self.active_dir.glob("*.json"))
        
        # Standardstruktur für die kombinierte Datei
        combined_data = {"mcpServers": {}}
        
        if not active_configs:
            print("Hinweis: Keine aktiven Konfigurationen gefunden. Erstelle leere Konfiguration.")
        else:
            for config_file in active_configs:
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        
                    # Tiefer Merge für verschachtelte Dictionaries
                    combined_data = self.deep_merge(config_data, combined_data)
                except Exception as e:
                    print(f"Fehler beim Verarbeiten von {config_file.name}: {str(e)}")
                    return False
        
        try:
            with open(self.combined_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            print(f"Konfigurationen wurden erfolgreich in {self.combined_file} kombiniert.")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der kombinierten Konfiguration: {str(e)}")
            return False
    
    def show_combined_config(self):
        """
        Zeigt die kombinierte Konfiguration an.
        """
        if not self.combined_file.exists():
            print(f"Fehler: Keine kombinierte Konfiguration vorhanden ({self.combined_file}).")
            return
        
        try:
            with open(self.combined_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            print("\nInhalt der kombinierten Konfiguration:")
            print(json.dumps(config_data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Fehler beim Anzeigen der kombinierten Konfiguration: {str(e)}")


def main():
    """
    Hauptfunktion für die Kommandozeilenschnittstelle.
    """
    parser = argparse.ArgumentParser(description='MCP-Konfigurationsmanager')
    parser.add_argument('--dir', '-d', help='Basisverzeichnis für Konfigurationen')
    
    subparsers = parser.add_subparsers(dest='command', help='Befehle')
    
    # Befehl: add
    add_parser = subparsers.add_parser('add', help='Konfiguration hinzufügen')
    add_parser.add_argument('file', help='Pfad zur JSON-Konfigurationsdatei')
    
    # Befehl: enable
    enable_parser = subparsers.add_parser('enable', help='Konfiguration aktivieren')
    enable_parser.add_argument('config', help='Name der Konfigurationsdatei')
    
    # Befehl: disable
    disable_parser = subparsers.add_parser('disable', help='Konfiguration deaktivieren')
    disable_parser.add_argument('config', help='Name der Konfigurationsdatei')
    
    # Befehl: list
    subparsers.add_parser('list', help='Konfigurationen auflisten')
    
    # Befehl: combine
    subparsers.add_parser('combine', help='Aktive Konfigurationen kombinieren')
    
    # Befehl: show
    subparsers.add_parser('show', help='Kombinierte Konfiguration anzeigen')
    
    # Befehl: backup
    subparsers.add_parser('backup', help='Backup der kombinierten Konfiguration erstellen')
    
    args = parser.parse_args()
    
    manager = MCPConfigManager(args.dir)
    
    if args.command == 'add':
        manager.add_config(args.file)
    elif args.command == 'enable':
        manager.enable_config(args.config)
    elif args.command == 'disable':
        manager.disable_config(args.config)
    elif args.command == 'list':
        manager.list_configs()
    elif args.command == 'combine':
        manager.combine_configs()
    elif args.command == 'show':
        manager.show_combined_config()
    elif args.command == 'backup':
        manager.create_backup()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
