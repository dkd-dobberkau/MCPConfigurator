#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests für den MCP Konfigurationsmanager
"""

import os
import json
import shutil
import unittest
import tempfile
from pathlib import Path
from mcp_config_manager import MCPConfigManager


class TestMCPConfigManager(unittest.TestCase):
    def setUp(self):
        """Erstellt eine temporäre Testumgebung für die Tests"""
        # Erstelle ein temporäres Verzeichnis für die Tests
        self.test_dir = tempfile.mkdtemp()
        self.manager = MCPConfigManager(self.test_dir)
        
        # Testdaten für die Konfigurationsdateien vorbereiten
        self.test_config1 = {
            "mcpServers": {
                "server1": {
                    "command": "test-command1",
                    "args": ["arg1", "arg2"],
                    "env": {"TEST_VAR": "test-value1"}
                }
            }
        }
        
        self.test_config2 = {
            "mcpServers": {
                "server2": {
                    "command": "test-command2",
                    "args": ["arg3", "arg4"],
                    "env": {"TEST_VAR": "test-value2"}
                }
            }
        }
        
        # Testdateien erstellen
        self.config1_path = os.path.join(self.test_dir, "config1.json")
        self.config2_path = os.path.join(self.test_dir, "config2.json")
        
        with open(self.config1_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_config1, f)
        
        with open(self.config2_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_config2, f)
    
    def tearDown(self):
        """Bereinigt die Testumgebung nach den Tests"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Testet, ob die Verzeichnisstruktur korrekt initialisiert wird"""
        self.assertTrue(os.path.exists(self.manager.base_dir))
        self.assertTrue(os.path.exists(self.manager.available_dir))
        self.assertTrue(os.path.exists(self.manager.active_dir))
        self.assertTrue(os.path.exists(self.manager.backups_dir))
    
    def test_add_config(self):
        """Testet das Hinzufügen einer Konfiguration"""
        # Konfiguration hinzufügen
        result = self.manager.add_config(self.config1_path)
        self.assertTrue(result)
        
        # Überprüfen, ob die Datei im available Verzeichnis existiert
        expected_path = os.path.join(self.manager.available_dir, os.path.basename(self.config1_path))
        self.assertTrue(os.path.exists(expected_path))
        
        # Überprüfen, ob der Inhalt korrekt ist
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        self.assertEqual(content, self.test_config1)
    
    def test_add_invalid_config(self):
        """Testet das Hinzufügen einer ungültigen Konfiguration"""
        invalid_path = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_path, 'w', encoding='utf-8') as f:
            f.write("This is not valid JSON")
        
        result = self.manager.add_config(invalid_path)
        self.assertFalse(result)
    
    def test_enable_config(self):
        """Testet das Aktivieren einer Konfiguration"""
        # Konfiguration zuerst hinzufügen
        self.manager.add_config(self.config1_path)
        
        # Konfiguration aktivieren
        result = self.manager.enable_config(os.path.basename(self.config1_path))
        self.assertTrue(result)
        
        # Überprüfen, ob die Datei im active Verzeichnis existiert
        expected_path = os.path.join(self.manager.active_dir, os.path.basename(self.config1_path))
        self.assertTrue(os.path.exists(expected_path))
    
    def test_disable_config(self):
        """Testet das Deaktivieren einer Konfiguration"""
        # Konfiguration zuerst hinzufügen und aktivieren
        self.manager.add_config(self.config1_path)
        self.manager.enable_config(os.path.basename(self.config1_path))
        
        # Konfiguration deaktivieren
        result = self.manager.disable_config(os.path.basename(self.config1_path))
        self.assertTrue(result)
        
        # Überprüfen, ob die Datei nicht mehr im active Verzeichnis existiert
        expected_path = os.path.join(self.manager.active_dir, os.path.basename(self.config1_path))
        self.assertFalse(os.path.exists(expected_path))
    
    def test_combine_configs_empty(self):
        """Testet das Kombinieren ohne aktive Konfigurationen"""
        result = self.manager.combine_configs()
        self.assertTrue(result)
        
        # Überprüfen, ob die kombinierte Datei die erwartete leere Struktur hat
        with open(self.manager.combined_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        self.assertEqual(content, {"mcpServers": {}})
    
    def test_combine_configs_single(self):
        """Testet das Kombinieren mit einer aktiven Konfiguration"""
        # Konfiguration hinzufügen und aktivieren
        self.manager.add_config(self.config1_path)
        self.manager.enable_config(os.path.basename(self.config1_path))
        
        # Konfigurationen kombinieren
        result = self.manager.combine_configs()
        self.assertTrue(result)
        
        # Überprüfen, ob die kombinierte Datei den erwarteten Inhalt hat
        with open(self.manager.combined_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        self.assertEqual(content, self.test_config1)
    
    def test_combine_configs_multiple(self):
        """Testet das Kombinieren mit mehreren aktiven Konfigurationen"""
        # Konfigurationen hinzufügen und aktivieren
        self.manager.add_config(self.config1_path)
        self.manager.add_config(self.config2_path)
        self.manager.enable_config(os.path.basename(self.config1_path))
        self.manager.enable_config(os.path.basename(self.config2_path))
        
        # Konfigurationen kombinieren
        result = self.manager.combine_configs()
        self.assertTrue(result)
        
        # Überprüfen, ob die kombinierte Datei den erwarteten Inhalt hat
        with open(self.manager.combined_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Erwartetes Ergebnis: Beide Server sollten in mcpServers erscheinen
        expected = {
            "mcpServers": {
                "server1": self.test_config1["mcpServers"]["server1"],
                "server2": self.test_config2["mcpServers"]["server2"]
            }
        }
        self.assertEqual(content, expected)
    
    def test_deep_merge(self):
        """Testet die deep_merge Funktion"""
        dict1 = {
            "a": {
                "b": 1,
                "c": 2
            },
            "d": [1, 2]
        }
        
        dict2 = {
            "a": {
                "b": 3,  # Überschreibt dict1["a"]["b"]
                "e": 4   # Neuer Schlüssel in dict1["a"]
            },
            "d": [3, 4], # Wird mit dict1["d"] kombiniert
            "f": 5       # Neuer Schlüssel in dict1
        }
        
        result = self.manager.deep_merge(dict2, dict1)
        
        expected = {
            "a": {
                "b": 3,  # Von dict2 überschrieben
                "c": 2,  # Von dict1 beibehalten
                "e": 4   # Von dict2 hinzugefügt
            },
            "d": [1, 2, 3, 4],  # Kombiniert
            "f": 5       # Von dict2 hinzugefügt
        }
        
        self.assertEqual(result, expected)
    
    def test_create_backup(self):
        """Testet das Erstellen eines Backups"""
        # Zuerst eine kombinierte Konfiguration erstellen
        self.manager.add_config(self.config1_path)
        self.manager.enable_config(os.path.basename(self.config1_path))
        self.manager.combine_configs()
        
        # Backup erstellen
        backup_path = self.manager.create_backup()
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        
        # Überprüfen, ob das Backup den korrekten Inhalt hat
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        with open(self.manager.combined_file, 'r', encoding='utf-8') as f:
            original = json.load(f)
        self.assertEqual(content, original)


if __name__ == "__main__":
    unittest.main()