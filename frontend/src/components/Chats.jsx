import React from 'react'
import { useState } from "react";
import Chat from "./Chat";

const Chats = () => {

	const [chats, setChats] = useState([]);
	const [tempQuery, setTempQuery] = useState('');
	const [isLoading, setIsLoading] = useState(false)

	const handleSubmit = async (e) => {
		e.preventDefault();
		const userMessage = tempQuery.trim();
		if (!userMessage) {
			return
		}

		setTempQuery('');
		setChats((prevChats) => [
			...prevChats, 
			{	content: userMessage, sender:"human"}
		])
		setTempQuery('');
		setIsLoading(true);
		
		setChats((prevChats) => [
			...prevChats,
			{ content: "", sender:"bot", loading: true}
		])

		try {
			const response = await fetch('http://127.0.0.1:5000/api/chat', {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
			},
				body: JSON.stringify({ input: userMessage }),
			});
			const data = await response.json();
			
			setChats((prevChats) =>
				prevChats.map((chat, index) =>
					index === prevChats.length - 1
						? { content: data.response, cypher: data.cypher, data: data.data, sender: "bot", loading: false }
						: chat
				)
			);
		
		} catch (error) {
			setChats((prevChats) =>
				prevChats.map((chat, index) =>
					index === prevChats.length - 1
						? { content: "Error fetching response", sender: "bot", loading: false }
						: chat
				)
			);
		} finally {
			setIsLoading(false);
		}
	}

	return (
		<div className="flex justify-center items-center flex-col w-full">
			<div className='overflow-y-scroll overflow-x-hidden flex items-center flex-col w-full mb-[5%] scrollbar scrollbar-track-slate-800 scrollbar-thumb-slate-600'>
			<div className={`${!chats.length ? `h-[0%]` : `max-h-[68vh]`} -x-hidden w-[70%]`}>
			 {chats.map((chat, index) => (
				<Chat key={index} content={chat.content} sender={chat.sender} loading={chat.loading} cypher={chat.cypher} data={chat.data}/>
			 ))}
			</div>
			</div>
			<div className={`h-[10%] w-full absolute ${(chats.length === 0) ? `m-auto` : `bottom-[5%]`}`}>
			 <form onSubmit={handleSubmit} className={`w-[100%] flex items-center justify-center`}>
					<div className="flex items-center justify-center w-[60%]">
						<div className="flex justify-center items-center p-2 bg-slate-600 w-[100%] rounded-2xl">
							<input className="w-[85%] rounded-full p-1 pl-4 bg-slate-100" placeholder='Enter query here' value={tempQuery} onChange={(e) => setTempQuery(e.target.value)}>
							</input>
							<button className="bg-green-400 ml-[2.5%] p-1 px-4 rounded-3xl text-center text-slate-800"type="submit">Send</button>
						</div>
					</div>
				
				</form>
			</div>
		</div>
	)
}

export default Chats