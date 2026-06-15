import re
import random
import string
from core.groups import get_mask_by_group

DATAMATRIX_URL_TEMPLATE = "https://barcode.tec-it.com/barcode.ashx?data={full_code}&code=DataMatrix&multiplebarcodes=false&translate-esc=false&unit=Fit&dpi=96&imagetype=Png"
DATAMATRIX_URL_TEMPLATE_MANUAL = "https://barcode.tec-it.com/barcode.ashx?data={full_code_manual}&code=DataMatrix&multiplebarcodes=false&translate-esc=false&unit=Fit&dpi=96&imagetype=Png"
EAN13_URL_TEMPLATE = "https://barcode.tec-it.com/barcode.ashx?data={full_code}&code=EAN13&multiplebarcodes=false&translate-esc=false&unit=Fit&dpi=96&imagetype=Png"
EAN8_URL_TEMPLATE = "https://barcode.tec-it.com/barcode.ashx?data={full_code}&code=EAN8&multiplebarcodes=false&translate-esc=false&unit=Fit&dpi=96&imagetype=Png"


def generate_random_string(length: int) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def build_full_code(code_type: str, ean: str, group_name: str = None) -> str:
    if code_type == "EAN-13" or code_type == "EAN-8":
        return ean
    elif code_type == "DataMatrix":
        if not group_name:
            raise ValueError("Для DataMatrix требуется выбрать группу маркировки")
        mask = get_mask_by_group(group_name)
        result = mask

        def replace_random(match):
            length = int(match.group(1))
            return generate_random_string(length)
        result = re.sub(r'\{random:(\d+)\}', replace_random, result)

        result = result.replace("{gs}", "\x1D")
        result = result.replace("{ean}", ean)
        return result
    else:
        raise ValueError(f"Неизвестный тип кода: {code_type}")


def get_code_url(code_type: str, full_code: str) -> str:
    if code_type == "EAN-13":
        return EAN13_URL_TEMPLATE.format(full_code=full_code)
    elif code_type == "EAN-8":
        return EAN8_URL_TEMPLATE.format(full_code=full_code)
    elif code_type == "DataMatrix":
        return DATAMATRIX_URL_TEMPLATE.format(full_code=full_code)
    else:
        raise ValueError(f"Неизвестный тип кода: {code_type}")


def get_manual_code_url(saved_code: str) -> str:
    return DATAMATRIX_URL_TEMPLATE_MANUAL.format(full_code_manual=saved_code)