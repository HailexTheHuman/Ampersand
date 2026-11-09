"use client"

import { redirect } from "next/navigation";

async function signup(formdata) {
    if (formdata.username && formdata.password == formdata.confirm) {
        console.log('signing up...')
        console.log("form stuffs ", JSON.stringify({ username: formdata.username, password:formdata.password }))
        // const respone = await fetch('http://localhost:8080/user', {
        const respone = await fetch('https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: formdata.username, password:formdata.password })
        });
        console.log('frontend signup')
        let resJson = await respone.json()
        let status = await respone.status
        console.log("resJson", resJson)
        console.log("status", status)
        if (resJson.message == "User created successfully") {
            redirect("/login")
        } else if (status == 409) {
            let messElement = document.getElementById('message');
            messElement.innerHTML = "Username already taken"
        }
    }
}

function getFormData() {
    let username = document.getElementById('username').value;
    // let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;
    let confirm = document.getElementById('passconfirm').value;
    return { username, password, confirm };
}

export function SignupForm() {
    
    return(
        <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
            <main className="flex flex-1 w-full max-w-3xl flex-col items-center py-32 px-16 bg-white dark:bg-black">
                <h3 id="message"></h3>
                <form className="flex flex-col items-center text-center justify-between sm:w-[60%] w-[80%] border-1 outline-gray-600 border-gray-600 rounded-md" action={() => signup(getFormData())}>
                    <div className="w-full">
                        <label htmlFor="username" className="sm:mr-[12%]">username</label>
                        <input type="text" name="username" id="username" placeholder="username" className="border-2 outline-purple-700 border-purple-700 rounded-md sm:ml-[6%]" required/>
                    </div>
                    <div className="w-full">
                        <label htmlFor="password" className="sm:mr-[13%]">password</label>
                        <input type="password" name="password" id="password" placeholder="password" className="border-2 outline-purple-700 border-purple-700 rounded-md sm:ml-[6%]" required/>
                    </div>
                    <div className="w-full">
                        <label htmlFor="passconfirm" className="sm:mr-[2%]">confirm password</label>
                        <input type="password" name="passconfirm" id="passconfirm" placeholder="passconfirm" className="border-2 outline-purple-700 border-purple-700 rounded-md sm:ml-[2%]" required/>
                    </div>
                    <div className="w-full">
                        <input type="submit" name="submit" id="submit" value={"signup"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                    </div>
                </form>
            </main>
        </div>
    )
}