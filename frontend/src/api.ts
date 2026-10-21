const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();
if (import.meta.env.PROD && !configuredApiUrl) {
  throw new Error('VITE_API_URL must be set to the deployed API origin for production builds.');
}
export const API = (configuredApiUrl || 'http://127.0.0.1:8000').replace(/\/$/, '');
export type Report = { id:number; public_report_id:string; title:string; description:string; citizen_category:string; ai_suggested_category:string; location_name:string; latitude:number|null; longitude:number|null; severity:string; ai_explanation:string; ai_summary:string; department:string; status:string; image_path:string|null; created_at:string; updated_at:string; resolved_at:string|null };
export type Analytics = { by_category:{name:string;value:number}[]; by_status:{name:string;value:number}[]; by_severity:{name:string;value:number}[]; by_department:{name:string;value:number}[]; trend:{date:string;count:number}[]; average_resolution_hours:number|null; resolved_with_duration:number };

export class NetworkRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkRequestError';
  }
}

function notifyConnection(available: boolean): void {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new Event(available ? 'nexus-network-available' : 'nexus-network-unavailable'),
    );
  }
}

export async function request<T>(path:string, init?:RequestInit):Promise<T>{
  let response:Response;
  try {
    response=await fetch(`${API}${path}`,{...init,headers:{'Content-Type':'application/json',...(init?.headers||{})}});
    notifyConnection(true);
  } catch {
    notifyConnection(false);
    throw new NetworkRequestError('Cannot reach the server. Check your connection and try again.');
  }
  if(!response.ok){let detail='Request failed';try{const body=await response.json();detail=typeof body.detail==='string'?body.detail:JSON.stringify(body.detail||body);}catch{}throw new Error(detail);}
  return response.json();
}
