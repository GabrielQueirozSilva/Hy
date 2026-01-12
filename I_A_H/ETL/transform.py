from I_A_H.parser.item_parser import parse_item_data

def transformar_documento(doc):
    raw_text = doc.get("raw_text", "")

    item_data, sanitized_text = parse_item_data(raw_text)

    if "seller" not in item_data:
        item_data["seller"] = None

    if "pet_type" not in item_data:
        item_data["pet_type"] = None

    return {
        "id": str(doc.get("_id")),
        "scan_timestamp": doc.get("scan_timestamp"),
        "raw_text": raw_text,
        "sanitized_text": sanitized_text,
        "parsed": item_data
    }
