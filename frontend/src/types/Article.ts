export interface Category {
  id: number;
  name: string;
}

export interface Source {
  id?: number;
  name: string;
  homepage?: string;
}

export interface Article {
  id: number;
  title: string;
  summary?: string;
  content?: string;
  url: string;
  image_url?: string;
  published_at: string;
  source?: Source | string;
  categories: (Category | string)[];
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

