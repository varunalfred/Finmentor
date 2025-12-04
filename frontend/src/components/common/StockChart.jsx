import React from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import './StockChart.css';

const StockChart = ({ data, color = '#10b981', height = 300 }) => {
    if (!data || data.length === 0) {
        return (
            <div className="stock-chart-empty" style={{ height }}>
                <p>No chart data available</p>
            </div>
        );
    }

    // Calculate min/max for Y-axis domain to make chart look dynamic
    const prices = data.map(d => d.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const padding = (maxPrice - minPrice) * 0.1;

    return (
        <div className="stock-chart-container" style={{ height }}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333" opacity={0.3} />
                    <XAxis
                        dataKey="date"
                        hide={true}
                    />
                    <YAxis
                        domain={[minPrice - padding, maxPrice + padding]}
                        hide={true}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(20, 20, 30, 0.9)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '8px',
                            color: '#fff'
                        }}
                        itemStyle={{ color: '#fff' }}
                        formatter={(value) => [`₹${value.toFixed(2)}`, 'Price']}
                        labelStyle={{ color: '#aaa', marginBottom: '5px' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="price"
                        stroke={color}
                        fillOpacity={1}
                        fill="url(#colorPrice)"
                        strokeWidth={2}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default StockChart;
