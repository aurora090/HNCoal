from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse,FileResponse
import json
class LoginCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if request.path_info in ["/queryNeo4jInfoByID","/queryNeo4jInfoByname",'/FuzzyQueryName',"/saveNodeToCSV",
                                 '/showNodeForTable','/uploadExcelData']:
            is_login = request.session.get("is_login",0)

            if is_login:
                print("已登录")
                return

            tooken={
                    'status':0,
                    'message':'请登录',
                    }
            print("请登录")
            return HttpResponse(json.dumps(tooken,ensure_ascii=False))
        
        return
