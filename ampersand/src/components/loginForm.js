"use client"

import { setCookie, hasCookie, getCookie, } from 'cookies-next/client';
import { refresh } from 'next/cache';

import { redirect, useRouter } from "next/navigation";
import { useEffect, useState } from 'react';

async function login(formdata, setUsername, setPassword, router) {
    if (formdata.username && formdata.password) {
        setUsername(formdata.username)
        setPassword(formdata.password)
        console.log('logging in...')
        console.log("form stuffs ", JSON.stringify({ username: formdata.username, password: formdata.password }))
        const respone = await fetch(`http://localhost:8080/user?username=${formdata.username}&password=${formdata.password}`);
        console.log('frontend login')
        // let resJson = await respone.json()
        let status = await respone.status
        // console.log("resJson", resJson)
        console.log("status", status)
        if (status == 200) {
            setCookie("username", formdata.username, {maxAge: 14400})
            router.refresh()
            redirect("/profile")
        } else {
            let messElement = document.getElementById('message');
            messElement.innerHTML = "Username or Password is incorrect"
        }
    }
}

function getFormData() {
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    return { username, password };
}



export function LoginForm() {

    const [textUser, setTextUser] = useState("");
    const [textPass, setTextPass] = useState("");

    const handleChangeUser = (e) => {
        setTextUser(e.target.value);
    };

    const handleChangePass = (e) => {
        setTextPass(e.target.value);
    };

    const router = useRouter()
    const [loggedUsername, setLoggedUsername] = useState(null)

    useEffect(() => {
        const name = getCookie("username")
        if (name) {
            router.replace("/profile")
            setLoggedUsername(name)
        }
    }, [router])

    if (loggedUsername) return null
    
    return(
        <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
            <main className="flex flex-1 w-full max-w-3xl flex-col items-center py-32 px-16 bg-white dark:bg-black">
                <h3 id="message"></h3>
                <form className="flex flex-col items-center text-center justify-between w-[60%] border-1 outline-gray-600 border-gray-600 rounded-md" action={() => login(getFormData(), setTextUser, setTextPass, router)}>
                    <div className="w-full">
                        <label htmlFor="username" className="mr-[12%]">username</label>
                        <input type="text" name="username" id="username" value={textUser ? textUser : ""} onChange={handleChangeUser} placeholder="username" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[6%]" required/>
                    </div>
                    <div className="w-full">
                        <label htmlFor="password" className="mr-[13%]">password</label>
                        <input type="password" name="password" id="password" value={textPass ? textPass : ""} onChange={handleChangePass} placeholder="password" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[6%]" required/>
                    </div>
                    <div className="w-full">
                        <input type="submit" name="submit" id="submit" value={"login"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                    </div>
                </form>
            </main>
        </div>
    )
}