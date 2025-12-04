import React from 'react';
import './SkeletonLoader.css';

const SkeletonLoader = ({ type = 'card', count = 1 }) => {
    const renderSkeleton = () => {
        switch (type) {
            case 'market-card':
                return (
                    <div className="skeleton-market-card">
                        <div className="skeleton-line skeleton-title"></div>
                        <div className="skeleton-line skeleton-value"></div>
                        <div className="skeleton-line skeleton-change"></div>
                    </div>
                );

            case 'stock-card':
                return (
                    <div className="skeleton-stock-card">
                        <div className="skeleton-circle"></div>
                        <div className="skeleton-content">
                            <div className="skeleton-line skeleton-name"></div>
                            <div className="skeleton-line skeleton-price"></div>
                        </div>
                    </div>
                );

            case 'message':
                return (
                    <div className="skeleton-message">
                        <div className="skeleton-line"></div>
                        <div className="skeleton-line" style={{ width: '80%' }}></div>
                        <div className="skeleton-line" style={{ width: '60%' }}></div>
                    </div>
                );

            case 'card':
            default:
                return (
                    <div className="skeleton-card">
                        <div className="skeleton-line"></div>
                        <div className="skeleton-line" style={{ width: '90%' }}></div>
                        <div className="skeleton-line" style={{ width: '70%' }}></div>
                    </div>
                );
        }
    };

    return (
        <div className="skeleton-container">
            {Array.from({ length: count }).map((_, index) => (
                <div key={index} className="skeleton-item">
                    {renderSkeleton()}
                </div>
            ))}
        </div>
    );
};

export default SkeletonLoader;
