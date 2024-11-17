import os
import sqlite3
from io import BytesIO
from PyPDF2 import PdfReader

COMPANY = os.environ.get('COMPANY')
COMPANY_ID = os.environ.get('COMPANY_ID')
MONTH_PASS_PRICE = ["1 490", "1 491", "1 492", "1 493", "1 494", "1 495", "1 496", "1 497", "1 498", "1 499", "1 500"]
DAY_PASS_PRICE = ["490", "491", "492", "493", "494", "495", "496", "497", "498", "499", "500"]

def verify_pdf(pdf_bytes, supabase):
    # Open the PDF file
    pdf_stream = BytesIO(pdf_bytes)

    # Pass the stream to PdfReader
    reader = PdfReader(pdf_stream)
    
    for page in reader.pages:
        text = page.extract_text()
        lines = text.split("\n")

        company_name = ""
        vendor_id = ""
        payment = ""
        customer_name = ""
        transaction_time = ""
        transaction_id = ""

        try:
            company_name = lines[1]
            vendor_id = lines[5].split(" ")[2]
            payment = lines[3][:-2]
            customer_name = lines[6]
            transaction_time = lines[7]
            transaction_id = lines[4].split(" ")[2]
        except:
            return {"approved": False,
                    "reason": "Wrong PDF", 
                    "days_added": 0, 
                    "company_name": company_name,
                    "vendor_id": vendor_id,
                    "payment": payment, 
                    "transaction_id": transaction_id,
                    "customer_name": customer_name,
                    "transaction_time": transaction_time}
        
        # Check DB for repetition
        response = supabase.table("records").select("transaction_id").eq("status", "Approved").execute()
        rows = response.data
        for row in rows:
            if transaction_id == row["transaction_id"]:
                return {"approved": False,
                        "reason": "Repeated transaction ID", 
                        "days_added": 0, 
                        "company_name": company_name,
                        "vendor_id": vendor_id,
                        "payment": payment, 
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "transaction_time": transaction_time}

        # Check Company Credentials First
        if company_name == COMPANY and vendor_id == COMPANY_ID:
            if payment in MONTH_PASS_PRICE:
                return {"approved": True, 
                        "reason": "Passed 1 month verification", 
                        "days_added": 30, 
                        "company_name": company_name,
                        "vendor_id": vendor_id,
                        "payment": payment, 
                        "transaction_id": transaction_id,
                        "customer_name": customer_name,
                        "transaction_time": transaction_time}
            elif payment in DAY_PASS_PRICE:
                return {"approved": True,
                        "reason": "Passed 1 day verification", 
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