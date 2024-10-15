import React from 'react';
import { render, screen } from '@testing-library/react';
import EmailNotification from '../components/EmailNotification';
import '@testing-library/jest-dom/extend-expect';

describe('EmailNotification Component', () => {
    const medication = {
        id: 1,
        name: 'Aspirin',
        missedDoses: ['8:00 AM', '2:00 PM']
    };

    test('renders medication name', () => {
        render(<EmailNotification medication={medication} />);
        const medicationName = screen.getByText(/Email Notifications for Aspirin/i);
        expect(medicationName).toBeInTheDocument();
    });

    test('renders missed doses', () => {
        render(<EmailNotification medication={medication} />);
        const missedDose1 = screen.getByText(/8:00 AM/i);
        const missedDose2 = screen.getByText(/2:00 PM/i);
        expect(missedDose1).toBeInTheDocument();
        expect(missedDose2).toBeInTheDocument();
    });

    test('fetches and displays email data', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve({ email: 'user@example.com' })
            })
        );

        render(<EmailNotification medication={medication} />);
        const email = await screen.findByText(/user@example.com/i);
        expect(email).toBeInTheDocument();
    });

    test('sends email notifications for missed doses', () => {
        render(<EmailNotification medication={medication} />);
        medication.missedDoses.forEach(dose => {
            const notification = screen.getByText(new RegExp(`Sending email notification for missed dose of Aspirin to user@example.com`, 'i'));
            expect(notification).toBeInTheDocument();
        });
    });
});
