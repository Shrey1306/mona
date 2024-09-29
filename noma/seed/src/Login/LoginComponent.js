import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import text from '../art_assets/seed_logo_with_text.png'
import leaves from '../art_assets/leaves.png';

function Login() {
    const [isRegistering, setIsRegistering] = useState(false);
    const navigate = useNavigate();
    const handleSubmit = (e) => {
        e.preventDefault();
        if (isRegistering) {
            navigate('/dashboard')
        } else {
            navigate('/dashboard');
        }
    };

    const toggleRegister = () => {
        setIsRegistering(!isRegistering);
    };

    return (
        <div className='font-vango w-full h-full'>
            <div className="w-full bg-[#f4e9e1] rounded-2xl dark:border dark:white dark:white justify-center relative overflow-hidden h-full">
                        <img
                            src={leaves}
                            alt="Leaves"
                            className="absolute h-full top-0 w-full"
                            style={{
                                transform: "scale(1.1)", // Zoom out by 20%
                                opacity: 0.5 // Reduce opacity to 50%
                            }}
                        />
                    <div className="p-0 justify-center items-center flex flex-col w-full">
                            <img
                                className="h-auto w-1/3 flex pt-10 pb-5" // Added margin-bottom for spacing
                                src={text}
                                alt="Log In"
                            />
                    <form className="space-y-4 md:space-y-6 w-1/2 pb-5 flex flex-col" onSubmit={handleSubmit}>
                        {/* Email field */}
                        <div className="relative rounded-md shadow-sm">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                {/* SVG for Email */}
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">
                                <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/>
                                </svg>
                            </div>
                            <input type="email" name="email" id="email" placeholder="johndoe@emory.org" required 
                                className="pl-10 pr-4 bg-white text-black text-lg rounded-md focus:ring-black/[0.5] block w-full p-2 dark:bg-white dark:placeholder-gray-400 dark:text-black dark:focus:ring-black/[0.5] dark:focus:border-black focus:outline-none focus:ring-1" />
                        </div>

                        {/* Password field */}
                        <div className="relative rounded-md shadow-sm">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                {/* SVG for Password */}
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-key-fill" viewBox="0 0 16 16">
                                    <path d="M3.5 11.5a3.5 3.5 0 1 1 3.163-5H14L15.5 8 14 9.5l-1-1-1 1-1-1-1 1-1-1-1 1H6.663a3.5 3.5 0 0 1-3.163 2M2.5 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/>
                                    </svg>
                            </div>
                            <input type="password" name="password" id="password" placeholder="Password" required 
                                className="pl-10 pr-4 bg-white text-black text-lg rounded-md focus:ring-black/[0.5] block w-full p-2 dark:bg-white dark:placeholder-gray-400 dark:text-black dark:focus:ring-black/[0.5] dark:focus:border-black focus:outline-none focus:ring-1" />
                                </div>

                        {/* Conditional second password field for registration */}
                        {isRegistering && (
                            <div className="relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    {/* Duplicate of SVG for Password Confirmation */}
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-key-fill" viewBox="0 0 16 16">
                                    <path d="M3.5 11.5a3.5 3.5 0 1 1 3.163-5H14L15.5 8 14 9.5l-1-1-1 1-1-1-1 1-1-1-1 1H6.663a3.5 3.5 0 0 1-3.163 2M2.5 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/>
                                    </svg>
                                </div>
                                <input type="password" name="confirmPassword" id="confirmPassword" placeholder="Confirm Password" required 
                                   className="pl-10 pr-4 bg-white text-black text-lg rounded-md focus:ring-black/[0.5] block w-full p-2 dark:bg-white dark:placeholder-gray-400 dark:text-black dark:focus:ring-black/[0.5] dark:focus:border-black focus:outline-none focus:ring-1" />
                                   </div>
                        )}

                        <div className="flex:grow flex flex-row items-center h-full justify-center pt-8">
                            <button type="submit" className="text-white text-lg w-fit py-3 px-16 rounded-full bg-[#050505] hover:bg-[#1C281E]/[0.5]">
                                {isRegistering ? 'Register' : 'Log in'}
                            </button>
                        </div>

                        {!isRegistering && (
                            <div className="flex:grow flex flex-row items-center h-full justify-center">
                                <button type="button" onClick={toggleRegister} className="text-white text-lg w-fit py-3 px-16 rounded-full bg-[#050505] hover:bg-[#1C281E]/[0.8] shadow-lg">
                                    Register
                                </button>
                            </div>
                        )}

                        {isRegistering && (
                            <div className="flex:grow flex flex-row items-center h-full justify-center">
                                <button type="button" onClick={toggleRegister} className="text-white text-lg w-fit py-3 px-16 rounded-full bg-[#1C281E] hover:bg-[#1C281E]/[0.8]">
                                    Back to Login
                                </button>
                            </div>
                        )}
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Login;