import os
import sqlite3
from io import BytesIO
from PyPDF2 import PdfReader

COMPANY = os.environ.get('COMPANY') #"BEKKULISHA"
COMPANY_ID = os.environ.get('COMPANY_ID') #"041017601713"
MONTH_PASS_PRICE = "1499"
DAY_PASS_PRICE = "499"

def verify_pdf(pdf_bytes):
    # Open the PDF file
    pdf_stream = BytesIO(pdf_bytes)

    # Pass the stream to PdfReader
    reader = PdfReader(pdf_stream)
    
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split("\n")
        if len(lines) < 8:
            return {"approved": False,
                    "reason": "Wrong PDF", 
                    "days_added": 0, 
                    "company_name": "",
                    "vendor_id": "",
                    "payment": "", 
                    "transaction_id": "",
                    "customer_name": "",
                    "transaction_time": ""}

        company_name = lines[1]
        vendor_id = lines[5].split(" ")[2]
        payment = lines[3].split(" ")[0]
        customer_name = lines[6]
        transaction_time = lines[7]
        transaction_id = lines[4].split(" ")[2]
        
        # Check DB for repetition
        db = sqlite3.connect('records_and_tasks.db')
        cursor = db.cursor()
        cursor.execute("SELECT transaction_id FROM Records WHERE status = ?", ("Approved",))
        rows = cursor.fetchall()
        for row in rows:
            if transaction_id == row[0]:
                db.close()
                return {"approved": False,
                        "reason": "Repeated transaction ID", 
                        "days_added": 0, 
                        "company_name": company_name,
                        "vendor_id": vendor_id,
                        "payment": payment, 
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "transaction_time": transaction_time}
        db.close()

        # Check Company Credentials First
        if company_name == COMPANY and vendor_id == COMPANY_ID:
            if MONTH_PASS_PRICE in payment:
                return {"approved": True, 
                        "reason": "Verified", 
                        "days_added": 30, 
                        "company_name": company_name,
                        "vendor_id": vendor_id,
                        "payment": payment, 
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "transaction_time": transaction_time}
            elif DAY_PASS_PRICE in payment:
                return {"approved": True,
                        "reason": "Verified", 
                        "days_added": 1, 
                        "company_name": company_name,
                        "vendor_id": vendor_id,
                        "payment": payment, 
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "transaction_time": transaction_time}
            else:
                return {"approved": False,
                        "reason": "Wrong sum", 
                        "days_added": 0, 
                        "company_name": company_name,
                        "vendor_id": vendor_id,
                        "payment": payment, 
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "transaction_time": transaction_time}
        else:
            return {"approved": False,
                    "reason": "Wrong name", 
                    "days_added": 0, 
                    "company_name": company_name,
                    "vendor_id": vendor_id,
                    "payment": payment, 
                    "transaction_id": transaction_id,
                    "customer_name": customer_name,
                    "transaction_time": transaction_time}