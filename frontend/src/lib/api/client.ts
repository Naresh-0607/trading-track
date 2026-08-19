import { env } from '$env/dynamic/public';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
export class ApiError extends Error { constructor(public status:number,message:string){super(message)} }
export async function api<T>(path:string, init:RequestInit={}):Promise<T>{
 const token=browser?localStorage.getItem('token'):null; const headers=new Headers(init.headers); headers.set('Content-Type','application/json'); if(token)headers.set('Authorization',`Bearer ${token}`);
 const response=await fetch(`${env.PUBLIC_API_URL||'http://localhost:8000/api/v1'}${path}`,{...init,headers});
 if(!response.ok){let message='Something went wrong';try{message=(await response.json()).detail||message}catch{}if(response.status===401&&browser){localStorage.removeItem('token');void goto('/')}throw new ApiError(response.status,message)}
 return response.status===204?undefined as T:response.json();
}
