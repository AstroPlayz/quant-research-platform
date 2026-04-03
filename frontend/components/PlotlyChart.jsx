'use client'

import dynamic from 'next/dynamic'

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

export default function PlotlyChart({ data, layout, style }) {
  return (
    <Plot
      data={data}
      layout={layout}
      style={style}
      config={{ responsive: true, displaylogo: false }}
      useResizeHandler
    />
  )
}
