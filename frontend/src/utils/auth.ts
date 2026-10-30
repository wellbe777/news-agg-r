// src/utils/auth.ts
import { jwtDecode } from "jwt-decode"; 

interface JwtPayload {
  exp: number;
}

export function isTokenValid(token: string | null): boolean {
  if (!token) return false;
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}
