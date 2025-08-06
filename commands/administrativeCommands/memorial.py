import datetime

memorial_dic = {datetime.date(2025, 8, 14): "1 month just like that :candle: We hope heaven's keeping you safe, brother.",
                datetime.date(2025, 9, 22): "Happy 21st Cal! You would've been so proud of me :face_holding_back_tears:",
                datetime.date(2025, 10, 14): "3 month",
                datetime.date(2026, 1, 14): "6 month",
                datetime.date(2026, 4, 14): "9 month",
                datetime.date(2026, 7, 14): "12 month",}

def memorial():
    """returns tuple of form (memorial, message)"""
    today = datetime.date.today()
    if today in memorial_dic:
        memorial = (True, memorial_dic[today])
        memorial_dic.pop(today, None)
        return memorial
    else:
        return (False, None)