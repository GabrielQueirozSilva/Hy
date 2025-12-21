import cv2

def draw_overlay(frame, detection):
    item = detection.get("parsed", {})
    y = 40

    lines = [
        f"Conf: {detection['confidence']:.2f}",
        f"Name: {item.get('name')}",
        f"Tier: {item.get('item_tier')}",
        f"Class: {item.get('class')}",
        f"Price: {item.get('price')}",
        f"Seller: {item.get('seller')}"
    ]

    for line in lines:
        cv2.putText(
            frame, line,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        y += 25
