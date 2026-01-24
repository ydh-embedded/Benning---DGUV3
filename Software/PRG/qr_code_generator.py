"""
QR-Code Generator für Benning Device Manager
Generiert QR-Codes mit Device ID
"""

import qrcode
import io
import base64
from typing import Optional


class QRCodeGenerator:
    """Generiert QR-Codes für Device IDs"""
    
    @staticmethod
    def generate_qr_code(device_id: str, size: int = 10, border: int = 2) -> str:
        """
        Generiere QR-Code für Device ID
        
        Args:
            device_id: Device ID (z.B. "Parloa-00001")
            size: QR-Code Größe (Pixel pro Box)
            border: Border Größe
        
        Returns:
            Base64 encoded PNG String
        """
        try:
            # Erstelle QR-Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
            qr.add_data(device_id)
            qr.make(fit=True)
            
            # Erstelle Image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Konvertiere zu Base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            base64_string = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{base64_string}"
        
        except Exception as e:
            print(f"❌ Fehler beim QR-Code generieren: {e}")
            return None
    
    @staticmethod
    def generate_qr_code_svg(device_id: str) -> str:
        """
        Generiere QR-Code als SVG
        
        Args:
            device_id: Device ID
        
        Returns:
            SVG String
        """
        try:
            import qrcode.image.svg
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                image_factory=qrcode.image.svg.SvgPathImage,
            )
            qr.add_data(device_id)
            qr.make(fit=True)
            
            img = qr.make_image()
            
            buffer = io.BytesIO()
            img.save(buffer)
            buffer.seek(0)
            
            return buffer.getvalue().decode()
        
        except Exception as e:
            print(f"❌ Fehler beim SVG generieren: {e}")
            return None
    
    @staticmethod
    def generate_qr_code_html(device_id: str) -> str:
        """
        Generiere HTML mit QR-Code und Label
        
        Args:
            device_id: Device ID
        
        Returns:
            HTML String
        """
        qr_base64 = QRCodeGenerator.generate_qr_code(device_id)
        
        if not qr_base64:
            return "<p>QR-Code konnte nicht generiert werden</p>"
        
        html = f"""
        <div class="qr-code-container">
            <img src="{qr_base64}" alt="QR-Code für {device_id}" class="qr-code-image">
            <div class="qr-code-label">{device_id}</div>
        </div>
        """
        return html


# Beispiel Verwendung
if __name__ == '__main__':
    generator = QRCodeGenerator()
    
    # Generiere QR-Code
    device_id = "Parloa-00001"
    qr_code = generator.generate_qr_code(device_id)
    
    print(f"✅ QR-Code für {device_id} generiert")
    print(f"Base64 Länge: {len(qr_code)} Zeichen")
