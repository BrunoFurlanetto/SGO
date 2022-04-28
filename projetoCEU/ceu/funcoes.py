from tkinter import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io


def criar_pdf_relatorio():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
    c.drawImage(
        r'C:\Users\bruno\OneDrive\Área de Trabalho\Projetos\SGO\projetoCEU\templates\static\img\logoAvalicao.png',
        x=20, y=20, width=100, height=250)
    c.showPage()
    c.save()
    buffer.seek(0)

    return buffer