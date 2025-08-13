import React from 'react';
import neologo from "../assets/neo4j.png";
import exitlogo from "../assets/exit.png";
import { useState } from "react";


const Chat = ({ content, sender, className, loading, cypher, data }) => {

	if (data === 0) {
		data = "No Retrieved Data"
	}
	const [showCypher, setShowCypher ] = useState(false)

	if (sender == "human") {
		return (
		<div className={`flex justify-end w-full mt-[3%] ${className}`}>
			<div className="w-[50%] flex justify-end">
			<div className="flex items-end w-[80%] bg-blue-600 p-4 rounded-full">
			<span className="text-white font-sans ml-[5%]">{content}</span>
			 </div>
			 </div>
			</div>
		)
	}
	if (sender == "bot") {
		return loading ? (
			<div className={`flex justify-start w-full mt-[3%] ${className}`}>
			<div className="w-[75%] flex justify-start">
				<div className="flex items-end w-[105%] bg-gray-600 p-6 rounded-xl">
					<span className="text-white font-sans animate-pulse">Loading...</span>
				 </div>
			 </div>
		</div>

			) : (!showCypher ? (
			<div className={`flex justify-start w-full mt-[3%] ${className}`}>
				<div className="w-[60%] flex justify-start">
					<div className="flex items-end w-[105%] h-full bg-gray-600 rounded-xl flex-col p-0.5 pb-4 pl-4">
						<button className="flex justify-end "><img src={neologo} className='w-[12%] bg-green-400 rounded-3xl' onClick={() => setShowCypher((showCypher) => !showCypher)}/></button>
						<span className="text-white font-sans mt-[-0.25%]">{content}</span>
			 		</div>
			 	</div>
			</div>
		)
		: (
		<div className={`flex justify-start w-full mt-[3%] ${className}`}>
		<div className="w-[60%] flex justify-start">
			<div className="flex items-end w-[105%] h-full bg-gray-600 rounded-xl flex-col p-0.5 pb-4 pl-4">
				<button className="flex justify-end"><img src={exitlogo} className='w-[4%] rounded-3xl' onClick={() => setShowCypher((showCypher) => !showCypher)}/></button>
				<span className='w-full text-gray-50 mb-[1%]'>Cypher Query Generated:</span>
				<pre className="text-gray-50 w-[95%]">{cypher}</pre>
				<span className='w-full mt-[2%] text-gray-50 mb-[1%]'>Data Rendered:</span>
				<span className='w-[95%] text-gray-50'>{data}</span>
			 </div>
		 </div>
		</div>

	)
			)
	}
}

export default Chat