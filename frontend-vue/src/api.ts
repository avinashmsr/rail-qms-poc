export const API = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')
export const fetchLineStats = async () => (await fetch(`${API}/stats/lines`)).json();
export const fetchPads = async () => (await fetch(`${API}/pads`)).json();

export const paths = {
  predictByMix:      () => `${API}/predict/material_mix`,
  predictByPad:      (id: string|number) => `${API}/predict/pad?id=${id}`,
  xaiByPad:          (id: string|number) => `${API}/xai/pad?id=${id}`,
  reviewsList:       (status='PENDING', page=1, pageSize=20) =>
                      `${API}/reviews?status=${status}&page=${page}&page_size=${pageSize}`,
  reviewAction:      (id: string|number, action: 'approve'|'reject'|'override') =>
                      `${API}/reviews/${id}/${action}`,
  modelInfo:         () => `${API}/model/info`,
  modelMetrics:      () => `${API}/model/metrics`,
  modelRetrain:      () => `${API}/model/retrain`,
  modelStatus:       (jobId: string) => `${API}/model/status?job_id=${jobId}`,
  cvDefects:         (limit=20, label='', minScore=0) =>
                      `${API}/cv/defects?limit=${limit}${label?`&label=${encodeURIComponent(label)}`:''}&min_score=${minScore}`,
  padsPaged:         (page=1, pageSize=20) => `${API}/pads?page=${page}&page_size=${pageSize}`,
  stages:            () => `${API}/stages`,
}