---
title: Chart Types
description: Chart type selection guide with Recharts and D3.js examples for line, bar, pie, area, scatter, and heatmap charts
tags: [chart, line, bar, pie, donut, area, scatter, heatmap, Recharts, D3]
---

# Chart Types

## Line Chart

**Best for:** Trends over time, continuous data (stock prices, temperature, traffic).

```tsx
<LineChart data={data}>
  <Line type="monotone" dataKey="value" stroke="#8884d8" />
</LineChart>
```

Use for multiple data series comparison. Add `<CartesianGrid>`, `<Tooltip>`, `<Legend>` for readability.

## Bar Chart

**Best for:** Comparing categories, rankings (sales by product, users by country).

```tsx
<BarChart data={data}>
  <Bar dataKey="value" fill="#8884d8" />
</BarChart>
```

## Pie / Donut Chart

**Best for:** Part-to-whole relationships (market share, budget allocation).

```tsx
<PieChart>
  <Pie data={data} dataKey="value" nameKey="name" fill="#8884d8" />
</PieChart>
```

Limit to 5-7 slices maximum. For precise comparison, use a bar chart instead.

## Area Chart

**Best for:** Volume over time, stacked categories, cumulative totals.

```tsx
<AreaChart data={data}>
  <Area type="monotone" dataKey="value" fill="#8884d8" />
</AreaChart>
```

## Scatter Plot

**Best for:** Correlation between variables, outlier detection, distribution analysis.

```tsx
<ScatterChart>
  <Scatter data={data} fill="#8884d8" />
</ScatterChart>
```

## Heatmap

**Best for:** Intensity across two dimensions (time patterns, geographic data, matrix data).

```ts
const colorScale = d3
  .scaleSequential(d3.interpolateBlues)
  .domain([0, d3.max(data)]);

svg
  .selectAll('rect')
  .data(data)
  .join('rect')
  .attr('fill', (d) => colorScale(d.value));
```

## Selection Guide

| Data Type           | Recommended Chart                |
| ------------------- | -------------------------------- |
| Time series         | Line or Area                     |
| Category comparison | Bar (horizontal for long labels) |
| Proportions         | Pie/Donut (max 7 slices)         |
| Correlation         | Scatter                          |
| Distribution        | Histogram or Box plot            |
| Geographic          | Heatmap or Choropleth            |
| Hierarchy           | Treemap or Sunburst              |
| Flow                | Sankey diagram                   |
