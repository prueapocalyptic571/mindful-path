"""Generates the Mindful Path app icon as a PNG."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QColor, QFont, QPixmap, QLinearGradient, QRadialGradient
from PyQt6.QtCore import Qt, QRectF

app = QApplication.instance() or QApplication(sys.argv)

for size in (16, 32, 48, 64, 128, 256):
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)

    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background circle with warm gradient
    grad = QRadialGradient(size * 0.45, size * 0.4, size * 0.55)
    grad.setColorAt(0.0, QColor("#e8920a"))
    grad.setColorAt(1.0, QColor("#a05808"))
    p.setBrush(grad)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(1, 1, size - 2, size - 2)

    # Subtle inner shadow ring
    from PyQt6.QtGui import QPen
    pen = QPen(QColor(0, 0, 0, 40))
    pen.setWidth(max(1, size // 32))
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(1, 1, size - 2, size - 2)

    # Dharma wheel ☸
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    font = QFont("Noto Sans", max(8, int(size * 0.58)))
    font.setBold(False)
    p.setFont(font)
    p.setPen(QColor(255, 255, 255, 230))
    p.drawText(QRectF(0, 0, size, size * 1.05), Qt.AlignmentFlag.AlignCenter, "☸")

    p.end()

    out_dir = os.path.expanduser("~/.local/share/icons/hicolor")
    icon_dir = os.path.join(out_dir, f"{size}x{size}", "apps")
    os.makedirs(icon_dir, exist_ok=True)
    path = os.path.join(icon_dir, "mindful-path.png")
    px.save(path, "PNG")
    print(f"  Saved {size}x{size} → {path}")

# Also save a copy in the project for the .desktop fallback
project_icon = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
px256 = QPixmap(256, 256)
px256.fill(Qt.GlobalColor.transparent)
p = QPainter(px256)
p.setRenderHint(QPainter.RenderHint.Antialiasing)
grad = QRadialGradient(115, 103, 140)
grad.setColorAt(0.0, QColor("#e8920a"))
grad.setColorAt(1.0, QColor("#a05808"))
p.setBrush(grad)
p.setPen(Qt.PenStyle.NoPen)
p.drawEllipse(2, 2, 252, 252)
font = QFont("Noto Sans", 148)
p.setFont(font)
p.setPen(QColor(255, 255, 255, 230))
p.drawText(QRectF(0, 0, 256, 270), Qt.AlignmentFlag.AlignCenter, "☸")
p.end()
px256.save(project_icon, "PNG")
print(f"  Saved project icon → {project_icon}")

print("Done.")
