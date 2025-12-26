def validar_item(item: dict) -> bool:
    parsed = item.get("parsed", {})

    # Campos obrigatórios mínimos
    obrigatorios = [
        "name",
        "class",
        "item_tier",
        "price"
    ]

    for campo in obrigatorios:
        if campo not in parsed:
            return False

    # Tipos básicos
    if not isinstance(parsed["price"], int):
        return False

    if parsed["price"] <= 0:
        return False

    # Regras de sanidade
    if parsed["class"] == "Unknown":
        return False

    if parsed["item_tier"] == "Unknown":
        return False

    return True
