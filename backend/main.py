from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.supabase_client import supabase
from fastapi.responses import StreamingResponse
from datetime import date
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/purchases")
def list_purchases():
    data = supabase.table("purchases").select("*").order("date", desc=True).execute()
    return data.data

@app.post("/purchases")
def create_purchase(item: dict):
    supabase.table("purchases").insert(item).execute()
    return {"message": "Compra adicionada com sucesso"}

@app.put("/purchases/{id}")
def update_purchase(id: int, item: dict):
    supabase.table("purchases").update(item).eq("id", id).execute()
    return {"message": "Compra atualizada"}

@app.delete("/purchases/{id}")
def delete_purchase(id: int):
    supabase.table("purchases").delete().eq("id", id).execute()
    return {"message": "Compra excluída"}

@app.get("/totals")
def totals():
    data = supabase.table("purchases").select("*").execute()
    df = pd.DataFrame(data.data)
    if df.empty:
        return {"by_buyer": {}, "total": 0}
    totals_by_buyer = df.groupby("buyer")["amount"].sum().to_dict()
    total_general = float(df["amount"].sum())
    return {"by_buyer": totals_by_buyer, "total": total_general}

@app.get("/export/pdf")
def export_pdf():
    data = supabase.table("purchases").select("*").execute()
    df = pd.DataFrame(data.data)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Relatório de Compras", styles["Heading1"])]
    table_data = [["Comprador", "Valor", "Data"]]
    for _, row in df.iterrows():
        table_data.append([row["buyer"], f"R$ {row['amount']:.2f}", str(row["date"])])
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=relatorio_compras.pdf"
    })

@app.get("/export/excel")
def export_excel():
    data = supabase.table("purchases").select("*").execute()
    df = pd.DataFrame(data.data)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Compras")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=relatorio_compras.xlsx"}
    )
