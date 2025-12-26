from I_A_H.parser.item_parser import parse_item_data

def transformar_documento(doc):
    raw_text = doc.get("raw_text", "")

    item_data, sanitized_text = parse_item_data(raw_text)

    item_data.setdefault("class", "Unknown")
    item_data.setdefault("item_tier", "Unknown")
    item_data.setdefault("seller", "Unknown")

    return {
        "id": str(doc.get("_id")),
        "raw_text": raw_text,
        "sanitized_text": sanitized_text,
        "parsed": item_data
    }
