import React from 'react';
import { render, screen } from '@testing-library/react';
import DosageReminder from '../components/DosageReminder';
import '@testing-library/jest-dom/extend-expect';

describe('DosageReminder Component', () => {
    const medication = {
        id: 1,
        name: 'Aspirin',
        reminders: ['8:00 AM', '2:00 PM', '8:00 PM']
    };

    test('renders medication name', () => {
        render(<DosageReminder medication={medication} />);
        const medicationName = screen.getByText(/Dosage Reminders for Aspirin/i);
        expect(medicationName).toBeInTheDocument();
    });

    test('renders reminders', () => {
        render(<DosageReminder medication={medication} />);
        const reminder1 = screen.getByText(/8:00 AM/i);
        const reminder2 = screen.getByText(/2:00 PM/i);
        const reminder3 = screen.getByText(/8:00 PM/i);
        expect(reminder1).toBeInTheDocument();
        expect(reminder2).toBeInTheDocument();
        expect(reminder3).toBeInTheDocument();
    });

    test('fetches and displays dosage data', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve({ reminders: ['8:00 AM', '2:00 PM', '8:00 PM'] })
            })
        );

        render(<DosageReminder medication={medication} />);
        const reminder1 = await screen.findByText(/8:00 AM/i);
        const reminder2 = await screen.findByText(/2:00 PM/i);
        const reminder3 = await screen.findByText(/8:00 PM/i);
        expect(reminder1).toBeInTheDocument();
        expect(reminder2).toBeInTheDocument();
        expect(reminder3).toBeInTheDocument();
    });
});
