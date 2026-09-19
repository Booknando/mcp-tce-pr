import io
import zipfile

import httpx
import pytest
import respx
from defusedxml.common import DefusedXmlException

from mcp_tce_pr.client import SourceError
from mcp_tce_pr.pit import query_pit, query_xml

XML = '<root><Contrato cidade="São José" valor="1"/><Contrato cidade="Curitiba" valor="2"/></root>'.encode()


def test_xml_filters_pagination_and_entities():
    result = query_xml(XML, {"cidade": "sao jose"}, 0, 1)
    assert result["total_encontrado"] == 1
    assert result["registros"][0]["valor"] == "1"
    assert query_xml(XML, {}, 0, 1)["proximo_deslocamento"] == 1
    with pytest.raises(SourceError):
        query_xml(XML, {"inexistente": "x"}, 0, 1)
    with pytest.raises(DefusedXmlException):
        query_xml(b'<!DOCTYPE root [<!ENTITY x "boom">]><root a="&x;"/>', {}, 0, 1)


@respx.mock
def test_nested_pit_zip():
    inner, outer = io.BytesIO(), io.BytesIO()
    with zipfile.ZipFile(inner, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Contrato.xml", XML)
    with zipfile.ZipFile(outer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("2026_410010_Contrato.zip", inner.getvalue())
    body = outer.getvalue()
    url = "https://pit.tce.pr.gov.br/Arquivos/test.zip"
    respx.head(url).mock(
        return_value=httpx.Response(200, headers={"content-length": str(len(body))})
    )

    def respond(req):
        a, b = map(int, req.headers["range"].split("=")[1].split("-"))
        return httpx.Response(
            206, content=body[a : b + 1], headers={"content-range": f"bytes {a}-{b}/{len(body)}"}
        )

    respx.get(url).mock(side_effect=respond)
    index = query_pit(url, 2026, "410010", "Contrato", None, {}, 0, 2)
    assert index["arquivos"][0]["nome"] == "Contrato.xml"
    result = query_pit(url, 2026, "410010", "Contrato", "Contrato.xml", {}, 1, 1)
    assert result["registros"][0]["valor"] == "2"
