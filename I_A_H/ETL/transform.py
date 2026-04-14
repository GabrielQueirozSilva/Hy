from I_A_H.parser.item_parser import parse_item_data
from dotenv import load_dotenv

load_dotenv() 
 
def transformar_documento(doc, valid, reason, collection):
    item_data = doc.get("parsed", {})

    if valid is True:
        etl_status = "validated"
    elif valid is False and reason != "PARSED_MISSING":
        etl_status = "quarantine"
    else:
        etl_status = "rejected"

    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "etl_status": etl_status,
            "etl_errors": reason
        }}
    )

    return {
        "id": str(doc.get("_id")),
        "scan_timestamp": doc.get("scan_timestamp"),
        "raw_text": doc.get("raw_text"),
        "sanitized_text": doc.get("sanitized_text"),
        "parsed": item_data
    }