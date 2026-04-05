import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect, useRef, useState, useCallback } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { toast } from 'sonner'
import { Loader2, House } from 'lucide-react'
import { useKremlins } from '@/hooks/useKremlins'
import { useMapSearchStore } from '@/store/mapSearchStore'
import type { KremlinListItem } from '@/types/kremlin'

export const Route = createFileRoute('/')({
  component: MapPage,
})

const INITIAL_CENTER: [number, number] = [37.62, 55.75]
const INITIAL_ZOOM = 4

const PIN_SVG = `
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="14" cy="14" r="13" fill="#DC2626" stroke="white" stroke-width="1.5"/>
    <circle cx="14" cy="14" r="3" fill="white"/>
  </svg>
`

function buildPopupHTML(kremlin: KremlinListItem): string {
  const cityYear = [
    kremlin.city,
    kremlin.yearBuilt ? `${kremlin.yearBuilt} г.` : null,
  ]
    .filter(Boolean)
    .join(' · ')

  return `<div style="font-family:Inter,sans-serif;padding:2px">
    <p style="font-size:17px;font-weight:700;margin:0 0 4px;line-height:1.3">${kremlin.name}</p>
    ${cityYear ? `<p style="font-size:12px;color:#6b7280;margin:0 0 12px">${cityYear}</p>` : '<div style="margin-bottom:12px"></div>'}
    <button
      id="btn-kremlin-${kremlin.id}"
      style="background:#DC2626;color:white;border:none;border-radius:6px;padding:7px 0;font-size:13px;font-weight:600;cursor:pointer;width:100%;font-family:Inter,sans-serif"
    >Подробнее</button>
  </div>`
}

function MapPage() {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)

  const navigate = useNavigate()
  const navigateRef = useRef(navigate)
  navigateRef.current = navigate

  const popupOpenRef = useRef(false)
  const currentPopupRef = useRef<maplibregl.Popup | null>(null)
  const zoomedInRef = useRef(false)

  const { data: kremlins, isLoading, isError } = useKremlins()
  const { pendingKremlin, setPendingKremlin } = useMapSearchStore()

  useEffect(() => {
    if (isError) toast.error('Не удалось загрузить кремли')
  }, [isError])

  // Initialise map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      center: INITIAL_CENTER,
      zoom: INITIAL_ZOOM,
    })

    mapRef.current = map
    map.on('load', () => setMapLoaded(true))

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  const flyHome = useCallback(() => {
    const map = mapRef.current
    if (!map) return
    currentPopupRef.current?.remove()
    map.flyTo({ center: INITIAL_CENTER, zoom: INITIAL_ZOOM, speed: 1.2 })
    zoomedInRef.current = false
  }, [])

  // Open popup + flyTo helper
  const openPopupForKremlin = useCallback((kremlin: KremlinListItem) => {
    const map = mapRef.current
    if (!map) return

    map.flyTo({
      center: [kremlin.location.lon, kremlin.location.lat],
      zoom: 14,
      speed: 1.2,
    })
    zoomedInRef.current = true

    currentPopupRef.current?.remove()

    const popup = new maplibregl.Popup({ offset: 20, maxWidth: '260px' })
      .setLngLat([kremlin.location.lon, kremlin.location.lat])
      .setHTML(buildPopupHTML(kremlin))
      .addTo(map)

    currentPopupRef.current = popup
    popupOpenRef.current = true
    popup.on('close', () => {
      popupOpenRef.current = false
      currentPopupRef.current = null
    })

    requestAnimationFrame(() => {
      const btn = document.getElementById(`btn-kremlin-${kremlin.id}`)
      btn?.addEventListener('click', () => {
        navigateRef.current({
          to: '/kremlins/$kremlinId',
          params: { kremlinId: String(kremlin.id) },
        })
      })
    })
  }, [])

  // React to search selection from the header
  useEffect(() => {
    if (!pendingKremlin || !mapLoaded) return
    openPopupForKremlin(pendingKremlin)
    setPendingKremlin(null)
  }, [pendingKremlin, mapLoaded, openPopupForKremlin, setPendingKremlin])

  // Add markers after map load and data fetch
  useEffect(() => {
    const map = mapRef.current
    if (!map || !mapLoaded || !kremlins) return

    const markers: maplibregl.Marker[] = []
    const tooltip = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      offset: 16,
    })

    for (const kremlin of kremlins) {
      const el = document.createElement('div')
      el.innerHTML = PIN_SVG.trim()
      el.style.cssText = 'cursor:pointer;width:28px;height:28px;display:flex'

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([kremlin.location.lon, kremlin.location.lat])
        .addTo(map)

      el.addEventListener('mouseenter', () => {
        if (popupOpenRef.current) return
        tooltip
          .setLngLat([kremlin.location.lon, kremlin.location.lat])
          .setHTML(
            `<span style="font-size:13px;font-weight:500;white-space:nowrap;font-family:Inter,sans-serif">${kremlin.name}</span>`,
          )
          .addTo(map)
      })
      el.addEventListener('mouseleave', () => tooltip.remove())

      el.addEventListener('click', (e) => {
        e.stopPropagation()
        tooltip.remove()
        openPopupForKremlin(kremlin)
      })

      markers.push(marker)
    }

    return () => {
      markers.forEach((m) => m.remove())
      tooltip.remove()
    }
  }, [mapLoaded, kremlins, openPopupForKremlin])

  // Escape — двухшаговый возврат
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === 'Escape' &&
        !(document.activeElement instanceof HTMLInputElement) &&
        !(document.activeElement instanceof HTMLTextAreaElement)
      ) {
        if (popupOpenRef.current) {
          currentPopupRef.current?.remove()
        } else if (zoomedInRef.current) {
          flyHome()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [flyHome])

  return (
    <div className="relative" style={{ height: 'calc(100vh - 3.5rem)' }}>
      <div ref={containerRef} className="absolute inset-0" />

      {/* Home button */}
      <button
        onClick={flyHome}
        title="Вернуться к карте России (Esc)"
        className="absolute bottom-6 left-4 z-10 flex items-center gap-1.5 rounded-xl bg-white px-3 py-2 text-xs font-medium text-gray-600 shadow-md hover:bg-gray-50 active:bg-gray-100"
      >
        <House className="h-4 w-4" />
        Вся Россия
      </button>

      {isLoading && (
        <div className="absolute bottom-6 right-6 z-10 rounded-full bg-white p-2 shadow-md">
          <Loader2 className="h-5 w-5 animate-spin text-red-600" />
        </div>
      )}
    </div>
  )
}
