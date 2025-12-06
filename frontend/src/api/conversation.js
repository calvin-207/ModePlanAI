import {
  ajaxGet,
  ajaxPost,
  ajaxDelete,
  ajaxPut,
  ajaxPatch,
  uploadImg,
  ajaxGetDetailByID,
  ajaxDownloadExcel,
  uploadFileParams,
  getDownloadFile,
  downloadFile,
} from "./request";
import sysConfig from "@/config";
import { getToken } from "@/utils/util";

const Api = {};
// 获取验证码
Api.postChat = (params) => ajaxPost({ url: `/api/modeplan/chat/`, params });

Api.postChatStream = (params) => {
  const token = getToken();
  const controller = new AbortController();
  const responsePromise = fetch(sysConfig.API_URL + `/api/modeplan/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: sysConfig.TOKEN_PREFIX + token,
    },
    body: JSON.stringify(params || {}),
    signal: controller.signal,
  });
  return { controller, responsePromise };
};

export default Api;

