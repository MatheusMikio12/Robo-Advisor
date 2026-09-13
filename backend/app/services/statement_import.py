import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import io
import re


def parse_statement(content: str, kind: str, account: str) -> list[dict]:
    if kind == "csv":
        delimiter = ";" if ";" in content.splitlines()[0] else ","
        reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")), delimiter=delimiter)
        if not {"date", "description", "amount"}.issubset(reader.fieldnames or []):
            raise ValueError("Use as colunas date,description,amount,id (data AAAA-MM-DD; id opcional).")
        source = list(reader)
    else:
        if "<!ENTITY" in content.upper() or "<!DOCTYPE" in content.upper():
            raise ValueError("Declarações externas não são aceitas.")
        source = []
        for block in re.findall(r"<STMTTRN>(.*?)</STMTTRN>", content, re.S | re.I):
            def tag(name):
                match = re.search(rf"<{name}>([^<\r\n]+)", block, re.I)
                return match.group(1).strip() if match else ""
            day = tag("DTPOSTED")[:8]
            source.append({"date": f"{day[:4]}-{day[4:6]}-{day[6:8]}", "description": tag("MEMO") or tag("NAME"),
                           "amount": tag("TRNAMT"), "id": tag("FITID")})
    if not source or len(source) > 3000:
        raise ValueError("O extrato deve conter entre 1 e 3000 movimentações.")
    result, occurrence = [], {}
    for idx, row in enumerate(source, 1):
        try:
            day = date.fromisoformat(row["date"]).isoformat()
            amount = Decimal(row["amount"].replace(",", "."))
            if not amount.is_finite() or abs(amount) > Decimal("1000000000000"):
                raise ValueError()
            description = row["description"].strip()[:250]
            if not description:
                raise ValueError()
        except (KeyError, TypeError, ValueError, InvalidOperation):
            raise ValueError(f"Movimentação {idx}: data, descrição ou valor inválido.") from None
        identity = row.get("id") or f"{day}|{description}|{amount}"
        occurrence[identity] = occurrence.get(identity, 0) + 1
        suffix = "" if row.get("id") else f"|{occurrence[identity]}"
        fingerprint = hashlib.sha256(f"{account}|{identity}{suffix}".encode()).hexdigest()
        result.append({"external_id": fingerprint, "date": day, "description": description,
                       "amount": float(amount), "account": account, "currency": "BRL"})
    return result
