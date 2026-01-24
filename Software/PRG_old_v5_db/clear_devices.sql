-- ============================================================================
-- Benning Device Manager - Datenbank Cleanup
-- ============================================================================
-- Löscht alle Seed Daten und setzt Auto-Increment zurück

USE benning_device_manager;

-- ANCHOR: Löschen Sie alle Daten aus den Tabellen
DELETE FROM audit_log;
DELETE FROM inspections;
DELETE FROM devices;

-- ANCHOR: Setze Auto-Increment zurück
ALTER TABLE devices AUTO_INCREMENT = 1;
ALTER TABLE inspections AUTO_INCREMENT = 1;
ALTER TABLE audit_log AUTO_INCREMENT = 1;

-- ANCHOR: Überprüfe
SELECT COUNT(*) as 'Devices' FROM devices;
SELECT COUNT(*) as 'Inspections' FROM inspections;

-- ============================================================================
-- Cleanup abgeschlossen!
-- ============================================================================
