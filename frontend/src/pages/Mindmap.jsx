import { useEffect, useRef, useState } from 'react'
import { getTopics } from '../api/client'
import { Network, CircleDot, Lock, CheckCircle } from 'lucide-react'

export default function Mindmap() {
  const svgRef = useRef(null)
  const [topics, setTopics] = useState([])
  const [loading, setLoading] = useState(true)
  const [userId] = useState(() => parseInt(localStorage.getItem('hackerlabacademy_user_id')))

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    try {
      const data = await getTopics(userId)
      setTopics(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (loading || !topics.length || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth
    const height = 500

    // Build nodes and links
    const nodeMap = new Map()
    topics.forEach(t => {
      nodeMap.set(t.slug, {
        id: t.id,
        slug: t.slug,
        name: t.name,
        completed: t.progress?.theory_completed && t.progress?.quiz_passed,
        unlocked: t.unlocked,
        x: width / 2 + (Math.random() - 0.5) * 50,
        y: height / 2 + (Math.random() - 0.5) * 50
      })
    })

    const links = []
    topics.forEach(t => {
      const prereqs = JSON.parse(t.prerequisites || '[]')
      prereqs.forEach(prereqSlug => {
        const source = nodeMap.get(prereqSlug)
        const target = nodeMap.get(t.slug)
        if (source && target) {
          links.push({ source: source.id, target: target.id })
        }
      })
    })

    // Convert to D3 structures
    const nodes = Array.from(nodeMap.values())
    const linkSelection = links.map(l => ({ source: nodes.find(n => n.id === l.source), target: nodes.find(n => n.id === l.target) })).filter(l => l.source && l.target)

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(linkSelection).id(d => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('y', d3.forceY(height / 2).strength(0.1))
      .force('x', d3.forceX(width / 2).strength(0.1))

    // Draw links
    const link = svg.append('g')
      .selectAll('line')
      .data(linkSelection)
      .enter()
      .append('line')
      .attr('stroke', '#30363d')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', d => (d.source.unlocked && d.target.unlocked) ? '0' : '5,5')

    // Draw nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', d => d.completed ? 18 : 14)
      .attr('fill', d => {
        if (!d.unlocked) return '#21262d'  // locked = gray
        if (d.completed) return '#39d353' // completed = green
        return '#e3b341' // unlocked = yellow
      })
      .attr('stroke', '#0d1117')
      .attr('stroke-width', 3)
      .call(drag(simulation))

    // Labels
    const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text(d => d.name)
      .attr('font-size', 11)
      .attr('fill', '#c9d1d9')
      .attr('text-anchor', 'middle')
      .attr('dy', -22)

    // Tooltip (simple title)
    node.append('title')
      .text(d => `${d.name}\n${d.unlocked ? (d.completed ? '✅ Completed' : '🔓 Unlocked') : '🔒 Locked'}`)

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y)
    })

    function drag(sim) {
      function dragstarted(event, d) {
        if (!event.active) sim.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
      }
      function dragged(event, d) {
        d.fx = event.x
        d.fy = event.y
      }
      function dragended(event, d) {
        if (!event.active) sim.alphaTarget(0)
        d.fx = null
        d.fy = null
      }
      return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended)
    }
  }, [loading, topics, userId])

  if (loading) return (
    <div className="p-8 text-[#8b949e] text-center animate-pulse">
      Ładowanie mapy tematów...
    </div>
  )

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-[#f0f6fc] mb-2 flex items-center gap-2">
        <Network size={24} className="text-[#58a6ff]" />
        Mindmap Tematów
      </h1>
      <p className="text-[#8b949e] mb-6">
        Graf zależności między tematami. Zielony = ukończony, Żółty = dostępny, Szary = zablokowany (wymaga prerequisite'ów).
        Przeciągaj węzły.
      </p>

      <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
        <svg ref={svgRef} width="100%" height="500" style={{ maxWidth: '100%' }} />
      </div>

      <div className="mt-4 flex items-center gap-6 text-sm text-[#8b949e]">
        <div className="flex items-center gap-2">
          <CheckCircle size={16} className="text-[#39d353]" /> Ukończony
        </div>
        <div className="flex items-center gap-2">
          <CircleDot size={16} className="text-[#e3b341]" /> Dostępny
        </div>
        <div className="flex items-center gap-2">
          <Lock size={16} className="text-[#8b949e]" /> Zablokowany
        </div>
      </div>
    </div>
  )
}
