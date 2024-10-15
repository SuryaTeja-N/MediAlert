import React, { useState, useEffect } from 'react';

const StockAlert = ({ medication }) => {
    const [stockLevel, setStockLevel] = useState(medication.stock);

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

export default StockAlert;
