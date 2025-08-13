import React, { useState } from 'react';
import Chat from './Chat';

const Input = ({ setChats }) => {
    const [query, setQuery] = useState('');
    const [tempQuery, setTempQuery] = useState('');

    const addChat = (chat) => {
        setChats((prevChats) => [...prevChats, chat]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Use tempQuery directly for adding human chat
        addChat({ content: tempQuery, sender: 'Human' });
        setQuery(tempQuery); // Now set query to tempQuery after the chat is added

        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: tempQuery }),
            });
            const data = await response.json();
            addChat({ content: data, sender: 'Bot' });
        } catch (error) {
            // Handle error properly by accessing error.message
            addChat({ content: `Error: ${error.message}`, sender: 'Bot', type: 'Error' });
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                placeholder='Enter query here'
                value={tempQuery} // Make input a controlled component
                onChange={(e) => setTempQuery(e.target.value)}
                className="border rounded-md p-2"
            />
            <button className="bg-white ml-2 p-0.5 rounded-lg text-center" type="submit">
                Send
            </button>
        </form>
    );
};

export default Input;
