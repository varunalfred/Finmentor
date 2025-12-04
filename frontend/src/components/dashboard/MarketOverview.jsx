import React, { useState, useMemo } from 'react';
import { useLiveIndices } from '../../hooks/useLiveIndices';
import StockChart from '../common/StockChart';
import './MarketOverview.css';

const MarketOverview = () => {
    const { data: marketData, isLoading } = useLiveIndices();
    const [selectedIndex, setSelectedIndex] = useState('^NSEI'); // Default to NIFTY 50

    // Flatten all indices into one list for easy access
    const allIndices = useMemo(() => {
        if (!marketData) return [];
        return [
            ...(marketData.indian_markets || []),
            ...(marketData.global_markets || []),
            ...(marketData.commodities || [])
        ];
    }, [marketData]);

    const selectedData = useMemo(() => {
        return allIndices.find(idx => idx.symbol === selectedIndex);
    }, [allIndices, selectedIndex]);

    // Determine chart color based on change
    const chartColor = (selectedData?.change || 0) >= 0 ? '#10b981' : '#ef4444';

    if (isLoading) {
        return <div className="market-overview-loading">Loading Market Overview...</div>;
    }

    return (
        <div className="market-overview-card">
            <div className="overview-header">
                <h3 className="overview-title">Market Overview</h3>
                <div className="index-selector">
                    <select
                        value={selectedIndex}
                        onChange={(e) => setSelectedIndex(e.target.value)}
                        className="index-dropdown"
                    >
                        <optgroup label="Indian Markets">
                            {marketData?.indian_markets?.map(idx => (
                                <option key={idx.symbol} value={idx.symbol}>{idx.name}</option>
                            ))}
                        </optgroup>
                        <optgroup label="Global Markets">
                            {marketData?.global_markets?.map(idx => (
                                <option key={idx.symbol} value={idx.symbol}>{idx.name}</option>
                            ))}
                        </optgroup>
                        <optgroup label="Commodities">
                            {marketData?.commodities?.map(idx => (
                                <option key={idx.symbol} value={idx.symbol}>{idx.name}</option>
                            ))}
                        </optgroup>
                    </select>
                </div>
            </div>

            <div className="overview-content">
                <div className="current-stats">
                    <div className="stat-price">
                        ₹{selectedData?.current_price?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </div>
                    <div className={`stat-change ${selectedData?.change >= 0 ? 'positive' : 'negative'}`}>
                        {selectedData?.change >= 0 ? '+' : ''}{selectedData?.change?.toFixed(2)} ({selectedData?.change_percent?.toFixed(2)}%)
                    </div>
                </div>

                <div className="chart-wrapper">
                    <StockChart
                        data={selectedData?.history || []}
                        color={chartColor}
                        height={250}
                    />
                </div>
            </div>
        </div>
    );
};

export default MarketOverview;
