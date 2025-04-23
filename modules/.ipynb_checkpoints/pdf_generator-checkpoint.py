import os
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(devis_df):
    # Taille de la page A4
    PAGE_WIDTH, PAGE_HEIGHT = A4

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=5*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # 🎨 Couleurs et images
    primary_color = colors.HexColor("#1F4E79")  # Bleu foncé
    accent_color = colors.HexColor("#E57C9D")  # Rose doux
    
    # 🖼️ Chemins des images
    top_image_path = os.path.join("images", "top_right.png")
    bottom_image_path = os.path.join("images", "bottom_left.png")

    # 📌 Fonction pour ajouter les images aux coins
    def draw_header_footer(canvas, doc):
        # Ajout de l'image en haut à droite
        top_img = Image(top_image_path, width=6 * cm, height=6 * cm)
        top_img.drawOn(canvas, PAGE_WIDTH - (6 * cm), PAGE_HEIGHT - (6 * cm))  # Positionné sans marge

        # Ajout de l'image en bas à gauche
        bottom_img = Image(bottom_image_path, width=6 * cm, height=6 * cm)
        bottom_img.drawOn(canvas, 0, 0)  # Positionné sans marge

    # 📆 Informations du devis
    date_issued = f"Date : {datetime.date.today().strftime('%d %B %Y')}"
    invoice_no = f"Numéro de devis : 01234"
    issued_to = "<b>Destinataire :</b> Sacha Dubois<br/>123 Anywhere St., Any City, ST 12345"

    # 📌 Création de l'en-tête
    header_table = Table([
        [[Paragraph(date_issued, styles["Normal"]), Paragraph(invoice_no, styles["Normal"])], 
         Paragraph(issued_to, styles["Normal"])]
    ], colWidths=[8*cm, 8*cm])

    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    # 🏷️ Ajout des éléments au PDF
    elements.append(Paragraph("<b>DEVIS</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(header_table)
    elements.append(Spacer(1, 12))

    # 🏷️ Tableau du devis
    table_data = [["Destination", "Poids Total (kg)", "Nombre de colis", "Prix par palette (€)", "Nombre palettes", "Total (€)"]]

    total_general = 0  # Initialisation du total
    for _, row in devis_df.iterrows():
        total_ligne = float(str(row["Total (€)"]).replace(' €', '').replace(',', '.'))
        total_general += total_ligne  # Ajout au total global

        table_data.append([
            row["Destination"], row["Poids total (kg)"], row["Quantité"],
            row["Tarif unitaire (€)"], row["Palettes"], f"{total_ligne:.2f} €"
        ])

    # 🏷️ Ajout de la ligne du total général
    table_data.append(["", "", "", "", "TOTAL", f"{total_general:.2f} €"])

    devis_table = Table(table_data, colWidths=[4 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm])

    # 🎨 Style du tableau
    devis_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Police en gras pour les en-têtes
        ('FONTSIZE', (0, 0), (-1, 0), 8),  
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),  # En-tête en bleu foncé
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, -1), (-1, -1), accent_color),  # Ligne du total en rose
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(devis_table)

    # ✍ Signature et Note
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("<b>Note :</b><br/>Bank Name: Rimberio<br/>Account No: 0123 4567 8901", styles["Normal"]))
    elements.append(Spacer(1, 24))

    # 📌 Zone Signature
    signature_table = Table([
        [Paragraph("<b>Claudia</b>", styles["Normal"]), ""],
        [Paragraph("<i>Finance Manager</i>", styles["Normal"]), "Signature"]
    ], colWidths=[8*cm, 8*cm])

    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (1, 1), (1, 1), 10),
        ('LINEABOVE', (1, 1), (1, 1), 1, colors.black)
    ]))

    elements.append(signature_table)

    # 📄 Génération du PDF avec images en arrière-plan
    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    
    buffer.seek(0)
    return buffer
