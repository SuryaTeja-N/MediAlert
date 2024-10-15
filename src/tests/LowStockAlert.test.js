import React from 'react';
import { render, screen } from '@testing-library/react';
import LowStockAlert from '../components/LowStockAlert';
import '@testing-library/jest-dom/extend-expect';

describe('LowStockAlert Component', () => {
    const medication = {
        id: 1,
        name: 'Aspirin',
        stock: 3
    };

    test('renders medication name', () => {
        render(<LowStockAlert medication={medication} />);
        const medicationName = screen.getByText(/Aspirin/i);
        expect(medicationName).toBeInTheDocument();
    });

    test('renders stock level', () => {
        render(<LowStockAlert medication={medication} />);
        const stockLevel = screen.getByText(/Stock Level: 3/i);
        expect(stockLevel).toBeInTheDocument();
    });

    test('displays low stock alert', () => {
        render(<LowStockAlert medication={medication} />);
        const alertMessage = screen.getByText(/Low stock alert for Aspirin! Only 3 left./i);
        expect(alertMessage).toBeInTheDocument();
    });
});
