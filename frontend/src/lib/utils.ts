import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/*
Преобразует относительный путь к изображению в абсолютный URL бэкенда.
Если передан абсолютный URL (например, placeholder), возвращает его без изменений.
*/
export function getImageUrl(url: string | null | undefined): string {
  if (!url) return "";

  // Если это уже абсолютная ссылка (на внешние ресурсы или плейсхолдеры)
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }

  // Получаем базовый URL бэкенда из переменных окружения
  const baseUrl = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";
  const cleanBase = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
  const cleanUrl = url.startsWith("/") ? url : `/${url}`;

  return `${cleanBase}${cleanUrl}`;
}
