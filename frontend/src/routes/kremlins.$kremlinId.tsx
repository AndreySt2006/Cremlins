import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { ExternalLink, ArrowLeft, Paperclip, X, Send } from 'lucide-react'
import { useState, useRef } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useKremlin } from '@/hooks/useKremlin'
import { useComments } from '@/hooks/useComments'
import { useRoutesStore } from '@/store/routesStore'
import { useAuthStore } from '@/store/authStore'
import { createComment } from '@/api/comments'
import type { Comment } from '@/types'

export const Route = createFileRoute('/kremlins/$kremlinId')({
  component: KremlinPage,
})

function KremlinPage() {
  const { kremlinId } = Route.useParams()
  const id = Number(kremlinId)
  const navigate = useNavigate()

  const { data, isLoading, isError, error } = useKremlin(id)
  const { isPlanned, isVisited, togglePlanned, toggleVisited } = useRoutesStore()

  if (isLoading) return <SkeletonPage />
  if (isError) return <ErrorPage error={error} />
  if (!data) return null

  const cityYear = [data.city, data.yearBuilt ? `${data.yearBuilt} г.` : null]
    .filter(Boolean)
    .join(' · ')

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8">
      {/* Шапка */}
      <div className="mb-6 flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <button
            onClick={() => navigate({ to: '/' })}
            title="На карту"
            className="mt-1 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{data.name}</h1>
          {cityYear && (
            <p className="mt-1 text-sm text-gray-500">{cityYear}</p>
          )}
          </div>
        </div>
        <div className="flex shrink-0 gap-2">
          <button
            onClick={() => togglePlanned(id)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              isPlanned(id)
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Планирую
          </button>
          <button
            onClick={() => toggleVisited(id)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              isVisited(id)
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Посетил
          </button>
        </div>
      </div>

      {/* Галерея */}
      {data.images.length > 0 ? (
        <div className="-mx-4 mb-6 flex gap-3 overflow-x-auto px-4 pb-2">
          {data.images.map((url, i) => (
            <img
              key={i}
              src={url}
              alt={`${data.name} — фото ${i + 1}`}
              className="h-56 w-auto shrink-0 rounded-xl object-cover"
            />
          ))}
        </div>
      ) : (
        <div className="mb-6 flex h-40 items-center justify-center rounded-xl bg-gray-100 text-sm text-gray-400">
          Фото пока не добавлены
        </div>
      )}

      {/* Описание */}
      <div className="mb-6">
        {data.description ? (
          <p className="leading-relaxed text-gray-800">{data.description}</p>
        ) : (
          <p className="text-sm text-gray-400">Описание пока не добавлено</p>
        )}
      </div>

      {/* Wikipedia */}
      {data.wikipediaUrl && (
        <a
          href={data.wikipediaUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-sm text-red-600 hover:underline"
        >
          <ExternalLink className="h-4 w-4" />
          Читать на Wikipedia
        </a>
      )}

      {/* Комментарии */}
      <CommentSection kremlinId={id} />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Утилиты
// ---------------------------------------------------------------------------

function formatRuDate(iso: string): string {
  return new Date(iso)
    .toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
    .replace(' г.', '')
}

function getInitial(name: string): string {
  return name.trim().charAt(0).toUpperCase()
}

// ---------------------------------------------------------------------------
// CommentSection
// ---------------------------------------------------------------------------

function CommentSection({ kremlinId }: { kremlinId: number }) {
  const { data: comments = [], isLoading } = useComments(kremlinId)
  const { isAuthenticated } = useAuthStore()

  return (
    <section className="mt-10 border-t border-gray-100 pt-8">
      <h2 className="mb-6 text-xl font-semibold text-gray-900">
        Комментарии{comments.length > 0 && ` (${comments.length})`}
      </h2>

      {isAuthenticated ? (
        <CommentForm kremlinId={kremlinId} />
      ) : (
        <p className="mb-6 rounded-lg bg-gray-50 px-4 py-3 text-sm text-gray-600">
          Чтобы оставить комментарий,{' '}
          <a href="/auth" className="font-medium text-red-600 hover:underline">
            войдите
          </a>
        </p>
      )}

      {isLoading ? (
        <CommentsSkeleton />
      ) : comments.length === 0 ? (
        <p className="py-6 text-center text-sm text-gray-400">
          Комментариев пока нет. Будьте первым!
        </p>
      ) : (
        <ul className="space-y-6">
          {comments.map((comment) => (
            <CommentItem key={comment.id} comment={comment} />
          ))}
        </ul>
      )}
    </section>
  )
}

// ---------------------------------------------------------------------------
// CommentItem
// ---------------------------------------------------------------------------

function CommentItem({ comment }: { comment: Comment }) {
  return (
    <li className="flex gap-3">
      {/* Аватар */}
      {comment.authorAvatarUrl ? (
        <img
          src={comment.authorAvatarUrl}
          alt={comment.authorName}
          className="h-9 w-9 shrink-0 rounded-full object-cover"
        />
      ) : (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-red-100 text-sm font-semibold text-red-700">
          {getInitial(comment.authorName)}
        </div>
      )}

      <div className="flex-1 min-w-0">
        {/* Имя и дата */}
        <div className="flex flex-wrap items-baseline gap-2">
          <span className="font-medium text-gray-900">{comment.authorName}</span>
          <span className="text-xs text-gray-400">{formatRuDate(comment.createdAt)}</span>
        </div>

        {/* Текст */}
        <p className="mt-1 text-sm leading-relaxed text-gray-700">{comment.text}</p>

        {/* Фото */}
        {comment.imageUrls.length > 0 && (
          <div className="-ml-0 mt-3 flex gap-2 overflow-x-auto pb-1">
            {comment.imageUrls.map((url, i) => (
              <img
                key={i}
                src={url}
                alt={`Фото ${i + 1}`}
                className="h-28 w-auto shrink-0 rounded-lg object-cover"
              />
            ))}
          </div>
        )}
      </div>
    </li>
  )
}

// ---------------------------------------------------------------------------
// CommentForm
// ---------------------------------------------------------------------------

function CommentForm({ kremlinId }: { kremlinId: number }) {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [text, setText] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [previews, setPreviews] = useState<string[]>([])

  const mutation = useMutation({
    mutationFn: () => createComment(kremlinId, { text, images: files }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', kremlinId] })
      setText('')
      setFiles([])
      setPreviews([])
    },
  })

  function handleFilesChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = Array.from(e.target.files ?? [])
    if (!selected.length) return
    setFiles((prev) => [...prev, ...selected])
    selected.forEach((file) => {
      const url = URL.createObjectURL(file)
      setPreviews((prev) => [...prev, url])
    })
    // сбросить input чтобы повторный выбор тех же файлов работал
    e.target.value = ''
  }

  function removeFile(index: number) {
    URL.revokeObjectURL(previews[index])
    setFiles((prev) => prev.filter((_, i) => i !== index))
    setPreviews((prev) => prev.filter((_, i) => i !== index))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!text.trim()) return
    mutation.mutate()
  }

  return (
    <form onSubmit={handleSubmit} className="mb-8">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ваш комментарий..."
        rows={3}
        className="w-full resize-none rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-800 placeholder-gray-400 outline-none focus:border-red-400 focus:ring-1 focus:ring-red-400 transition-colors"
      />

      {/* Превью выбранных фото */}
      {previews.length > 0 && (
        <div className="mt-2 flex gap-2 overflow-x-auto pb-1">
          {previews.map((src, i) => (
            <div key={i} className="relative shrink-0">
              <img
                src={src}
                alt={`Превью ${i + 1}`}
                className="h-20 w-20 rounded-lg object-cover"
              />
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-gray-700 text-white hover:bg-gray-900 transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="mt-3 flex items-center justify-between">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
        >
          <Paperclip className="h-4 w-4" />
          Прикрепить фото
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          className="hidden"
          onChange={handleFilesChange}
        />

        <button
          type="submit"
          disabled={!text.trim() || mutation.isPending}
          className="inline-flex items-center gap-1.5 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Send className="h-4 w-4" />
          {mutation.isPending ? 'Отправка...' : 'Отправить'}
        </button>
      </div>

      {mutation.isError && (
        <p className="mt-2 text-sm text-red-600">
          Ошибка при отправке. Попробуйте ещё раз.
        </p>
      )}
    </form>
  )
}

// ---------------------------------------------------------------------------
// Скелетоны и ошибка
// ---------------------------------------------------------------------------

function CommentsSkeleton() {
  return (
    <ul className="space-y-6 animate-pulse">
      {[1, 2].map((i) => (
        <li key={i} className="flex gap-3">
          <div className="h-9 w-9 shrink-0 rounded-full bg-gray-200" />
          <div className="flex-1 space-y-2">
            <div className="h-3.5 w-1/4 rounded bg-gray-200" />
            <div className="h-3 rounded bg-gray-200" />
            <div className="h-3 w-3/4 rounded bg-gray-200" />
          </div>
        </li>
      ))}
    </ul>
  )
}

function SkeletonPage() {
  return (
    <div className="container mx-auto max-w-3xl animate-pulse px-4 py-8">
      {/* Шапка */}
      <div className="mb-6 flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="mb-2 h-8 w-2/3 rounded-lg bg-gray-200" />
          <div className="h-4 w-1/3 rounded-lg bg-gray-200" />
        </div>
        <div className="flex gap-2">
          <div className="h-9 w-24 rounded-lg bg-gray-200" />
          <div className="h-9 w-24 rounded-lg bg-gray-200" />
        </div>
      </div>
      {/* Галерея */}
      <div className="mb-6 flex gap-3 overflow-hidden">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-56 w-72 shrink-0 rounded-xl bg-gray-200" />
        ))}
      </div>
      {/* Описание */}
      <div className="mb-6 space-y-2">
        <div className="h-4 rounded bg-gray-200" />
        <div className="h-4 rounded bg-gray-200" />
        <div className="h-4 w-3/4 rounded bg-gray-200" />
      </div>
    </div>
  )
}

function ErrorPage({ error }: { error: unknown }) {
  const navigate = useNavigate()
  const message = error instanceof Error ? error.message : 'Что-то пошло не так'
  return (
    <div className="container mx-auto max-w-3xl px-4 py-16 text-center">
      <p className="mb-4 text-gray-600">{message}</p>
      <button
        onClick={() => navigate({ to: '/' })}
        className="inline-flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
      >
        <ArrowLeft className="h-4 w-4" />
        Назад
      </button>
    </div>
  )
}
