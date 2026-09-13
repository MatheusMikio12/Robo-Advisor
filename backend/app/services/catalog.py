"""Importadores públicos com limite de tamanho e sem URLs fornecidas pelo usuário."""
import csv
from datetime import datetime, date, timezone
import hashlib
import io
import zipfile
import httpx

TESOURO_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv"
CVM_URL = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/registro_fundo_classe.zip"


def download(url: str) -> bytes:
    with httpx.stream("GET", url, timeout=45, follow_redirects=True) as response:
        response.raise_for_status()
        chunks, size = [], 0
        for chunk in response.iter_bytes():
            size += len(chunk)
            if size > 50_000_000:
                raise ValueError("Fonte ultrapassou o limite de 50 MB.")
            chunks.append(chunk)
        return b"".join(chunks)


def number(value):
    result = float(value.replace(".", "").replace(",", "."))
    if not __import__("math").isfinite(result):
        raise ValueError("Valor inválido na fonte.")
    return result


def treasury_csv(content: bytes) -> list[dict]:
    rows = csv.DictReader(io.StringIO(content.decode("utf-8-sig")), delimiter=";")
    latest, products = None, {}
    for row in rows:
        observed = datetime.strptime(row["Data Base"], "%d/%m/%Y").date()
        maturity = datetime.strptime(row["Data Vencimento"], "%d/%m/%Y").date()
        if latest and observed < latest:
            continue
        if latest is None or observed > latest:
            products = {}
            latest = observed
        if maturity <= date.today():
            continue
        name = row["Tipo Titulo"]
        price = number(row["PU Compra Manha"])
        if price <= 0:
            continue
        selic = "Selic" in name
        inflation = "IPCA" in name
        simple = selic or (inflation and "Juros" not in name)
        product_id = "td-" + hashlib.sha256(f"{name}-{maturity}".encode()).hexdigest()[:20]
        products[product_id] = {
            "id": product_id, "name": f"{name} {maturity.year}", "issuer": "Tesouro Nacional",
            "asset_class": "liquidez" if selic else "inflacao" if inflation else "outros",
            "platform": "Tesouro Direto", "currency": "BRL", "risk": 0 if selic else 1,
            "price": price, "rate_pct": number(row["Taxa Compra Manha"]),
            "indexer": "Selic +" if selic else "IPCA +" if inflation else "Prefixado",
            "minimum": round(price * .01, 2), "liquidity_days": 1, "fee_pct": .2,
            "maturity": maturity.isoformat(), "as_of": observed.isoformat(),
            "source": TESOURO_URL, "eligible": simple, "quote_type": "Referência diária, não oferta executável",
            "tax": "IR sobre ganhos; IOF pode incidir em resgates de curto prazo. Confira regras vigentes.",
            "risks": "Venda antecipada a preço de mercado pode gerar perda. Liquidação depende de horários e condições do programa.",
            "cost_note": "Custódia de referência; isenções e custos da instituição devem ser confirmados.",
            "fgc": False,
        }
    if not products:
        raise ValueError("A fonte não retornou títulos válidos.")
    return list(products.values())


def cvm_zip(content: bytes) -> list[dict]:
    result = []
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for entry in archive.infolist():
            if not entry.filename.endswith(".csv") or entry.file_size > 100_000_000:
                continue
            with archive.open(entry) as raw:
                data = raw.read()
                try:
                    decoded = data.decode("utf-8-sig")
                except UnicodeDecodeError:
                    decoded = data.decode("latin-1")
                rows = csv.DictReader(io.StringIO(decoded, newline=None), delimiter=";")
                for row in rows:
                    cnpj = row.get("CNPJ_Fundo") or row.get("CNPJ_FUNDO") or row.get("CNPJ_Classe")
                    name = row.get("Denominacao_Social") or row.get("DENOM_SOCIAL")
                    if not cnpj or not name:
                        continue
                    result.append({"id": f"cvm-{cnpj}", "name": name, "cnpj": cnpj,
                                   "issuer": row.get("Administrador", "Não informado"), "asset_class": "outros",
                                   "currency": "BRL", "source": CVM_URL, "as_of": date.today().isoformat(),
                                   "eligible": False, "status": row.get("Situacao", row.get("SIT", "Não informada")),
                                   "quote_type": "Cadastro público; custos, risco e disponibilidade ainda não verificados"})
    if not result:
        raise ValueError("Formato cadastral da CVM não reconhecido. Catálogo anterior preservado.")
    return result


def fetch_products(source: str) -> list[dict]:
    return treasury_csv(download(TESOURO_URL)) if source == "tesouro" else cvm_zip(download(CVM_URL))
