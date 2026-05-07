import { useEffect, useState } from 'react'
import { getVideosByTopic, getVideos } from '../api/client'
import { Play, Filter, Globe } from 'lucide-react'

const CATEGORIES = ['tutorial', 'demo', 'defense', 'ctf']

export default function Videos() {
  const [videosByTopic, setVideosByTopic] = useState({})
  const [selectedTopic, setSelectedTopic] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [allVideos, setAllVideos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMapping()
  }, [])

  const loadMapping = async () => {
    try {
      const mapping = await getVideosByTopic()
      setVideosByTopic(mapping)
      const topics = Object.keys(mapping)
      if (topics.length > 0) setSelectedTopic(topics[0])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const loadVideosForTopic = async (topicSlug) => {
    setSelectedTopic(topicSlug)
    setLoading(true)
    try {
      const data = await getVideos({ topic_slug: topicSlug, category: selectedCategory || undefined })
      setAllVideos(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleTopicChange = (e) => {
    const topic = e.target.value
    loadVideosForTopic(topic)
  }

  const handleCategoryFilter = (category) => {
    setSelectedCategory(category)
    if (selectedTopic) {
      setLoading(true)
      getVideos({ topic_slug: selectedTopic, category: category || undefined })
        .then(setAllVideos)
        .finally(() => setLoading(false))
    }
  }

  const currentVideos = selectedTopic ? videosByTopic[selectedTopic] || [] : []

  if (loading && Object.keys(videosByTopic).length === 0) {
    return (
      <div className="p-8 text-[#8b949e] text-center animate-pulse">
        Ładowanie filmów...
      </div>
    )
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2 flex items-center gap-2">
        <Play size={24} className="text-[#ff0000]" />
        YouTube Security Videos
      </h1>
      <p className="text-[#8b949e] mb-6">Wyselekcjonowane filmy edukacyjne per temat</p>

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 mb-6">
        <div className="flex items-center gap-4">
          <Filter size={16} className="text-[#8b949e]" />
          <select
            value={selectedTopic}
            onChange={handleTopicChange}
            className="bg-[#0d1117] border border-[#30363d] rounded px-3 py-1.5 text-sm text-[#c9d1d9] flex-1 max-w-xs"
          >
            {Object.keys(videosByTopic).map(slug => (
              <option key={slug} value={slug}>{slug.replace(/-/g, ' ')}</option>
            ))}
          </select>
          <div className="flex gap-2">
            <button
              onClick={() => handleCategoryFilter('')}
              className={`px-3 py-1.5 rounded text-xs ${!selectedCategory ? 'bg-[#1f6feb] text-white' : 'bg-[#21262d] text-[#8b949e]'}`}
            >
              Wszystkie
            </button>
            {CATEGORIES.map(cat => (
              <button
                key={cat}
                onClick={() => handleCategoryFilter(cat)}
                className={`px-3 py-1.5 rounded text-xs capitalize ${selectedCategory === cat ? 'bg-[#1f6feb] text-white' : 'bg-[#21262d] text-[#8b949e]'}`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-[#8b949e]">Ładowanie...</div>
      ) : allVideos.length === 0 ? (
        <div className="text-center py-8 text-[#8b949e]">Brak filmów dla tego tematu</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {allVideos.map(video => (
            <div key={video.id} className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden">
              <div className="aspect-video bg-black relative">
                <iframe
                  className="w-full h-full"
                  src={video.url}
                  title={video.title}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
              <div className="p-4">
                <h3 className="text-[#f0f6fc] font-semibold mb-1">{video.title}</h3>
                <p className="text-[#8b949e] text-xs mb-2">{video.channel} • {video.category}</p>
                {video.description && (
                  <p className="text-[#c9d1d9] text-sm">{video.description}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
