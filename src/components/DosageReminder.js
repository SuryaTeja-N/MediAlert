import React, { useState, useEffect } from 'react';

const DosageReminder = ({ medication }) => {
    const [reminders, setReminders] = useState(medication.reminders);

    useEffect(() => {
        fetchDosageData();
    }, []);

    const fetchDosageData = async () => {
        try {
            const response = await fetch(`/api/dosage/${medication.id}`);
            const data = await response.json();
            setReminders(data.reminders);
        } catch (error) {
            console.error('Error fetching dosage data:', error);
        }
    };

    useEffect(() => {
        displayReminders();
    }, [reminders]);

    const displayReminders = () => {
        reminders.forEach(reminder => {
            alert(`Reminder: Time to take your ${medication.name} dose.`);
        });
    };

    return (
        <div>
            <h2>Dosage Reminders for {medication.name}</h2>
            <ul>
                {reminders.map((reminder, index) => (
                    <li key={index}>{reminder}</li>
                ))}
            </ul>
        </div>
    );
};

export default DosageReminder;
