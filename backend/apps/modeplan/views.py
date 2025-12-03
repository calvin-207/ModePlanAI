import json
from urllib.request import Request, urlopen
from django.conf import settings
from utils.apiview import CustomAPIView
from utils.jsonResponse import DetailResponse, ErrorResponse

class FigmaReadView(CustomAPIView):
    permission_classes = []

    def post(self, request):
        file_key = request.data.get("file_key")
        token = request.data.get("token") or request.headers.get("X-Figma-Token")
        if not file_key:
            return ErrorResponse(msg="缺少file_key")
        if not token:
            return ErrorResponse(msg="缺少token")
        url = f"https://api.figma.com/v1/files/{file_key}"
        try:
            req = Request(url, headers={"X-Figma-Token": token})
            resp = urlopen(req)
            data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return ErrorResponse(msg="读取Figma失败")
        result = {"name": data.get("name"), "pages": []}
        document = (data.get("document") or {})
        children = document.get("children") or []
        for page in children:
            page_info = {"id": page.get("id"), "name": page.get("name"), "type": page.get("type"), "frames": []}
            for node in page.get("children") or []:
                if node.get("type") in ("FRAME", "COMPONENT", "COMPONENT_SET", "INSTANCE"):
                    page_info["frames"].append({"id": node.get("id"), "name": node.get("name"), "type": node.get("type")})
            result["pages"].append(page_info)
        return DetailResponse(data=result, msg="读取成功")

