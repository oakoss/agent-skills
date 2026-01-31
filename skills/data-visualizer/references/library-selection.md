---
title: Library Selection
description: Comparison and setup examples for Recharts (React), Chart.js (framework-agnostic), and D3.js (custom/advanced) charting libraries
tags: [Recharts, Chart.js, D3, library, React, SVG, canvas, setup, comparison]
---

# Library Selection

## Recharts (Recommended for React)

Declarative React components built on D3. Best for quick, standard chart types in React projects.

```tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const data = [
  { month: 'Jan', revenue: 4000, expenses: 2400 },
  { month: 'Feb', revenue: 3000, expenses: 1398 },
  { month: 'Mar', revenue: 2000, expenses: 9800 },
];

function RevenueChart() {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="month" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
      <Line type="monotone" dataKey="expenses" stroke="#82ca9d" />
    </LineChart>
  );
}
```

## Chart.js (Recommended for Vue/Angular)

Canvas-based, framework-agnostic. Simple API with good defaults.

```ts
import { Chart } from 'chart.js/auto';

const ctx = document.getElementById('myChart');
const chart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Sales',
        data: [12, 19, 3, 5, 2, 3],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
    ],
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Monthly Sales' },
    },
  },
});
```

## D3.js (Advanced/Custom)

Low-level data-driven document manipulation. Full control over rendering. Use when you need custom chart types, complex interactions, or publication-quality graphics.

```ts
import * as d3 from 'd3';

function createBarChart(data: Array<{ name: string; value: number }>) {
  const width = 600;
  const height = 400;
  const margin = { top: 20, right: 20, bottom: 30, left: 40 };

  const svg = d3
    .select('#chart')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  const x = d3
    .scaleBand()
    .domain(data.map((d) => d.name))
    .range([margin.left, width - margin.right])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.value)])
    .range([height - margin.bottom, margin.top]);

  svg
    .selectAll('rect')
    .data(data)
    .join('rect')
    .attr('x', (d) => x(d.name))
    .attr('y', (d) => y(d.value))
    .attr('height', (d) => y(0) - y(d.value))
    .attr('width', x.bandwidth())
    .attr('fill', 'steelblue');

  svg
    .append('g')
    .attr('transform', `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x));

  svg
    .append('g')
    .attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y));
}
```

## Comparison

| Feature           | Recharts         | Chart.js               | D3.js               |
| ----------------- | ---------------- | ---------------------- | ------------------- |
| Rendering         | SVG              | Canvas                 | SVG/Canvas          |
| React integration | Native           | Wrapper                | Manual              |
| Customization     | Moderate         | Moderate               | Full                |
| Learning curve    | Low              | Low                    | High                |
| Bundle size (gz)  | ~139KB           | ~68KB (tree-shakeable) | ~13-30KB per module |
| Best for          | React dashboards | Multi-framework        | Custom viz          |
