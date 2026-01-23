"""
Unit Tests für Device Domain Model
"""
import unittest
from datetime import date, datetime, timedelta
from src.core.domain.device import Device, DeviceId


class TestDeviceId(unittest.TestCase):
    """Tests für DeviceId Value Object"""
    
    def test_valid_device_id(self):
        """Test: Gültige Device ID"""
        device_id = DeviceId("BENNING-001")
        self.assertEqual(str(device_id), "BENNING-001")
    
    def test_invalid_device_id(self):
        """Test: Ungültige Device ID"""
        with self.assertRaises(ValueError):
            DeviceId("INVALID-001")


class TestDevice(unittest.TestCase):
    """Tests für Device Entity"""
    
    def setUp(self):
        """Richte Test-Fixtures auf"""
        self.device = Device(
            id=DeviceId("BENNING-001"),
            name="Test Device",
            type="Power Supply",
            location="Lab 1",
            manufacturer="Benning",
            serial_number="SN123456",
            purchase_date=date(2023, 1, 1),
            last_inspection=date(2024, 1, 1),
            next_inspection=date(2025, 1, 1),
            status='active',
            notes="Test device",
            created_at=datetime.now()
        )
    
    def test_is_active(self):
        """Test: Gerät ist aktiv"""
        self.assertTrue(self.device.is_active())
    
    def test_is_due_for_inspection(self):
        """Test: Inspektion ist fällig"""
        self.device.next_inspection = date.today() - timedelta(days=1)
        self.assertTrue(self.device.is_due_for_inspection())
    
    def test_schedule_next_inspection(self):
        """Test: Nächste Inspektion planen"""
        next_date = self.device.schedule_next_inspection(365)
        expected = date.today() + timedelta(days=365)
        self.assertEqual(next_date, expected)


if __name__ == '__main__':
    unittest.main()
