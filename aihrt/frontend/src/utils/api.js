const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(method, path, body, isFormData = false) {
  const opts = {
    method,
    headers: isFormData ? {} : { "Content-Type": "application/json" },
    body: body
      ? isFormData
        ? body
        : JSON.stringify(body)
      : undefined,
  };

  const res = await fetch(`${BASE_URL}${path}`, opts);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

export const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  postForm: (path, formData) => request("POST", path, formData, true),
};

export async function uploadAudio(sessionId, questionId, blob) {
  const formData = new FormData();
  formData.append("question_id", questionId);
  formData.append("file", blob, "response.wav");
  return api.postForm(`/audio/upload/${sessionId}`, formData);
}
