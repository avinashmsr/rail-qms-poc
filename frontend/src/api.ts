const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const fetchLineStats = async () => (await fetch(`${API}/stats/lines`)).json();
export const fetchPads = async () => (await fetch(`${API}/pads`)).json();