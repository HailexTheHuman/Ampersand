"use client"

import { redirect } from "next/navigation";


async function addAlter(formdata, username) {
    if (formdata.name && formdata.description) {
        console.log('creating alter...')
        console.log("form stuff for creating alter: ", JSON.stringify({ username:username,  alter_name:formdata.name, description: formdata.description }))
        const respone = await fetch('http://localhost:8080/alter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username,  alter_name:formdata.name, description: formdata.description })
        });
        console.log('frontend create alter')
        let resJson = await respone.json()
        let status = await respone.status
        console.log("resJson", resJson)
        console.log("status", status)
        if (resJson.message == "Alter created successfully") {
            redirect('/profile')
        }
    }
}

function getAddFormData() {
    let name = document.getElementById('name').value;
    let description = document.getElementById('description').value;
    return { name, description};
}

export function AddAlterForm({ username }) {
    
    return(
        <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black max-w-[40%] ml-[9%] max-h-[90%]">
            {/* <h3 id="message"></h3> */}
            <form className="flex flex-col items-center text-center  min-w-[70%] min-h-[35%] border-1 outline-gray-600 border-gray-600 rounded-md" action={() => addAlter(getAddFormData(), username)}>
                <div className="w-full max-h-[40%] min-h-[20%] mt-[14%]">
                    <label htmlFor="name" className="">name</label>
                    <input type="text" name="name" id="name" placeholder="name" className="border-2 outline-purple-700 border-purple-700 rounded-md" required/>
                </div>
                <div className="w-full max-h-[40%] min-h-[20%] ">
                    <label htmlFor="description" className="">description</label>
                    <input type="text" name="description" id="description" placeholder="description" className="border-2 outline-purple-700 border-purple-700 rounded-md" required/>
                </div>
                <div className="w-full max-h-[40%] min-h-[20%] ">
                    <input type="submit" name="submit" id="submit" value={"Add alter"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
            </form>
        </div>
    )
}

async function editAlter(formdata, username) {
    if (formdata.oldName && (formdata.description || formdata.newName)) {
        console.log('editing alter...')
        console.log("form stuff for editing alter: ", JSON.stringify({ username:username,  oldName:formdata.oldName, newName:formdata.newName, description: formdata.description }))
        const respone = await fetch('http://localhost:8080/alter', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username:username,  old_name:formdata.oldName, new_name:formdata.newName, description: formdata.description })
        });
        console.log('frontend edit alter')
        let resJson = await respone.json()
        let status = await respone.status
        console.log("resJson", resJson)
        console.log("status", status)
        if (resJson.message == "Alter edited successfully") {
            redirect('/profile')
        }
    }
}

function getEditFormData() {
    let oldName = document.getElementById('oldName').value;
    let newName = document.getElementById('newName').value;
    let description = document.getElementById('descriptionEdit').value;
    return { oldName, newName, description};
}

export function EditAlterForm({ username }) {
    
    return(
        <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black max-w-[40%] ml-[2%] max-h-[90%]">
            {/* <h3 id="message"></h3> */}
            <form className="flex flex-col items-center text-center  min-w-[70%] min-h-[35%] border-1 outline-gray-600 border-gray-600 rounded-md" action={() => editAlter(getEditFormData(), username)}>
                <div className="w-full max-h-[30%] min-h-[20%] mt-[14%]">
                    <label htmlFor="oldName" className="">old name</label>
                    <input type="text" name="oldName" id="oldName" placeholder="old name" className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
                <div className="w-full max-h-[30%] min-h-[20%] ">
                    <label htmlFor="newName" className="">new name</label>
                    <input type="text" name="newName" id="newName" placeholder="new name (not required)" className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
                <div className="w-full max-h-[30%] min-h-[20%] ">
                    <label htmlFor="description" className="">description</label>
                    <input type="text" name="descriptionEdit" id="descriptionEdit" placeholder="description (not required)" className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
                <div className="w-full max-h-[30%] min-h-[20%] ">
                    <input type="submit" name="submit" id="submit" value={"Edit alter"} className="border-2 outline-purple-700 border-purple-700 rounded-md"/>
                </div>
            </form>
        </div>
    )
}