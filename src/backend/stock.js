const express = require('express');
const router = express.Router();
const db = require('../config/db');

// Fetch stock data for a specific medication
router.get('/stock/:medicationId', async (req, res) => {
    try {
        const medicationId = req.params.medicationId;
        const stockData = await db.query('SELECT stock FROM medications WHERE id = ?', [medicationId]);
        res.json(stockData[0]);
    } catch (error) {
        console.error('Error fetching stock data:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Update stock data for a specific medication
router.put('/stock/:medicationId', async (req, res) => {
    try {
        const medicationId = req.params.medicationId;
        const { stock } = req.body;
        await db.query('UPDATE medications SET stock = ? WHERE id = ?', [stock, medicationId]);
        res.json({ message: 'Stock updated successfully' });
    } catch (error) {
        console.error('Error updating stock data:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
