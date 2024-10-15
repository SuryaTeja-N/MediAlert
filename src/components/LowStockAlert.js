import React, { useState, useEffect } from 'react';

const LowStockAlert = ({ medication }) => {
    const [stockLevel, setStockLevel] = useState(medication.stock);

    useEffect(() => {
        fetchStockData();
    }, []);

    const fetchStockData = async () => {
        try {
            const response = await fetch(`/api/stock/${medication.id}`);
            const data = await response.json();
            setStockLevel(data.stock);
        } catch (error) {
            console.error('Error fetching stock data:', error);
        }
    };

    useEffect(() => {
        checkStockLevel();
    }, [stockLevel]);

    const checkStockLevel = () => {
        if (stockLevel < 5) {
            alert(`Low stock alert for ${medication.name}! Only ${stockLevel} left.`);
        }
    };

    return (
        <div>
            <h2>{medication.name}</h2>
            <p>Stock Level: {stockLevel}</p>
        </div>
    );
};

export default LowStockAlert;
