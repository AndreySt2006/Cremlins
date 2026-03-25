export interface KremlinLocation {
  lat: number
  lon: number
}

export interface KremlinListItem {
  id: number
  name: string
  location: KremlinLocation
  previewImageUrl: string | null
  city: string | null
  yearBuilt: number | null
}

export interface KremlinDetail extends KremlinListItem {
  description: string | null
  wikipediaUrl: string | null
  wikidataId: string | null
  images: string[]
  commentsCount: number
}
